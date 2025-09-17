# IITI-GPT Backend

Backend for the IITI-GPT AI chat application, providing user authentication, chat management, and document-based AI responses.

## Folder Structure

```
IITI_gpt_backend/
├── server.js          # Main Express.js server with API routes and logic
├── package.json       # Node.js dependencies and scripts
├── .env               # Environment variables for backend
├── setup.bat          # Windows batch script for Python environment setup
├── docs/              # Folder for IITI PDFs/texts (created by setup.bat)
└── README.md          # Project documentation
```

## Setup Instructions

1. **Python Environment Setup**  
   Run `setup.bat` in this folder to:
   - Create a Python virtual environment
   - Install required Python packages for AI and document processing
   - Set environment variables for OpenAI and embedding models
   - Create the `docs` folder for your source files

   ```
   setup.bat
   ```

   > After running, restart your terminal to apply environment variables.

2. **Node.js Backend Setup**  
   - Install backend dependencies:
     ```
     npm install
     ```
   - Create a `.env` file with your MongoDB URI and other secrets.
   - Start the development server:
     ```
     npm run dev
     ```
   - For production:
     ```
     npm start
     ```

## How It Works

- **Document Ingestion:**  
  Place IITI PDFs or text files in the `docs` folder. The backend uses Python scripts and AI models to process and embed these documents for semantic search.

- **Chat API:**  
  The Express.js backend provides RESTful endpoints for user registration, login, chat creation, message exchange, and chat history management. Each chat is linked to a user and stores messages between the user and the AI assistant.

- **AI Responses:**  
  When a user sends a message, the backend uses OpenAI and embedding models to generate context-aware responses based on the ingested documents.

## API Endpoints

- **Authentication**
  - `POST /api/register` — Register a new user
  - `POST /api/login` — User login

- **Chat Management**
  - `GET /api/chats` — List user chats
  - `GET /api/chats/:chatId` — Get a specific chat
  - `POST /api/chats` — Create a new chat
  - `POST /api/chats/:chatId/messages` — Add a message
  - `DELETE /api/chats/:chatId` — Delete a chat

## Database Schema Overview

- **Users:** email, password (hashed), name, createdAt
- **Chats:** userId, title, messages, createdAt, updatedAt
- **Messages:** role (`user` or `assistant`), content, timestamp

---
For questions or issues, please refer to this README or contact the project maintainer.