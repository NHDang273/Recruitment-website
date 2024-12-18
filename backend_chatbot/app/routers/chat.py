import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from groq import Groq
import glob
from typing import Optional, List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain.docstore.document import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import pandas as pd
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize router and Groq client
router = APIRouter()
client = Groq()

# CSV folder setup
csv_folder = Path('csv_files')

# Function to read and combine CSV files
def load_csv_files():
    csv_files = glob.glob(str(csv_folder / "*.csv"))
    if not csv_files:
        print("No CSV files found.")
        return None

    dataframes = []
    for file in csv_files:
        print(f"Reading {file}...")
        df = pd.read_csv(file)
        dataframes.append(df)

    # Combine all DataFrames if needed
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Create RAW_KNOWLEDGE_BASE
    raw_knowledge_base = [
        LangchainDocument(
            page_content=f"Resume: {row['Resume']}",
            metadata={"source": row['source']}
        )
        for _, row in tqdm(combined_df.iterrows(), total=len(combined_df))
    ]
    return raw_knowledge_base

# Initialize the knowledge base
RAW_KNOWLEDGE_BASE = load_csv_files() or []

# Function to split documents into chunks
def split_documents(chunk_size: int, knowledge_base: List[LangchainDocument]) -> List[LangchainDocument]:
    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        AutoTokenizer.from_pretrained("thenlper/gte-small"),
        chunk_size=chunk_size,
        chunk_overlap=int(chunk_size / 10),
        add_start_index=False,
        strip_whitespace=True,
        separators=[". ", ", "]
    )

    docs_processed = []
    for doc in knowledge_base:
        docs_processed += text_splitter.split_documents([doc])

    # Remove duplicates
    unique_texts = {}
    docs_processed_unique = []
    for doc in docs_processed:
        if doc.page_content not in unique_texts:
            unique_texts[doc.page_content] = True
            docs_processed_unique.append(doc)

    return docs_processed_unique

# Create vector database
embedding_model = HuggingFaceEmbeddings(
    model_name="thenlper/gte-small",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

docs_processed = split_documents(512, RAW_KNOWLEDGE_BASE)
KNOWLEDGE_VECTOR_DATABASE = FAISS.from_documents(docs_processed, embedding_model, distance_strategy="cosine")

# Define prompt format for ChatGPT
prompt_in_chat_format = [
    {
        "role": "user",
        "content": """Using the information contained in the context,\n        give a comprehensive answer to the question.\n        Respond only to the question asked; the response should be concise and relevant to the question.\n        The answer must include two parts: \n        part 1 - your answer, \n        part 2 - list of related CVs provided to you (just names).\n        If the answer cannot be deduced from the context, do not give an answer.\n        \n        Context:\n        {context}\n        ---\n        Now here is the question you need to answer:\n        \n        Question: {question}"""
    }
]

# Function to answer questions using Groq API
def answer_with_groq_api(question: str, knowledge_index: FAISS, num_retrieved_docs: int = 5) -> Tuple[str, List[dict]]:
    relevant_docs = knowledge_index.similarity_search(query=question, k=num_retrieved_docs)
    relevant_content = [doc.page_content for doc in relevant_docs]
    relevant_metadatas = [doc.metadata for doc in relevant_docs]

    context = "\nExtracted documents:\n"
    context += "\n".join([f"Document {i + 1} ({doc_metadata['source']}):\n{doc_content}" for i, (doc_content, doc_metadata) in enumerate(zip(relevant_content, relevant_metadatas))])

    final_prompt = prompt_in_chat_format[0]["content"].format(question=question, context=context)

    # Send prompt to Groq API
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": final_prompt}],
        model="llama3-8b-8192",
        stream=False,
    )

    # Extract answer from API response
    answer = response.choices[0].message.content
    return answer, relevant_metadatas

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_binary(self, data: bytes, websocket: WebSocket):
        await websocket.send_bytes(data)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Function to get PDF path from metadata
def get_pdf_path_from_metadata(metadata):
    """Retrieve PDF file path from metadata."""
    pdf_filename = metadata.get('source')
    if pdf_filename:
        return Path("uploaded_files") / pdf_filename
    return None

# Function to send PDF file
async def send_pdf_file(websocket: WebSocket, pdf_path: Path):
    try:
        with open(pdf_path, "rb") as pdf_file:
            await manager.send_binary(pdf_file.read(), websocket)
    except Exception as e:
        await manager.send_message(f"Error sending PDF: {str(e)}", websocket)

# WebSocket endpoint for chatbot
@router.websocket("/chat/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            if not RAW_KNOWLEDGE_BASE:
                await manager.send_message("No data available", websocket)
                continue

            try:
                # Generate response
                response, metadata = answer_with_groq_api(data, KNOWLEDGE_VECTOR_DATABASE)
                print(response)
                print(metadata)
                await manager.send_message(response, websocket)

                # Send related PDF files
                # for meta in metadata:
                #     pdf_path = get_pdf_path_from_metadata(meta)
                #     if pdf_path and pdf_path.exists():
                #         await send_pdf_file(websocket, pdf_path)
                #     else:
                #         await manager.send_message(f"PDF not found: {meta.get('source')}", websocket)

            except Exception as e:
                await manager.send_message(f"Error: {str(e)}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Watchdog handler for CSV directory
class CSVWatchdogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".csv"):
            print("CSV file updated, reloading data...")
            global RAW_KNOWLEDGE_BASE
            RAW_KNOWLEDGE_BASE = load_csv_files() or []
            docs_processed = split_documents(512, RAW_KNOWLEDGE_BASE)
            global KNOWLEDGE_VECTOR_DATABASE
            KNOWLEDGE_VECTOR_DATABASE = FAISS.from_documents(docs_processed, embedding_model, distance_strategy="cosine")

# Watchdog observer for CSV changes
def start_watchdog():
    observer = Observer()
    observer.schedule(CSVWatchdogHandler(), path=str(csv_folder), recursive=False)
    observer.start()

# Run watchdog in a separate thread
watchdog_thread = threading.Thread(target=start_watchdog, daemon=True)
watchdog_thread.start()
