"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ThemeToggle } from "@/components/theme-toggle"
import { TypewriterText } from "@/components/typewriter-text"
import { ChatSidebar } from "@/components/chat-sidebar"
import { ChatService, type Message } from "@/lib/chat-service"
import { sendChat } from "@/lib/api"
import { Send, Bot, User, Sparkles, Brain, Zap, MessageCircle, Cpu, Menu, X } from "lucide-react"

interface ChatInterfaceProps {
  onLogout: () => void
}

export function ChatInterface({ onLogout }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [currentChatId, setCurrentChatId] = useState<string | undefined>()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const timer = setTimeout(() => {
      if (inputRef.current && window.innerWidth > 640) {
        inputRef.current.focus()
      }
    }, 1000)
    return () => clearTimeout(timer)
  }, [])

  const loadChat = async (chatId: string) => {
    try {
      const chat = await ChatService.getChat(chatId)
      setMessages(
        chat.messages.map((msg) => ({
          ...msg,
          id: Date.now().toString() + Math.random(),
          timestamp: new Date(msg.timestamp),
        })),
      )
      setCurrentChatId(chatId)
      setSidebarOpen(false)
    } catch (error) {
      console.error("Failed to load chat:", error)
    }
  }

  const startNewChat = () => {
    setMessages([])
    setCurrentChatId(undefined)
    setSidebarOpen(false)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const currentInput = input.trim()
    setInput("")
    setIsLoading(true)
    setIsTyping(true)

    try {
      let chatId = currentChatId
      if (!chatId) {
        const title = ChatService.generateChatTitle(currentInput)
        const newChat = await ChatService.createChat(title, currentInput)
        chatId = newChat._id
        setCurrentChatId(chatId)
      } else {
        await ChatService.addMessage(chatId, "user", currentInput)
      }

      const apiMessages = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }))

      const response = await sendChat(currentInput, apiMessages);
console.log(response);

// Extract the correct content from the response object
const assistantContent = response.final_answer || "I apologize, but I encountered an issue processing your request.";

console.log(assistantContent);

