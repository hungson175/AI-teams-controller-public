"use client"

import type { ReactNode } from "react"
import { AuthProvider } from "@/contexts/AuthContext"
import { SettingsProvider } from "@/contexts/SettingsContext"
import { VoiceFeedbackProvider } from "@/contexts/VoiceFeedbackContext"
import { VoiceNotificationPanel } from "@/components/voice/VoiceNotificationPanel"
import { Toaster } from "@/components/ui/toaster"

interface ProvidersProps {
  children: ReactNode
}

/**
 * Client-side providers wrapper.
 * Wraps the app with all required context providers.
 * Also renders global UI components (notification panel).
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <AuthProvider>
      <SettingsProvider>
        <VoiceFeedbackProvider>
          {children}
          <VoiceNotificationPanel />
          <Toaster />
        </VoiceFeedbackProvider>
      </SettingsProvider>
    </AuthProvider>
  )
}

export default Providers
