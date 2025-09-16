"use client"

import { useState, useEffect } from "react"
import { ChatInterface } from "@/components/chat-interface"
import { WelcomeLoader } from "@/components/welcome-loader"
import { AuthModal } from "@/components/auth-modal"
import { AuthService } from "@/lib/auth"

export default function Home() {
  const [showLoader, setShowLoader] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  useEffect(() => {
    const checkAuth = () => {
      const authenticated = AuthService.isAuthenticated()
      setIsAuthenticated(authenticated)
      setIsCheckingAuth(false)

      if (!authenticated) {
        setShowAuthModal(true)
      }
    }

    checkAuth()
  }, [])

  const handleAuthSuccess = () => {
    setIsAuthenticated(true)
    setShowAuthModal(false)
  }

  const handleLogout = () => {
    AuthService.logout()
    setIsAuthenticated(false)
    setShowAuthModal(true)
  }

  if (isCheckingAuth) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {showLoader && <WelcomeLoader onComplete={() => setShowLoader(false)} />}
      {!showLoader && isAuthenticated && <ChatInterface onLogout={handleLogout} />}

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} onSuccess={handleAuthSuccess} />
    </main>
  )
}
