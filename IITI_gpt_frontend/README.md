# IITI-GPT AI Agent Prototype

A modern, interactive AI agent chat interface built for university assignment submission. This prototype demonstrates intelligent task automation with user authentication and chat history management.

## Student Information
- **Name**: [Your Name]
- **University**: Indian Institute of Technology Indore (IITI)
- **Department**: [Your Department]
- **Assignment**: AI Agent Prototype Development

## Features

### Core Features (Mandatory)
- **AI Agent Interface**: Interactive chat UI for task automation
- **Intelligent Reasoning**: AI-powered task planning and execution
- **Modern UI/UX**: Responsive design inspired by ChatGPT and v0.dev
- **Real-time Chat**: Typewriter effects and streaming responses

### Bonus Features Implemented
- **User Authentication**: Registration and login system
- **Chat History**: Persistent conversation storage in MongoDB
- **Multi-session Support**: Users can manage multiple chat conversations
- **Responsive Design**: Mobile-first approach with touch optimizations
- **Dark/Light Mode**: Theme switching capability

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4 with shadcn/ui components
- **State Management**: React hooks with local storage
- **Animations**: CSS animations and Framer Motion principles

### Backend
- **Runtime**: Node.js with Express.js
- **Database**: MongoDB with Mongoose ODM
- **Authentication**: JWT tokens with bcrypt password hashing
- **API Design**: RESTful endpoints for auth and chat management

### Key Design Decisions
1. **Next.js App Router**: Chosen for modern React patterns and server-side capabilities
2. **MongoDB**: Selected for flexible document storage suitable for chat messages
3. **JWT Authentication**: Stateless authentication for scalability
4. **Minimal Backend Structure**: Simple folder organization as requested
5. **TypeScript**: Type safety for better development experience

## Installation & Setup

### Backend Setup
\`\`\`bash
cd backend
npm install
npm run dev
\`\`\`

### Frontend Setup
\`\`\`bash
npm install
npm run dev
\`\`\`

### Environment Variables
Create `.env` file in backend directory:
\`\`\`
MONGODB_URI=mongodb://localhost:27017/iiti-gpt
JWT_SECRET=your-super-secret-jwt-key
PORT=5000
\`\`\`

## System Architecture

### Component Breakdown
- **Authentication System**: Login/register modals with JWT token management
- **Chat Interface**: Main conversation UI with typewriter effects
- **Chat Sidebar**: History management with CRUD operations
- **Theme System**: Dark/light mode toggle with persistent preferences
- **API Layer**: Service classes for backend communication

### Data Design
- **Users Collection**: Email, password (hashed), name, timestamps
- **Chats Collection**: User reference, title, messages array, timestamps
- **Message Schema**: Role (user/assistant), content, timestamp

## Social Impact & Originality

This AI agent prototype addresses the growing need for intelligent task automation in academic and professional environments. By providing an intuitive chat interface, users can delegate complex multi-step tasks to AI, improving productivity and reducing manual effort. The system's ability to maintain conversation history enables continuous learning and task refinement.

## Demo Usage

1. **Registration**: Create account with email and password
2. **Task Description**: Describe any manual task you want automated
3. **AI Processing**: Watch as the agent analyzes and plans execution
4. **History Management**: Access previous conversations from sidebar
5. **Multi-device Support**: Seamless experience across desktop and mobile

## Evaluation Criteria Addressed

- **System Design**: Clean architecture with separation of concerns
- **Coding**: TypeScript, modern React patterns, and best practices
- **Originality**: Unique combination of features with impressive UI/UX
- **UI/UX Design**: Modern, responsive interface with smooth animations

## Future Enhancements

- Multi-agent collaboration system
- External tool integrations (RAG, MCP)
- Batch execution and scheduling
- Advanced monitoring dashboard
- Voice interaction capabilities
