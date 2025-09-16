import { AuthService } from "./auth"

export interface Message {
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export interface Chat {
  _id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api"

export class ChatService {
  static async getChats(): Promise<Chat[]> {
    const response = await fetch(`${API_BASE_URL}/chats`, {
      headers: {
        ...AuthService.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch chats")
    }

    return response.json()
  }

  static async getChat(chatId: string): Promise<Chat> {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
      headers: {
        ...AuthService.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch chat")
    }

    return response.json()
  }

  static async createChat(title: string, message: string): Promise<Chat> {
    const response = await fetch(`${API_BASE_URL}/chats`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...AuthService.getAuthHeaders(),
      },
      body: JSON.stringify({ title, message }),
    })

    if (!response.ok) {
      throw new Error("Failed to create chat")
    }

    return response.json()
  }

  static async addMessage(chatId: string, role: "user" | "assistant", content: string): Promise<Chat> {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}/messages`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...AuthService.getAuthHeaders(),
      },
      body: JSON.stringify({ role, content }),
    })

    if (!response.ok) {
      throw new Error("Failed to add message")
    }

    return response.json()
  }

  static async deleteChat(chatId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
      method: "DELETE",
      headers: {
        ...AuthService.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to delete chat")
    }
  }

  static generateChatTitle(message: string): string {
    // Generate a title from the first message (first 50 characters)
    return message.length > 50 ? message.substring(0, 50) + "..." : message
  }
}
