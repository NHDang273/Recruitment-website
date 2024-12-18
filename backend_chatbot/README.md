# Chatbot API with FastAPI and MongoDB

This project is a simple backend implementation for a chatbot using **FastAPI**, **MongoDB**, and **OpenAI's GPT model**.

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.7+**
- **pip** (Python package manager)
- **MongoDB** (For local development or MongoDB Atlas for cloud-based database)

## Setup

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd Backend-RAG-Chatbot
    ```

1. **Create Models folder**:
    Download model llama-2-7b-chat.Q2_K.gguf from https://huggingface.co/transformers/model_doc/gpt2.html into models folder

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

5. **Set up environment variables**:
    Create a `.env` file in the root directory and add the following variables:

    ```bash
    MONGO_URL=mongodb+srv://<username>:<password>@cluster0.mongodb.net/<your_database_name>
    MONGO_DB_NAME=<your_database_name>
    ```

    Replace `<username>`, `<password>`, and `<your_database_name>` with your actual MongoDB credentials and database name.

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
