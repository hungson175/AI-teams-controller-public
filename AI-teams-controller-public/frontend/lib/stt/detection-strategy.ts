/**
 * Detection Strategy Interface
 *
 * Defines the contract for speech/silence detection strategies.
 * Allows swapping between different detection implementations
 * (e.g., client-side silence detection, server VAD, etc.)
 */

/**
 * Result from processing an audio chunk
 */
export interface DetectionResult {
  /** Whether speech was detected in this chunk */
  isSpeech: boolean
  /** Whether silence threshold has been reached (ready to send) */
  shouldSend: boolean
  /** Current audio level in dB (for UI feedback) */
  levelDb: number
  /** Duration of current speech segment in ms */
  speechDurationMs: number
  /** Duration of current silence in ms */
  silenceDurationMs: number
}

/**
 * Configuration for detection strategies
 */
export interface DetectionConfig {
  /** Threshold in dB below which audio is considered silence (default: -40) */
  thresholdDb: number
  /** Duration of silence before triggering send (default: 5000ms) */
  silenceDurationMs: number
  /** Minimum speech duration to consider valid (default: 300ms) */
  minSpeechMs: number
}

/**
 * Detection Strategy Interface
 *
 * Implemented by different detection strategies to allow
 * pluggable speech/silence detection.
 */
export interface DetectionStrategy {
  /** Strategy name for identification */
  readonly name: string

  /**
   * Process an audio chunk and return detection result
   * @param audioData - Float32Array of audio samples (normalized -1 to 1)
   * @param sampleRate - Sample rate of the audio data
   * @returns Detection result with speech/silence state
   */
  processAudioChunk(audioData: Float32Array, sampleRate: number): DetectionResult

  /**
   * Reset the detector state (e.g., after sending a command)
   */
  reset(): void

  /**
   * Get current configuration
   */
  getConfig(): DetectionConfig

  /**
   * Update configuration
   * @param config - Partial configuration to update
   */
  updateConfig(config: Partial<DetectionConfig>): void
}

/**
 * Default detection configuration
 */
export const DEFAULT_DETECTION_CONFIG: DetectionConfig = {
  thresholdDb: -40,
  silenceDurationMs: 5000,
  minSpeechMs: 300,
}
