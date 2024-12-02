# Chatbot API with FastAPI

This project is a simple backend implementation for a chatbot using **FastAPI** and **OpenAI's GPT model**.

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.7+**
- **pip** (Python package manager)

## Setup

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd chatbot_backend
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:
    - On **Windows**:
      ```bash
      venv\Scripts\activate
      ```
    - On **Mac/Linux**:
      ```bash
      source venv/bin/activate
      ```

4. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    If you don't have `requirements.txt`, you can create it by running:
    ```bash
    pip freeze > requirements.txt
    ```

5. **Set up OpenAI API key**:
    - Sign up for an [OpenAI API key](https://platform.openai.com/signup) if you don’t have one.
    - Set your OpenAI API key as an environment variable:
      - On **Windows**:
        ```bash
        set OPENAI_API_KEY=your_openai_api_key
        ```
      - On **Mac/Linux**:
        ```bash
        export OPENAI_API_KEY=your_openai_api_key
        ```

## Running the Project

1. **Start the FastAPI application** using Uvicorn:
    ```bash
    uvicorn app.main:app --reload
    ```

2. **Access the API**:
    - Open your browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).
    - You can view the interactive documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Chatbot API Endpoint

- **POST** `/chatbot/message`
  - **Description**: Sends a user message to the chatbot and returns the response.
  - **Request body**:
    ```json
    {
      "user_message": "Your message here"
    }
    ```
  - **Response**:
    ```json
    {
      "user_message": "Your message here",
      "bot_response": "Bot's reply here"
    }
    ```

### Example cURL command:
```bash
curl -X POST "http://127.0.0.1:8000/chatbot/message" -H "Content-Type: application/json" -d '{"user_message": "Hello, who are you?"}'
