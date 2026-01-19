/**
 * Soniox STT Service - WebSocket-based Speech-to-Text
 *
 * Connects to Soniox WebSocket API for real-time transcription.
 * Uses stop-word-based detection to finalize commands.
 *
 * CRITICAL: Soniox protocol requires:
 * 1. Send JSON config message FIRST (text frame)
 * 2. Then send binary audio chunks (binary frames)
 */

import { StopWordDetector } from "./stopword-detector"
import { AudioCapture } from "./audio-capture"
import { getAuthHeaders } from "@/lib/auth-utils"
import { tryRefreshTokens } from "@/lib/auth"

// Soniox WebSocket endpoint
const SONIOX_WS_URL = "wss://stt-rt.soniox.com/transcribe-websocket"

// Keepalive ping interval (30 seconds) - prevents Cloudflare/proxy timeouts
const PING_INTERVAL_MS = 30000

/**
 * Soniox configuration sent as first message
 */
interface SonioxConfig {
  api_key: string
  model: string
  sample_rate: number
  num_channels: number
  audio_format: string
  language_hints?: string[]
  language_hints_strict?: boolean
}

/**
 * Soniox token from single word
 */
interface SonioxToken {
  text: string
  is_final: boolean
  start_ms?: number
  duration_ms?: number
  confidence?: number
}

/**
 * Soniox WebSocket response
 */
interface SonioxResponse {
  tokens?: SonioxToken[]
  error_message?: string
}

/**
 * Detection mode for finalizing transcripts (only stopword supported)
 */
export type SonioxDetectionMode = "stopword"

/**
 * Service configuration
 */
export interface SonioxServiceConfig {
  /** Detection mode: only stop-word-based detection is supported */
  detectionMode: SonioxDetectionMode
  /** Soniox model (default: stt-rt-preview) */
  model?: string
  /** Stop word to trigger command finalization (default: "thank you") */
  stopWord?: string
}

/**
 * Event callbacks
 */
export interface SonioxServiceCallbacks {
  /** Called for each transcript update (interim + final) */
  onTranscript?: (transcript: string, isFinal: boolean) => void
  /** Called when command is finalized (ready to send) */
  onFinalize?: (command: string) => void
  /** Called on connection state change */
  onConnectionChange?: (connected: boolean) => void
  /** Called on error */
  onError?: (error: Error) => void
  /** Called on audio level change (for UI) */
  onAudioLevel?: (levelDb: number) => void
  /** Called when AudioContext state changes (suspended/running) - for mobile mic suspension */
  onAudioStateChange?: (state: AudioContextState, resumed: boolean) => void
}

/**
 * Default service configuration
 */
export const DEFAULT_SONIOX_SERVICE_CONFIG: Required<SonioxServiceConfig> = {
  detectionMode: "stopword",
  model: "stt-rt-preview",
  stopWord: "thank you",
}

/**
 * Soniox STT Service
 *
 * Manages WebSocket connection, audio streaming, and detection.
 */
export class SonioxSTTService {
  private config: Required<SonioxServiceConfig>
  private callbacks: SonioxServiceCallbacks
  private websocket: WebSocket | null = null
  private audioCapture: AudioCapture | null = null
  private stopWordDetector: StopWordDetector
  private isConnected = false
  private transcript = ""
  private apiKey: string | null = null
  private lastClearTimestamp = 0  // Track when transcript was cleared to ignore buffered messages
  private pingInterval: ReturnType<typeof setInterval> | null = null  // Keepalive ping timer

  constructor(
    config: Partial<SonioxServiceConfig> = {},
    callbacks: SonioxServiceCallbacks = {}
  ) {
    this.config = { ...DEFAULT_SONIOX_SERVICE_CONFIG, ...config }
    this.callbacks = callbacks

    // Initialize stop word detector
    this.stopWordDetector = new StopWordDetector({
      stopWord: this.config.stopWord,
    })
  }

