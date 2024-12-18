from fastapi import FastAPI
from app.routers import chat, health, documents
from app.database.connection import connect_to_mongo, close_mongo_connection
import logging
import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.services.pdf_processing import *
import threading

# Cấu hình logging cho ứng dụng
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app_logger")

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Đăng ký các router
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])  # Chat có hỗ trợ WebSocket
app.include_router(documents.router, prefix="/api", tags=["Documents"])

# Đường dẫn thư mục cần theo dõi
uploaded_folder = Path('uploaded_files')
csv_folder = Path('csv_files')

# Kiểm tra và tạo thư mục nếu không tồn tại
uploaded_folder.mkdir(parents=True, exist_ok=True)
csv_folder.mkdir(parents=True, exist_ok=True)

# Class để theo dõi thay đổi trong thư mục
class Watcher(FileSystemEventHandler):
    def on_modified(self, event):
        # Nếu là thư mục và có thay đổi, kiểm tra các file PDF mới
        if event.is_directory and event.src_path == str(uploaded_folder):
            for file in os.listdir(uploaded_folder):
                file_path = uploaded_folder / file
                if file_path.suffix.lower() == '.pdf':
                    process_file(file_path, csv_folder)

    def on_created(self, event):
        # Nếu là file mới được tạo, kiểm tra nếu đó là file PDF
        if not event.is_directory and event.src_path.endswith('.pdf'):
            pdf_path = Path(event.src_path)
            process_file(pdf_path, csv_folder)

# Khởi tạo observer và thêm watcher
def start_watching():
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, path=str(uploaded_folder), recursive=False)
    observer.start()
    logger.info("Watching for changes in 'uploaded_files'...")
    try:
        while True:
            time.sleep(1)  # Duy trì tiến trình theo dõi
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Chạy Watcher trong luồng riêng
def run_watcher_in_thread():
    watcher_thread = threading.Thread(target=start_watching, daemon=True)
    watcher_thread.start()
    logger.info("Started file watcher thread.")

# Kết nối MongoDB và khởi động watcher khi server FastAPI khởi động
@app.on_event("startup")
async def startup_event():
    try:
        await connect_to_mongo()
        logger.info("MongoDB kết nối thành công")
    except Exception as e:
        logger.error(f"Không thể kết nối MongoDB: {e}")
        raise e

    # Bắt đầu theo dõi thư mục trong luồng riêng
    run_watcher_in_thread()

# Đóng kết nối MongoDB khi server tắt
@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    logger.info("Kết nối MongoDB đã được đóng.")
