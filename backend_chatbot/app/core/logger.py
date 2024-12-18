import logging
import os

# Tạo thư mục logs nếu chưa tồn tại
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Cấu hình logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)  # Đặt mức độ log là DEBUG để ghi lại tất cả các thông báo

# Định dạng log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler: hiển thị log trên console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Hiển thị các thông báo mức INFO và cao hơn trên console
console_handler.setFormatter(formatter)

# File handler: ghi log vào file
log_file = os.path.join(log_dir, "app.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)  # Ghi tất cả thông báo vào file (DEBUG và cao hơn)
file_handler.setFormatter(formatter)

# Thêm các handler vào logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Kiểm tra logger
logger.debug("Logger đã được cấu hình thành công!")
