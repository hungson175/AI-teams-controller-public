/**
 * Silence Detector - Client-Side Speech Detection
 *
 * Implements DetectionStrategy using RMS-based silence detection.
 * Detects speech/silence locally without server round-trips.
 *
 * Algorithm:
 * 1. Calculate RMS (Root Mean Square) of audio chunk
 * 2. Convert to dB scale
 * 3. Compare against threshold to determine speech/silence
 * 4. Track duration of speech and silence
 * 5. Trigger send after configured silence duration (if speech was detected)
 */

import {
  DetectionStrategy,
  DetectionResult,
  DetectionConfig,
  DEFAULT_DETECTION_CONFIG,
} from "./detection-strategy"

/**
 * Internal state for the silence detector
 */
interface DetectorState {
  /** Whether currently in speech segment */
  isSpeaking: boolean
  /** Timestamp when speech started (ms) */
  speechStartTime: number | null
  /** Timestamp when silence started (ms) */
  silenceStartTime: number | null
  /** Total speech duration in current segment (ms) */
  speechDurationMs: number
  /** Current silence duration (ms) */
  silenceDurationMs: number
  /** Whether we've had valid speech (meets minSpeechMs) */
  hasValidSpeech: boolean
}

/**
 * Silence Detector Class
 *
 * Client-side implementation of speech detection using
 * RMS-based audio level analysis.
 */
export class SilenceDetector implements DetectionStrategy {
  readonly name = "silence-detector"

  private config: DetectionConfig
  private state: DetectorState
  private lastProcessTime: number

  constructor(config: Partial<DetectionConfig> = {}) {
    this.config = { ...DEFAULT_DETECTION_CONFIG, ...config }
    this.state = this.createInitialState()
    this.lastProcessTime = Date.now()
  }

  /**
   * Create initial detector state
   */
  private createInitialState(): DetectorState {
    return {
      isSpeaking: false,
      speechStartTime: null,
      silenceStartTime: null,
      speechDurationMs: 0,
      silenceDurationMs: 0,
      hasValidSpeech: false,
    }
  }

  /**
   * Calculate RMS (Root Mean Square) of audio samples
   * RMS = sqrt(mean(samples^2))
   *
   * @param audioData - Float32Array of audio samples (-1 to 1)
   * @returns RMS value (0 to 1)
   */
  private calculateRms(audioData: Float32Array): number {
    if (audioData.length === 0) return 0

    let sumSquares = 0
    for (let i = 0; i < audioData.length; i++) {
      sumSquares += audioData[i] * audioData[i]
    }

    return Math.sqrt(sumSquares / audioData.length)
  }

  /**
   * Convert RMS to decibels (dB)
   * dB = 20 * log10(rms)
   *
   * @param rms - RMS value (0 to 1)
   * @returns dB value (typically -60 to 0)
   */
  calculateRmsDb(rms: number): number {
    // Prevent log(0) by using a minimum value
    const minRms = 1e-10
    const clampedRms = Math.max(rms, minRms)
    return 20 * Math.log10(clampedRms)
  }

  /**
   * Process an audio chunk and determine speech/silence state
   *
   * @param audioData - Float32Array of audio samples
   * @param sampleRate - Sample rate (used for timing calculations)
   * @returns Detection result
   */
  processAudioChunk(audioData: Float32Array, sampleRate: number): DetectionResult {
    const now = Date.now()
    const elapsedMs = now - this.lastProcessTime
    this.lastProcessTime = now

    // Calculate audio level
    const rms = this.calculateRms(audioData)
    const levelDb = this.calculateRmsDb(rms)

    // Determine if this chunk is speech or silence
    const isSpeechChunk = levelDb > this.config.thresholdDb

    // Update state based on speech detection
    if (isSpeechChunk) {
      // Speech detected
      if (!this.state.isSpeaking) {
        // Transition: silence -> speech
        this.state.isSpeaking = true
        this.state.speechStartTime = now
        this.state.silenceStartTime = null
        this.state.silenceDurationMs = 0
      }

      // Update speech duration
      if (this.state.speechStartTime) {
        this.state.speechDurationMs = now - this.state.speechStartTime
      }

      // Check if we've met minimum speech threshold
      if (this.state.speechDurationMs >= this.config.minSpeechMs) {
        this.state.hasValidSpeech = true
      }
    } else {
      // Silence detected
      if (this.state.isSpeaking) {
        // Transition: speech -> silence
        this.state.isSpeaking = false
        this.state.silenceStartTime = now
      }

      // Update silence duration
      if (this.state.silenceStartTime) {
        this.state.silenceDurationMs = now - this.state.silenceStartTime
      }
    }

    // Determine if we should send (silence threshold reached after valid speech)
    const shouldSend =
      this.state.hasValidSpeech &&
      !this.state.isSpeaking &&
      this.state.silenceDurationMs >= this.config.silenceDurationMs

    return {
      isSpeech: isSpeechChunk,
      shouldSend,
      levelDb,
      speechDurationMs: this.state.speechDurationMs,
      silenceDurationMs: this.state.silenceDurationMs,
    }
  }

  /**
   * Reset detector state (call after sending a command)
   */
  reset(): void {
    this.state = this.createInitialState()
    this.lastProcessTime = Date.now()
  }

  /**
   * Get current configuration
   */
  getConfig(): DetectionConfig {
    return { ...this.config }
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<DetectionConfig>): void {
    this.config = { ...this.config, ...config }
  }

  /**
   * Update threshold dynamically (for settings changes)
   * Convenience method for real-time noise filter updates
   */
  updateThreshold(thresholdDb: number): void {
    this.config.thresholdDb = thresholdDb
    console.log("[SilenceDetector] Threshold updated:", thresholdDb, "dB")
  }

  /**
   * Get current state (for debugging/UI)
   */
  getState(): Readonly<DetectorState> {
    return { ...this.state }
  }
}
