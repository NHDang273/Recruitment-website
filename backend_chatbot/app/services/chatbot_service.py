import openai

# Đảm bảo bạn đã set OPENAI_API_KEY trong biến môi trường
openai.api_key = "your_openai_api_key"

def process_message(user_message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Hoặc mô hình mà bạn đang dùng
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý chatbot."},
                {"role": "user", "content": user_message}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Đã có lỗi xảy ra: {str(e)}"
