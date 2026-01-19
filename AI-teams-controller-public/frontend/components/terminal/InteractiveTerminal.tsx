"use client"

import { useEffect, useRef, useCallback } from "react"
import { Terminal } from "xterm"
import { FitAddon } from "@xterm/addon-fit"
import { WebLinksAddon } from "@xterm/addon-web-links"
import "xterm/css/xterm.css"

interface InteractiveTerminalProps {
  /** JWT token for authentication */
  token: string
  /** Whether the terminal tab is visible */
  isVisible: boolean
}

// Terminal service port (Node.js microservice)
const TERMINAL_PORT = 17071

// Production terminal WebSocket URL (via Cloudflare tunnel)
const TERMINAL_WS_URL = process.env.NEXT_PUBLIC_TERMINAL_WS_URL

export function InteractiveTerminal({ token, isVisible }: InteractiveTerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null)
  const xtermRef = useRef<Terminal | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const fitAddonRef = useRef<FitAddon | null>(null)

  const connect = useCallback(() => {
    if (!terminalRef.current || !token) return

    // Create terminal
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: "#1e1e1e",
        foreground: "#d4d4d4",
        cursor: "#ffffff",
      },
    })

    // Add addons
    const fitAddon = new FitAddon()
    terminal.loadAddon(fitAddon)
    terminal.loadAddon(new WebLinksAddon())

    // Mount terminal
    terminal.open(terminalRef.current)
    fitAddon.fit()

    xtermRef.current = terminal
    fitAddonRef.current = fitAddon

    // Connect to Node.js terminal service (NOT FastAPI)
    // In production, use dedicated terminal hostname via Cloudflare tunnel
    // In development, connect directly to localhost:17071
    let wsUrl: string
    if (TERMINAL_WS_URL) {
      // Production: use configured terminal WebSocket URL
      wsUrl = `${TERMINAL_WS_URL}/terminal?token=${encodeURIComponent(token)}`
    } else {
      // Development: use localhost with port
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
      wsUrl = `${wsProtocol}//${window.location.hostname}:${TERMINAL_PORT}/terminal?token=${encodeURIComponent(token)}`
    }

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      // Send initial size
      const { cols, rows } = terminal
      ws.send(JSON.stringify({ type: "resize", cols, rows }))
    }

    ws.onmessage = (event) => {
      terminal.write(event.data)
    }

    ws.onclose = () => {
      terminal.write("\r\n\x1b[31mConnection closed\x1b[0m\r\n")
    }

    // Forward terminal input to WebSocket
    terminal.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data)
      }
    })

    // Handle resize
    terminal.onResize(({ cols, rows }) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "resize", cols, rows }))
      }
    })

    // Handle window resize
    const handleResize = () => {
      if (fitAddonRef.current) {
        fitAddonRef.current.fit()
      }
    }
    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      ws.close()
      terminal.dispose()
    }
  }, [token])

  useEffect(() => {
    if (isVisible) {
      const cleanup = connect()
      return cleanup
    }
  }, [isVisible, connect])

  // Fit terminal when tab becomes visible
  useEffect(() => {
    if (isVisible && fitAddonRef.current) {
      setTimeout(() => fitAddonRef.current?.fit(), 100)
    }
  }, [isVisible])

  return (
    <div
      ref={terminalRef}
      className="h-full w-full bg-[#1e1e1e]"
      style={{ minHeight: "400px" }}
    />
  )
}
