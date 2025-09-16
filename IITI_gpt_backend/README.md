# IITI-GPT Backend

Simple Express.js backend with MongoDB for the AI agent chat application.

## File Structure
\`\`\`
backend/
├── server.js          # Main server file with all routes and logic
├── package.json       # Dependencies and scripts
├── .env              # Environment variables
└── README.md         # This file
\`\`\`

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Chat Management
- `GET /api/chats` - Get user's chat history
- `GET /api/chats/:chatId` - Get specific chat
- `POST /api/chats` - Create new chat
- `POST /api/chats/:chatId/messages` - Add message to chat
- `DELETE /api/chats/:chatId` - Delete chat

## Setup
1. Install dependencies: `npm install`
2. Create `.env` file with required variables
3. Start development server: `npm run dev`
4. Production server: `npm start`

## Database Schema

### Users
- email (String, unique)
- password (String, hashed)
- name (String)
- createdAt (Date)

### Chats
- userId (ObjectId, ref: User)
- title (String)
- messages (Array of Message objects)
- createdAt (Date)
- updatedAt (Date)

### Message
- role (String: 'user' | 'assistant')
- content (String)
- timestamp (Date)
