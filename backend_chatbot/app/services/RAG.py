from dotenv import load_dotenv
import os
from groq import Groq
from typing import Optional, List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain.docstore.document import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm.notebook import tqdm
import pandas as pd

load_dotenv()

client = Groq()

# Đọc dữ liệu từ CSV
df = pd.read_csv('app\services\CV.csv')

# Tạo RAW_BASE
RAW_KNOWLEDGE_BASE = [
    LangchainDocument(
        page_content=f"Resume: {row['Resume']}",
        metadata={"source": row['source']}
    )
    for _, row in tqdm(df.iterrows(), total=len(df))
]

# Chunking và chuẩn bị dữ liệu
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

    # Loại bỏ bản sao
    unique_texts = {}
    docs_processed_unique = []
    for doc in docs_processed:
        if doc.page_content not in unique_texts:
            unique_texts[doc.page_content] = True
            docs_processed_unique.append(doc)

    return docs_processed_unique

# Tạo vector database
embedding_model = HuggingFaceEmbeddings(
    model_name="thenlper/gte-small",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

docs_processed = split_documents(512, RAW_KNOWLEDGE_BASE)
KNOWLEDGE_VECTOR_DATABASE = FAISS.from_documents(docs_processed, embedding_model, distance_strategy="cosine")

# Mẫu prompt ChatGPT
prompt_in_chat_format = [
    {
        "role": "user",
        "content": """Using the information contained in the context,
give a comprehensive answer to the question.
Respond only to the question asked, response should be concise and relevant to the question.
The answer must include 2 parts: part 1 - your answer, part 2 - list of related CV provided to you (just names).
If the answer cannot be deduced from the context, do not give an answer."""
 """Context:
{context}
---
Now here is the question you need to answer.

Question: {question}"""
    },
]

# Hàm trả lời sử dụng OpenAI API
def answer_with_gorq_api(question: str, knowledge_index: FAISS, num_retrieved_docs: int = 5) -> Tuple[str, List[LangchainDocument]]:
    relevant_docs = knowledge_index.similarity_search(query=question, k=num_retrieved_docs)
    relevant_content = [doc.page_content for doc in relevant_docs]
    relevant_metadatas = [doc.metadata for doc in relevant_docs]

    context = "\nExtracted documents:\n"
    context += "".join([f"Document {relevant_metadatas[i]}:::\n" + doc for i, doc in enumerate(relevant_content)])

    final_prompt = prompt_in_chat_format[0]["content"].format(question=question, context=context)

    # Gửi prompt tới OpenAI API
    response = client.chat.completions.create( 
        messages=[

            {
                "role": "user",
                "content": final_prompt
            }
        ],
        model="llama3-8b-8192",
        stream=False,
    )
    # Lấy câu trả lời từ OpenAI API
    answer = response.choices[0].message.content
    return answer, relevant_metadatas

# Testing
question = "find the CV containing: Programming Languages: Python (pandas, numpy, scipy, scikit-learn, matplotlib), Sql, Java, JavaScript/JQuery. * Machine learning: Regression, SVM, NaÃ¯ve Bayes, KNN, Random Forest, Decision Trees, Boosting techniques, Cluster Analysis, Word Embedding, Sentiment Analysis"

answer, metadatas = answer_with_gorq_api(question=question, knowledge_index=KNOWLEDGE_VECTOR_DATABASE)

print(answer)
print(metadatas)