  /**
   * Fetch Soniox API key from backend
   */
  private async fetchApiKey(): Promise<string> {
    let response = await fetch(`/api/voice/token/soniox`, {
      method: "POST",
      headers: getAuthHeaders(),
    })

    // Handle 401: try refresh tokens and retry once
    if (response.status === 401) {
      const refreshed = await tryRefreshTokens()
      if (refreshed) {
        response = await fetch(`/api/voice/token/soniox`, {
          method: "POST",
          headers: getAuthHeaders(),
        })
      } else {
        throw new Error("Authentication required")
      }
    }

    if (!response.ok) {
      throw new Error(`Failed to get Soniox token: ${response.status}`)
    }

    const data = await response.json()
    return data.api_key
  }

  /**
   * Connect to Soniox WebSocket and start audio capture
   */
  async connect(): Promise<void> {
    if (this.isConnected) {
      throw new Error("Already connected")
    }

    try {
      // Get API key from backend
      console.log("[Soniox] Fetching API key...")
      this.apiKey = await this.fetchApiKey()

      // Connect to WebSocket
      console.log("[Soniox] Connecting to WebSocket...")
      this.websocket = new WebSocket(SONIOX_WS_URL)

      // Wait for WebSocket to open
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error("WebSocket connection timeout"))
        }, 10000)

        this.websocket!.onopen = () => {
          clearTimeout(timeout)
          resolve()
        }

        this.websocket!.onerror = (event) => {
          clearTimeout(timeout)
          reject(new Error("WebSocket connection failed"))
        }
      })

      // Send config as first message (CRITICAL: must be JSON text frame)
      const config: SonioxConfig = {
        api_key: this.apiKey,
        model: this.config.model,
        sample_rate: 16000,
        num_channels: 1,
        audio_format: "pcm_s16le",
        language_hints: ["vi", "en"],
        language_hints_strict: true,
      }
      this.websocket.send(JSON.stringify(config))
      console.log("[Soniox] Sent config:", config.model)

      // Set up message handler
      this.websocket.onmessage = this.handleMessage.bind(this)

      this.websocket.onerror = (event) => {
        console.error("[Soniox] WebSocket error:", event)
        this.callbacks.onError?.(new Error("WebSocket error"))
      }

      this.websocket.onclose = (event: CloseEvent) => {
        // Log close reason for debugging (helps identify timeout vs error vs intentional close)
        console.log(`[Soniox] WebSocket closed - code: ${event.code}, reason: "${event.reason || 'none'}", wasClean: ${event.wasClean}`)
        this.stopPingInterval()
        this.isConnected = false
        this.callbacks.onConnectionChange?.(false)
      }

      // Start keepalive ping interval (prevents Cloudflare/proxy timeouts)
      this.startPingInterval()

      // Start audio capture
      console.log("[Soniox] Starting audio capture...")
      this.audioCapture = new AudioCapture({ sampleRate: 16000 })

      // Set up audio state callback (notifies when AudioContext suspended/resumed on mobile)
      this.audioCapture.setStateCallback((state, resumed) => {
        console.log(`[Soniox] AudioContext state: ${state}, resumed: ${resumed}`)
        this.callbacks.onAudioStateChange?.(state, resumed)
      })

      await this.audioCapture.start(this.handleAudioChunk.bind(this))

      this.isConnected = true
      this.transcript = ""
      this.callbacks.onConnectionChange?.(true)
      console.log("[Soniox] Connected and streaming")
    } catch (error) {
      console.error("[Soniox] Connection error:", error)
      this.cleanup()
      throw error
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const data: SonioxResponse = JSON.parse(event.data)

      // Check for errors
      if (data.error_message) {
        console.error("[Soniox] Error:", data.error_message)
        this.callbacks.onError?.(new Error(data.error_message))
        return
      }

      // Process tokens
      if (data.tokens) {
        let finalText = ""
        let interimText = ""

        for (const token of data.tokens) {
          if (token.is_final) {
            finalText += token.text
          } else {
            interimText += token.text
          }
        }

        // Accumulate final text (but ignore if recently cleared to avoid showing buffered old text)
        const timeSinceClear = Date.now() - this.lastClearTimestamp
        const shouldIgnoreBuffered = timeSinceClear < 500  // Ignore buffered messages for 500ms after clear

        if (finalText && !shouldIgnoreBuffered) {
          this.transcript += finalText
        } else if (finalText && shouldIgnoreBuffered) {
          console.log("[Soniox] Ignoring buffered final text after clear:", finalText.substring(0, 50))
        }

        // Emit transcript update (always show interim text for immediate feedback)
        const fullTranscript = this.transcript + interimText
        this.callbacks.onTranscript?.(fullTranscript, finalText.length > 0 && !shouldIgnoreBuffered)

        // Check for stop word
        const result = this.stopWordDetector.processTranscript(this.transcript)
        if (result.detected) {
          console.log("[Soniox] Stop word detected!")
          this.handleFinalize(result.command)
        }
      }
    } catch (error) {
      console.error("[Soniox] Message parse error:", error)
    }
  }

  /**
   * Handle audio chunk from capture
   */
  private handleAudioChunk(float32Data: Float32Array, int16Data: Int16Array): void {
    // Send audio to WebSocket (binary frame)
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(int16Data.buffer)
    }
  }

  /**
   * Handle command finalization
   */
  private handleFinalize(command: string): void {
    console.log("[Soniox] Finalizing command:", command)
    this.callbacks.onFinalize?.(command)

    // Reset for next command (hands-free mode)
    this.transcript = ""
  }

  /**
   * Send audio data manually (alternative to automatic capture)
   */
  sendAudio(int16Data: Int16Array): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(int16Data.buffer)
    }
  }

  /**
   * Disconnect and cleanup
   */
  disconnect(): void {
    console.log("[Soniox] Disconnecting...")
    this.cleanup()
  }

  /**
   * Check if connected
   */
  get connected(): boolean {
    return this.isConnected
  }

  /**
   * Get current transcript
   */
  getTranscript(): string {
    return this.transcript
  }

  /**
   * Reset accumulated transcript (for clear button)
   * Does NOT stop recording - just clears the buffer
   */
  resetTranscript(): void {
    this.transcript = ""
    this.lastClearTimestamp = Date.now()  // Mark clear time to ignore buffered messages
    this.stopWordDetector.reset()
    this.callbacks.onTranscript?.("", false)
    console.log("[Soniox] Transcript reset at", this.lastClearTimestamp)
  }

  /**
   * Get current configuration
   */
  getConfig(): Required<SonioxServiceConfig> {
    return { ...this.config }
  }

  /**
   * Update configuration (only effective before connect)
   */
  updateConfig(config: Partial<SonioxServiceConfig>): void {
    if (this.isConnected) {
      throw new Error("Cannot update config while connected")
    }
    this.config = { ...this.config, ...config }

    // Reinitialize stop word detector if stop word changed
    if (config.stopWord) {
      this.stopWordDetector = new StopWordDetector({
        stopWord: this.config.stopWord,
      })
    }
  }

  /**
   * Update callbacks
   */
  updateCallbacks(callbacks: Partial<SonioxServiceCallbacks>): void {
    this.callbacks = { ...this.callbacks, ...callbacks }
  }

  /**
   * Start keepalive ping interval
   * NOTE: Disabled - Soniox protocol requires BINARY-ONLY after initial JSON config.
   * Sending JSON pings violates protocol and causes connection drops.
   * Unlike Cloudflare tunnels, Soniox doesn't need keepalive pings.
   */
  private startPingInterval(): void {
    // DISABLED: Soniox expects binary audio only after config.
    // JSON pings violate the protocol and cause disconnections.
    // See: https://soniox.com/docs (binary-only after config)
    console.log("[Soniox] Keepalive ping DISABLED (not compatible with Soniox protocol)")
  }

  /**
   * Stop keepalive ping interval
   */
  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
      console.log("[Soniox] Stopped keepalive ping interval")
    }
  }

  /**
   * Cleanup resources
   */
  private cleanup(): void {
    this.isConnected = false
    this.stopPingInterval()

    if (this.audioCapture) {
      this.audioCapture.stop()
      this.audioCapture = null
    }

    if (this.websocket) {
      this.websocket.close()
      this.websocket = null
    }

    this.callbacks.onConnectionChange?.(false)
  }
}
