# from pydantic import BaseSettings, Field
# from dotenv import load_dotenv
# from pydantic import Field
# from pydantic_settings import BaseSettings


# # Tải biến môi trường từ file .env
# load_dotenv()

# class Settings(BaseSettings):
#     MODEL_PATH: str = Field(..., env="MODEL_PATH", description="Đường dẫn đến mô hình Llama")
#     N_THREADS: int = Field(8, env="N_THREADS", ge=1, description="Số luồng xử lý cho mô hình")
#     N_CTX: int = Field(2048, env="N_CTX", ge=1, description="Số lượng context tokens tối đa mà mô hình có thể xử lý")

#     class Config:
#         env_file = ".env"  # Đường dẫn tới file .env

# # Tạo đối tượng settings
# settings = Settings()

# # Ví dụ truy cập các cấu hình
# print(settings.MODEL_PATH)
# print(settings.N_THREADS)
# print(settings.N_CTX)