if (chatId) {
  await ChatService.addMessage(chatId, "assistant", assistantContent);
}


      const assistantMessage: Message = {
        role: "assistant",
        content: assistantContent,
        timestamp: new Date(),
      }

      setIsTyping(false)
      setMessages((prev) => [...prev, { ...assistantMessage, isTyping: true }])
    } catch (error) {
      console.error("Chat error:", error)
      setIsTyping(false)
      const errorMessage: Message = {
        role: "assistant",
        content: "I apologize, but I encountered an error. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, { ...errorMessage, isTyping: true }])
    } finally {
      setIsLoading(false)
      setTimeout(() => {
        if (inputRef.current && window.innerWidth > 640) {
          inputRef.current.focus()
        }
      }, 100)
    }
  }

  const handleTypewriterComplete = (messageIndex: number) => {
    setMessages((prev) => prev.map((msg, index) => (index === messageIndex ? { ...msg, isTyping: false } : msg)))
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-background via-background to-muted">
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div
        className={`${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 fixed lg:relative z-50 transition-transform duration-300 ease-in-out`}
      >
        <ChatSidebar
          currentChatId={currentChatId}
          onChatSelect={loadChat}
          onNewChat={startNewChat}
          onLogout={onLogout}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex flex-col h-full w-full max-w-none sm:max-w-4xl sm:mx-auto p-2 sm:p-4 gap-2 sm:gap-4 mobile-tap-highlight">
          {/* Header */}
          <Card className="p-3 sm:p-6 bg-card/50 backdrop-blur-sm border-border/50 hover:bg-card/60 transition-all duration-300 shrink-0 animate-mobile-slide-in">
            <div className="flex items-center gap-2 sm:gap-4">
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden h-8 w-8 shrink-0"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
              </Button>

              <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                <div className="relative group">
                  <Avatar className="h-8 w-8 sm:h-12 sm:w-12 bg-gradient-to-r from-primary to-accent transition-all duration-300 group-hover:scale-110 animate-float">
                    <AvatarFallback className="bg-transparent text-primary-foreground">
                      <Brain className="h-3 w-3 sm:h-6 sm:w-6 animate-pulse" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="absolute -top-1 -right-1">
                    <Sparkles className="h-2 w-2 sm:h-4 sm:w-4 text-accent animate-spin" />
                  </div>
                </div>
                <div className="min-w-0 flex-1">
                  <h1 className="text-responsive-lg font-bold bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent animate-gradient truncate">
                    IITI - GPT Assistant
                  </h1>
                  <p className="text-muted-foreground text-xs sm:text-sm animate-fade-in hidden sm:block">
                    Your intelligent task automation companion
                  </p>
                </div>
              </div>
              <div className="flex gap-1 sm:gap-3 items-center shrink-0">
                <Badge variant="secondary" className="gap-1 animate-pulse text-xs px-1 sm:px-2 animate-glow">
                  <Zap className="h-2 w-2 sm:h-3 sm:w-3" />
                  <span className="hidden sm:inline">Active</span>
                </Badge>
                <Badge variant="outline" className="gap-1 text-xs px-1 sm:px-2 hidden sm:flex">
                  <Cpu className="h-3 w-3" />
                  AI Ready
                </Badge>
                <ThemeToggle />
              </div>
            </div>
          </Card>

          {/* Chat Area */}
          <Card className="flex-1 flex flex-col bg-card/30 backdrop-blur-sm border-border/50 hover:bg-card/40 transition-all duration-300 min-h-0">
            <ScrollArea ref={scrollAreaRef} className="flex-1 p-3 sm:p-6 smooth-scroll touch-action-pan-y">
              <div className="space-y-4 sm:space-y-6 pb-4">
                {messages.length === 0 && (
                  <div className="text-center py-8 sm:py-12 animate-fade-in">
                    <div className="relative mx-auto w-16 h-16 sm:w-20 sm:h-20 mb-4 sm:mb-6">
                      <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent rounded-full animate-pulse"></div>
                      <div className="absolute inset-2 bg-background rounded-full flex items-center justify-center">
                        <MessageCircle className="h-6 w-6 sm:h-8 sm:w-8 text-primary animate-bounce" />
                      </div>
                    </div>
                    <h3 className="text-responsive-lg font-semibold text-foreground mb-2 sm:mb-3 animate-slide-up">
                      Welcome to IITI - GPT!
                    </h3>
                    <p className="text-muted-foreground/70 max-w-md mx-auto leading-relaxed animate-slide-up-delay text-responsive-base px-4">
                      I'm your advanced AI assistant, ready to help automate your daily tasks with intelligent reasoning
                      and planning. Tell me what you'd like to accomplish, and I'll break it down step by step.
                    </p>
                    <div className="flex justify-center gap-3 sm:gap-4 mt-4 sm:mt-6">
                      <div className="flex flex-col items-center gap-1 sm:gap-2 animate-fade-in-delay-1">
                        <div className="w-8 h-8 sm:w-10 sm:h-10 bg-primary/10 rounded-full flex items-center justify-center animate-float">
                          <Brain className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                        </div>
                        <span className="text-xs text-muted-foreground">Smart Planning</span>
                      </div>
                      <div className="flex flex-col items-center gap-1 sm:gap-2 animate-fade-in-delay-2">
                        <div
                          className="w-8 h-8 sm:w-10 sm:h-10 bg-accent/10 rounded-full flex items-center justify-center animate-float"
                          style={{ animationDelay: "0.5s" }}
                        >
                          <Zap className="h-4 w-4 sm:h-5 sm:w-5 text-accent" />
                        </div>
                        <span className="text-xs text-muted-foreground">Fast Execution</span>
                      </div>
                      <div className="flex flex-col items-center gap-1 sm:gap-2 animate-fade-in-delay-3">
                        <div
                          className="w-8 h-8 sm:w-10 sm:h-10 bg-secondary/10 rounded-full flex items-center justify-center animate-float"
                          style={{ animationDelay: "1s" }}
                        >
                          <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 text-secondary" />
                        </div>
                        <span className="text-xs text-muted-foreground">AI Powered</span>
                      </div>
                    </div>
                  </div>
                )}

                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-2 sm:gap-4 ${message.role === "user" ? "justify-end" : "justify-start"} animate-message-pop`}
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    {message.role === "assistant" && (
                      <Avatar className="h-6 w-6 sm:h-8 sm:w-8 bg-gradient-to-r from-primary to-accent shrink-0 hover:scale-110 transition-transform duration-200 touch-target">
                        <AvatarFallback className="bg-transparent text-primary-foreground">
                          <Bot className="h-3 w-3 sm:h-4 sm:w-4" />
                        </AvatarFallback>
                      </Avatar>
                    )}

                    <div
                      className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-3 py-2 sm:px-4 sm:py-3 transition-all duration-300 hover:scale-[1.02] ${
                        message.role === "user"
                          ? "bg-gradient-to-r from-primary to-primary/90 text-primary-foreground ml-8 sm:ml-12 hover:shadow-lg animate-glow"
                          : "bg-muted/80 text-muted-foreground hover:bg-muted"
                      }`}
                    >
                      <div className="text-responsive-base leading-relaxed whitespace-pre-wrap">
                        {message.role === "assistant" && (message as any).isTyping ? (
                          <TypewriterText
                            text={message.content}
                            speed={20}
                            onComplete={() => handleTypewriterComplete(index)}
                          />
                        ) : (
                          message.content
                        )}
                      </div>
                      <p
                        className={`text-xs mt-1 sm:mt-2 opacity-70 ${
                          message.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground/70"
                        }`}
                      >
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </p>
                    </div>

                    {message.role === "user" && (
                      <Avatar className="h-6 w-6 sm:h-8 sm:w-8 bg-gradient-to-r from-accent to-secondary shrink-0 hover:scale-110 transition-transform duration-200 touch-target">
                        <AvatarFallback className="bg-transparent text-accent-foreground">
                          <User className="h-3 w-3 sm:h-4 sm:w-4" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                  </div>
                ))}

                {(isLoading || isTyping) && (
                  <div className="flex gap-2 sm:gap-4 justify-start animate-message-pop">
                    <Avatar className="h-6 w-6 sm:h-8 sm:w-8 bg-gradient-to-r from-primary to-accent shrink-0">
                      <AvatarFallback className="bg-transparent text-primary-foreground">
                        <Bot className="h-3 w-3 sm:h-4 sm:w-4 animate-typing-indicator" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="bg-muted/80 text-muted-foreground rounded-2xl px-3 py-2 sm:px-4 sm:py-3 animate-pulse">
                      <div className="flex items-center gap-2 sm:gap-3">
                        <div className="flex gap-1">
                          <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                          <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-accent rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                          <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-secondary rounded-full animate-bounce"></div>
                        </div>
                        <span className="text-xs animate-pulse">
                          {isTyping ? "IITI-GPT is analyzing..." : "Processing..."}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            <Separator />

            {/* Input Area */}
            <div className="p-3 sm:p-6 bg-background/95 backdrop-blur-sm">
              <form onSubmit={handleSubmit} className="flex gap-2 sm:gap-3">
                <div className="flex-1 relative group">
                  <Input
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Describe a task you'd like IITI-GPT to help automate..."
                    className="pr-4 h-10 sm:h-12 text-sm sm:text-base bg-background/50 border-border/50 focus:bg-background transition-all duration-300 group-hover:border-primary/30 focus:border-primary/50 focus:shadow-lg mobile-input mobile-optimized touch-target"
                    disabled={isLoading}
                  />
                  <div className="absolute inset-0 rounded-md bg-gradient-to-r from-primary/20 to-accent/20 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 -z-10 blur-sm"></div>
                </div>
                <Button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="h-10 sm:h-12 px-3 sm:px-6 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground transition-all duration-300 hover:scale-105 hover:shadow-lg disabled:hover:scale-100 touch-target animate-glow"
                >
                  <Send className="h-3 w-3 sm:h-4 sm:w-4" />
                </Button>
              </form>
              <p className="text-xs text-muted-foreground/70 mt-1 sm:mt-2 text-center animate-fade-in">
                Press Enter to send • IITI-GPT will analyze and execute your request
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
