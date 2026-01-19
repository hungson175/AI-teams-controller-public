/**
 * Audio Capture - Microphone Audio Streaming
 *
 * Captures audio from microphone at 16kHz for Soniox STT.
 *
 * Uses Web Audio API with ScriptProcessorNode for audio processing.
 * Note: ScriptProcessorNode is deprecated but AudioWorklet requires
 * more setup (separate file, module loading). For simplicity and
 * browser compatibility, we use ScriptProcessorNode.
 */

/**
 * Audio capture configuration
 */
export interface AudioCaptureConfig {
  /** Sample rate in Hz (16000 for Soniox) */
  sampleRate: 16000
  /** Number of audio channels (always 1 for mono) */
  channelCount?: 1
  /** Chunk size in samples (default: 1024) */
  chunkSize?: number
  /** Enable echo cancellation */
  echoCancellation?: boolean
  /** Enable noise suppression */
  noiseSuppression?: boolean
}

/**
 * Audio chunk callback type
 */
export type AudioChunkCallback = (
  /** Float32 audio data (-1 to 1) */
  float32Data: Float32Array,
  /** Int16 PCM audio data */
  int16Data: Int16Array
) => void

/**
 * Audio state change callback type
 */
export type AudioStateCallback = (state: AudioContextState, resumed: boolean) => void

/**
 * Default audio capture configuration
 */
export const DEFAULT_AUDIO_CAPTURE_CONFIG: Required<AudioCaptureConfig> = {
  sampleRate: 16000,
  channelCount: 1,
  chunkSize: 1024,
  echoCancellation: true,
  noiseSuppression: true,
}

/**
 * Audio Capture Class
 *
 * Manages microphone capture with Web Audio API.
 */
export class AudioCapture {
  private config: Required<AudioCaptureConfig>
  private audioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private processor: ScriptProcessorNode | null = null
  private source: MediaStreamAudioSourceNode | null = null
  private isCapturing = false
  private onStateChange: AudioStateCallback | null = null
  private visibilityHandler: (() => void) | null = null

  constructor(config: Partial<AudioCaptureConfig> = {}) {
    this.config = { ...DEFAULT_AUDIO_CAPTURE_CONFIG, ...config }
  }

  /**
   * Set callback for AudioContext state changes (suspended/running)
   * Useful for notifying user when mic is suspended on mobile
   */
  setStateCallback(callback: AudioStateCallback | null): void {
    this.onStateChange = callback
  }

  /**
   * Convert Float32 audio samples to Int16 PCM
   *
   * @param float32Array - Audio samples in -1 to 1 range
   * @returns Int16 PCM samples
   */
  static float32ToInt16(float32Array: Float32Array): Int16Array {
    const int16Array = new Int16Array(float32Array.length)

    for (let i = 0; i < float32Array.length; i++) {
      // Clamp to -1 to 1 range
      const s = Math.max(-1, Math.min(1, float32Array[i]))
      // Convert to Int16 range (-32768 to 32767)
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7fff
    }

    return int16Array
  }

  /**
   * Convert Int16 PCM to base64 string
   *
   * @param int16Array - Int16 PCM samples
   * @returns Base64 encoded string
   */
  static int16ToBase64(int16Array: Int16Array): string {
    const bytes = new Uint8Array(int16Array.buffer)
    let binary = ""
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return btoa(binary)
  }

