"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Workflow, Terminal, LogOut } from "lucide-react"
import { TmuxController } from "@/components/controller/TmuxController"
import { TeamCreatorPanel } from "@/components/team-creator/TeamCreatorPanel"
import { useAuth } from "@/contexts/AuthContext"

export default function HomePage() {
  const router = useRouter()
  const { isAuthenticated, isLoading, logout } = useAuth()
  const [activeTab, setActiveTab] = useState("controller")

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  // Wait for auth to finish loading before making routing decisions
  if (isLoading) {
    return null
  }

  // Redirect to login if not authenticated (after loading completes)
  if (!isAuthenticated) {
    router.push("/login")
    return null
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top-level navigation tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="flex-1 flex flex-col overflow-hidden"
      >
        <div className="border-b border-border bg-card px-4 flex items-center justify-between">
          <TabsList className="h-12 bg-transparent gap-2">
            <TabsTrigger
              value="team-creator"
              className="gap-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              <Workflow className="h-4 w-4" />
              <span className="hidden sm:inline">Team Creator</span>
            </TabsTrigger>
            <TabsTrigger
              value="controller"
              className="gap-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              <Terminal className="h-4 w-4" />
              <span className="hidden sm:inline">Controller</span>
            </TabsTrigger>
          </TabsList>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="gap-2"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Logout</span>
          </Button>
        </div>

        <TabsContent
          value="team-creator"
          className="flex-1 m-0 data-[state=active]:flex data-[state=inactive]:hidden overflow-hidden"
        >
          <TeamCreatorPanel />
        </TabsContent>

        <TabsContent
          value="controller"
          className="flex-1 m-0 data-[state=active]:flex data-[state=inactive]:hidden overflow-hidden"
        >
          <TmuxController />
        </TabsContent>
      </Tabs>
    </div>
  )
}
