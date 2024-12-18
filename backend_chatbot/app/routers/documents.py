from fastapi import APIRouter, File, UploadFile
import shutil
import os

router = APIRouter()


@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    upload_folder = "./uploaded_files"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Tạo thư mục nếu chưa tồn tại
    
    file_location = f"{upload_folder}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "file_location": file_location}