  /**
   * Start audio capture
   *
   * @param onChunk - Callback for each audio chunk
   * @returns Promise that resolves when capture starts
   */
  async start(onChunk: AudioChunkCallback): Promise<void> {
    if (this.isCapturing) {
      throw new Error("Audio capture already started")
    }

    try {
      // Request microphone access with configured constraints
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channelCount,
          echoCancellation: this.config.echoCancellation,
          noiseSuppression: this.config.noiseSuppression,
        },
      })

      // Create AudioContext with target sample rate
      this.audioContext = new AudioContext({
        sampleRate: this.config.sampleRate,
      })

      // Handle AudioContext state changes (mobile browsers suspend when screen dims)
      this.audioContext.onstatechange = () => {
        const state = this.audioContext?.state
        console.log(`[AudioCapture] AudioContext state changed to: ${state}`)

        if (state === 'suspended' && this.isCapturing) {
          console.warn('[AudioCapture] AudioContext suspended - attempting resume...')
          this.onStateChange?.(state, false)
          // Try to resume immediately
          this.tryResume()
        } else if (state === 'running') {
          this.onStateChange?.(state, true)
        }
      }

      // Handle visibility change - resume AudioContext when tab becomes visible
      this.visibilityHandler = () => {
        if (document.visibilityState === 'visible' && this.audioContext && this.isCapturing) {
          console.log('[AudioCapture] Tab visible, checking AudioContext state...')
          if (this.audioContext.state === 'suspended') {
            console.log('[AudioCapture] AudioContext suspended, attempting resume...')
            this.tryResume()
          }
        }
      }
      document.addEventListener('visibilitychange', this.visibilityHandler)

      // Create source from media stream
      this.source = this.audioContext.createMediaStreamSource(this.mediaStream)

      // Create ScriptProcessor for audio processing
      // Note: Deprecated but widely supported. AudioWorklet requires more setup.
      this.processor = this.audioContext.createScriptProcessor(
        this.config.chunkSize,
        this.config.channelCount,
        this.config.channelCount
      )

      // Process audio chunks
      this.processor.onaudioprocess = (event) => {
        if (!this.isCapturing) return

        const float32Data = event.inputBuffer.getChannelData(0)
        const int16Data = AudioCapture.float32ToInt16(float32Data)

        onChunk(float32Data, int16Data)
      }

      // Connect audio nodes
      this.source.connect(this.processor)
      this.processor.connect(this.audioContext.destination)

      this.isCapturing = true

      console.log(
        `[AudioCapture] Started at ${this.config.sampleRate}Hz, ` +
        `chunk size: ${this.config.chunkSize} samples`
      )
    } catch (error) {
      // Clean up on error
      this.cleanup()
      throw error
    }
  }

  /**
   * Stop audio capture and release resources
   */
  stop(): void {
    this.isCapturing = false
    this.cleanup()
    console.log("[AudioCapture] Stopped")
  }

  /**
   * Try to resume suspended AudioContext
   * Called automatically on visibility change or state change
   */
  async tryResume(): Promise<boolean> {
    if (!this.audioContext) {
      console.warn('[AudioCapture] No AudioContext to resume')
      return false
    }

    if (this.audioContext.state === 'running') {
      console.log('[AudioCapture] AudioContext already running')
      return true
    }

    try {
      console.log('[AudioCapture] Attempting to resume AudioContext...')
      await this.audioContext.resume()
      console.log(`[AudioCapture] Resume result - state: ${this.audioContext.state}`)

      if (this.audioContext.state === 'running') {
        console.log('[AudioCapture] AudioContext resumed successfully!')
        this.onStateChange?.('running', true)
        return true
      } else {
        console.warn('[AudioCapture] AudioContext still not running after resume')
        this.onStateChange?.(this.audioContext.state, false)
        return false
      }
    } catch (error) {
      console.error('[AudioCapture] Failed to resume AudioContext:', error)
      this.onStateChange?.('suspended', false)
      return false
    }
  }

  /**
   * Get current AudioContext state
   */
  getState(): AudioContextState | null {
    return this.audioContext?.state ?? null
  }

  /**
   * Check if currently capturing
   */
  get capturing(): boolean {
    return this.isCapturing
  }

  /**
   * Get current configuration
   */
  getConfig(): Required<AudioCaptureConfig> {
    return { ...this.config }
  }

  /**
   * Update configuration (only effective before start)
   */
  updateConfig(config: Partial<AudioCaptureConfig>): void {
    if (this.isCapturing) {
      throw new Error("Cannot update config while capturing")
    }
    this.config = { ...this.config, ...config }
  }

  /**
   * Clean up audio resources
   */
  private cleanup(): void {
    // Remove visibility handler
    if (this.visibilityHandler) {
      document.removeEventListener('visibilitychange', this.visibilityHandler)
      this.visibilityHandler = null
    }

    if (this.processor) {
      this.processor.disconnect()
      this.processor = null
    }

    if (this.source) {
      this.source.disconnect()
      this.source = null
    }

    if (this.audioContext) {
      this.audioContext.onstatechange = null  // Remove state handler
      this.audioContext.close()
      this.audioContext = null
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop())
      this.mediaStream = null
    }
  }
}
