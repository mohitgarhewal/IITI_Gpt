"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Brain, Sparkles, Zap, Target, Lightbulb } from "lucide-react"

const welcomeMessages = [
  "Welcome to IITI - GPT",
  "Your Intelligent Task Automation Companion",
  "Powered by Advanced AI Reasoning",
  "Ready to Transform Your Workflow",
  "Let's Build Something Amazing Together",
]

interface WelcomeLoaderProps {
  onComplete: () => void
}

export function WelcomeLoader({ onComplete }: WelcomeLoaderProps) {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0)
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentMessageIndex((prev) => {
        if (prev < welcomeMessages.length - 1) {
          return prev + 1
        } else {
          // Start fade out after showing all messages
          setTimeout(() => {
            setIsVisible(false)
            setTimeout(onComplete, 500) // Wait for fade out animation
          }, 1500)
          clearInterval(timer)
          return prev
        }
      })
    }, 1200)

    return () => clearInterval(timer)
  }, [onComplete])

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-background via-background to-muted transition-opacity duration-500 ${isVisible ? "opacity-100" : "opacity-0"}`}
    >
      <Card className="p-12 bg-card/90 backdrop-blur-xl border-border/50 shadow-2xl max-w-2xl mx-4">
        <div className="text-center space-y-8">
          {/* Animated Logo */}
          <div className="relative mx-auto w-24 h-24">
            <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent rounded-full animate-pulse"></div>
            <div className="absolute inset-2 bg-background rounded-full flex items-center justify-center">
              <Brain className="h-10 w-10 text-primary animate-bounce" />
            </div>
            <div className="absolute -top-2 -right-2">
              <Sparkles className="h-6 w-6 text-accent animate-spin" />
            </div>
            <div className="absolute -bottom-2 -left-2">
              <Zap className="h-5 w-5 text-secondary animate-pulse" />
            </div>
          </div>

          {/* Welcome Messages */}
          <div className="space-y-4 min-h-[120px] flex flex-col justify-center">
            <h1 className="text-4xl font-bold text-primary animate-pulse drop-shadow-sm">{welcomeMessages[0]}</h1>

            {currentMessageIndex > 0 && (
              <div className="space-y-3 animate-fade-in">
                {welcomeMessages.slice(1, currentMessageIndex + 1).map((message, index) => (
                  <p
                    key={index}
                    className={`text-lg text-foreground transition-all duration-700 ${
                      index === currentMessageIndex - 1 ? "animate-slide-up opacity-100" : "opacity-70"
                    }`}
                  >
                    {message}
                  </p>
                ))}
              </div>
            )}
          </div>

          {/* Loading Animation */}
          <div className="flex items-center justify-center gap-3">
            <div className="flex gap-2">
              <div className="w-3 h-3 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-3 h-3 bg-accent rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-3 h-3 bg-secondary rounded-full animate-bounce"></div>
            </div>
            <span className="text-sm text-muted-foreground animate-pulse">Initializing AI Systems...</span>
          </div>

          {/* Feature Icons */}
          <div className="flex justify-center gap-6 pt-4">
            <div className="flex flex-col items-center gap-2 animate-fade-in-delay-1">
              <Target className="h-6 w-6 text-primary animate-pulse" />
              <span className="text-xs text-muted-foreground">Planning</span>
            </div>
            <div className="flex flex-col items-center gap-2 animate-fade-in-delay-2">
              <Brain className="h-6 w-6 text-accent animate-pulse" />
              <span className="text-xs text-muted-foreground">Reasoning</span>
            </div>
            <div className="flex flex-col items-center gap-2 animate-fade-in-delay-3">
              <Lightbulb className="h-6 w-6 text-secondary animate-pulse" />
              <span className="text-xs text-muted-foreground">Execution</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
