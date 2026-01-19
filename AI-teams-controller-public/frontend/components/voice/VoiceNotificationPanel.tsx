"use client"

import { useState } from "react"
import { useVoiceFeedback } from "@/contexts/VoiceFeedbackContext"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Play, Trash2, Volume2, Check } from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * Voice Notification Panel
 *
 * Sliding panel from right side showing notification history.
 * Features:
 * - List of voice feedback notifications
 * - Play button for each notification
 * - Read/unread indicators
 * - Clear all functionality
 */
export function VoiceNotificationPanel() {
  const {
    notifications,
    unreadCount,
    isPanelOpen,
    closePanel,
    markAsRead,
    markAllAsRead,
    playNotification,
    clearAll,
  } = useVoiceFeedback()

  const [selectedNotificationId, setSelectedNotificationId] = useState<string | null>(null)

  const selectedNotification = notifications.find(n => n.id === selectedNotificationId)

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    })
  }

  const formatRelativeTime = (timestamp: number) => {
    const now = Date.now()
    const diff = now - timestamp
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)

    if (minutes < 1) return "Just now"
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return formatTime(timestamp)
  }

  const handleNotificationClick = (id: string) => {
    markAsRead(id)
    setSelectedNotificationId(id)
  }

  const handlePlayClick = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    playNotification(id)
  }

  return (
    <>
    <Sheet open={isPanelOpen} onOpenChange={(open) => !open && closePanel()}>
      <SheetContent side="right" className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <Volume2 className="h-5 w-5" />
            Voice Notifications
            {unreadCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {unreadCount} new
              </Badge>
            )}
          </SheetTitle>
          <SheetDescription>
            Global voice feedback from all teams
          </SheetDescription>
        </SheetHeader>

        {/* Actions Bar */}
        <div className="flex items-center justify-between px-4 py-2 border-b">
          <span className="text-xs text-muted-foreground">
            {notifications.length} notification{notifications.length !== 1 ? "s" : ""}
          </span>
          <div className="flex gap-2">
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={markAllAsRead}
                className="h-7 text-xs"
              >
                <Check className="h-3 w-3 mr-1" />
                Mark all read
              </Button>
            )}
            {notifications.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAll}
                className="h-7 text-xs text-destructive hover:text-destructive"
              >
                <Trash2 className="h-3 w-3 mr-1" />
                Clear all
              </Button>
            )}
          </div>
        </div>

        {/* Notification List */}
        <ScrollArea className="flex-1 px-4">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
              <Volume2 className="h-12 w-12 mb-4 opacity-20" />
              <p className="text-sm">No notifications yet</p>
              <p className="text-xs mt-1">
                Voice feedback will appear here
              </p>
            </div>
          ) : (
            <div className="space-y-2 py-4">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification.id)}
                  className={cn(
                    "p-3 rounded-lg border cursor-pointer transition-colors",
                    notification.isRead
                      ? "bg-muted/30 border-border"
                      : "bg-primary/5 border-primary/20 hover:bg-primary/10"
                  )}
                >
                  {/* Header: Time + Source */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {!notification.isRead && (
                        <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                      )}
                      <span
                        className={cn(
                          "text-xs font-medium",
                          notification.isRead
                            ? "text-muted-foreground"
                            : "text-foreground"
                        )}
                      >
                        {formatRelativeTime(notification.timestamp)}
                      </span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {notification.teamId}/{notification.roleId}
                    </Badge>
                  </div>

                  {/* Summary */}
                  <p
                    className={cn(
                      "text-sm line-clamp-2",
                      notification.isRead
                        ? "text-muted-foreground"
                        : "text-foreground"
                    )}
                  >
                    {notification.summary}
                  </p>

                  {/* Actions */}
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-border/50">
                    <span className="text-xs text-muted-foreground">
                      {formatTime(notification.timestamp)}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => handlePlayClick(e, notification.id)}
                      className="h-7 text-xs"
                    >
                      <Play className="h-3 w-3 mr-1" />
                      {notification.isPlayed ? "Replay" : "Play"}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>

      {/* Full Message Dialog */}
      <Dialog open={!!selectedNotificationId} onOpenChange={(open) => !open && setSelectedNotificationId(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Volume2 className="h-5 w-5" />
              Voice Notification
            </DialogTitle>
            <DialogDescription>
              Full message from {selectedNotification?.teamId}/{selectedNotification?.roleId} at {selectedNotification && formatTime(selectedNotification.timestamp)}
            </DialogDescription>
          </DialogHeader>

          <div className="mt-4">
            {/* Full Summary Text */}
            <div className="p-4 bg-muted/50 rounded-lg">
              <p className="text-sm whitespace-pre-wrap leading-relaxed">
                {selectedNotification?.summary}
              </p>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <Badge variant="outline" className="text-xs">
                {selectedNotification && formatRelativeTime(selectedNotification.timestamp)}
              </Badge>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => selectedNotification && playNotification(selectedNotification.id)}
                >
                  <Play className="h-4 w-4 mr-2" />
                  {selectedNotification?.isPlayed ? "Replay" : "Play"}
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => setSelectedNotificationId(null)}
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default VoiceNotificationPanel
