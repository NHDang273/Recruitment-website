import os
import csv
from pdfminer.high_level import extract_text
from docx import Document
import logging
from pathlib import Path
import pandas as pd
import pdfplumber
import time



def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Error: File not found - {pdf_path}")
        time.sleep(0.1)  # Đợi một chút để đảm bảo file được tạo xong
        return extract_text(pdf_path)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_doc(doc_path):
    """Extract text from DOC/DOCX file."""
    try:
        document = Document(doc_path)
        return "\n".join([paragraph.text for paragraph in document.paragraphs])
    except Exception as e:
        print(f"Error extracting text from DOC/DOCX: {e}")
        return ""

def save_text_to_csv(text, csv_path, source_pdf):
    """Save extracted text to a CSV file."""
    try:
        cleaned_text = text.replace("\n", " ").replace("\r", " ")
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["source", "Resume"])  
            writer.writerow([source_pdf, cleaned_text])  # Dữ liệu
        print(f"CSV file saved at: {csv_path}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def convert_to_csv(file_path, output_csv_path):
    """Convert file (PDF/DOC/DOCX) to CSV."""
    file_extension = os.path.splitext(file_path)[-1].lower()
    if file_extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension in [".doc", ".docx"]:
        text = extract_text_from_doc(file_path)
    else:
        print("Unsupported file format. Only PDF and DOC/DOCX are supported.")
        return
    
    if text:
        last_folder = os.path.basename(os.path.normpath(file_path))
        save_text_to_csv(text, output_csv_path, last_folder)

# def process_file(input_file, output_csv):
#     """Process file and convert it to CSV."""
#     if os.path.exists(input_file):
#         convert_to_csv(input_file, output_csv)
#     else:
#         print(f"Error: File not found - {input_file}")

def process_file(input_file, output_folder):
    """Process file and convert it to CSV."""
    if os.path.exists(input_file):
        # Đảm bảo thư mục đầu ra tồn tại
        os.makedirs(output_folder, exist_ok=True)

        # Tạo đường dẫn đầy đủ cho tệp CSV trong thư mục đích
        input_path = Path(input_file)
        output_csv = Path(output_folder) / input_path.with_suffix('.csv').name

        # Gọi hàm convert_to_csv với đường dẫn chính xác
        convert_to_csv(input_file, str(output_csv))
        print(f"File processed and saved to: {output_csv}")
    else:
        print(f"Error: File not found - {input_file}")

# Usage
# # Đường dẫn tệp đầu vào
# input_file = r'E:\WORKSPACE\RecruitmentWebsite-RAG\Backend-RAG-Chatbot\uploaded_files\HaiDang_CV.pdf'

# # Thư mục lưu trữ tệp CSV
# output_folder = r'E:\WORKSPACE\RecruitmentWebsite-RAG\Backend-RAG-Chatbot\csv_files'

# # Gọi hàm
# process_file(input_file, output_folder)
