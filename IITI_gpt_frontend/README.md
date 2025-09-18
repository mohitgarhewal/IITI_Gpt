# IITI_GPT Frontend 🚀

**Author:** Mohit Garhewal  
**University:** Indian Institute of Technology, Indore  
**Department:** Metallurgical Engineering and Materials Science

---

## 1. Introduction

This is the frontend for IITI-GPT, a conversational AI platform designed to help students at IITI get accurate answers to their questions about the institute. The frontend provides a modern, mobile-friendly chat interface, user authentication, chat history management, and seamless interaction with backend AI agents.

---

## 2. Project Structure & Components

```
IITI_gpt_frontend/
├── app/                # Next.js App Router pages and layouts
│   ├── page.tsx        # Main chat interface UI
│   ├── layout.tsx      # Global layout, navigation, and theme context
│   └── ...             # Other route files (login, register, etc.)
├── components/         # Reusable React components
│   ├── ChatBox.tsx     # Renders chat messages and handles user input
│   ├── Sidebar.tsx     # Displays chat history and session management
│   ├── AuthModal.tsx   # Login and registration modal dialogs
│   ├── ThemeToggle.tsx # Dark/light mode switch
│   └── ...             # Other UI elements
├── lib/                # Utility functions and API services
│   ├── api.ts          # Functions for backend communication (chat, auth)
│   └── ...             # Helpers for authentication, storage, etc.
├── styles/             # Tailwind CSS and custom styles
│   └── globals.css     # Global style definitions
├── public/             # Static assets (icons, images)
├── README.md           # Project documentation (this file)
└── package.json        # Frontend dependencies and scripts
```

### Component Details

- **app/page.tsx**  
  The main chat interface. Displays the conversation between the user and the AI agent, handles message input, and shows streaming responses.

- **app/layout.tsx**  
  Sets up the global layout, navigation bar, and theme context for the entire app.

- **components/ChatBox.tsx**  
  Renders chat messages, manages user input, and triggers message sending to the backend.

- **components/Sidebar.tsx**  
  Shows chat history, allows users to switch between sessions, and manage previous conversations.

- **components/AuthModal.tsx**  
  Provides modal dialogs for user login and registration, handling authentication flows.

- **components/ThemeToggle.tsx**  
  Lets users switch between dark and light modes for a personalized experience.

- **lib/api.ts**  
  Contains functions to communicate with the backend API for chat messages, authentication, and session management.

- **styles/globals.css**  
  Global CSS and Tailwind configuration for consistent styling across the app.

- **public/**  
  Stores static files such as icons and images used in the UI.

---

## 3. Technologies Used

- **Next.js (App Router):** Modern React framework for server-side rendering and routing.
- **TypeScript:** Type safety and improved developer experience.
- **Tailwind CSS:** Utility-first CSS framework for rapid UI development.
- **shadcn/ui:** Prebuilt, accessible UI components for React.
- **React Hooks:** State management and side effects.
- **Local Storage:** Persists user preferences and session data.
- **Framer Motion:** Animations and transitions (if used).

---

## 4. Running Instructions

### Prerequisites

- Node.js (v18 or above recommended)
- npm (comes with Node.js)

### Setup & Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`.

3. **Build for production:**
   ```bash
   npm run build
   npm start
   ```

### Environment Variables

If authentication or API endpoints require configuration, create a `.env.local` file in the root directory and add necessary variables (refer to backend documentation for details).

---

## 5. Usage

- **Register/Login:** Create an account or log in using the authentication modal.
- **Ask Questions:** Use the chat interface to ask questions about IITI.
- **View History:** Access previous conversations from the sidebar.
- **Switch Theme:** Toggle between dark and light modes for comfort.
- **Mobile Friendly:** The interface is optimized for use on smartphones and tablets.

---

## 6. Contact

- **Email:** mems230005028@iiti.ac.in

---
