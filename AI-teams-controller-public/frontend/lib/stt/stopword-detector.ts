/**
 * Stop Word Detector - Trigger-Based Speech Detection
 *
 * Detects when a transcript ends with a configurable stop word/phrase.
 *
 * Example: User says "fix the login bug thank you"
 * - Detects "thank you" at the end
 * - Returns command: "fix the login bug"
 */

/**
 * Result from processing a transcript
 */
export interface StopWordResult {
  /** Whether the stop word was detected */
  detected: boolean
  /** The command text (transcript with stop word removed) */
  command: string
  /** The original transcript */
  originalTranscript: string
}

/**
 * Stop Word Detector Configuration
 */
export interface StopWordConfig {
  /** The stop word/phrase to detect (default: "thank you") */
  stopWord: string
  /** Whether detection is case-sensitive (default: false) */
  caseSensitive: boolean
}

/**
 * Default stop word configuration
 */
export const DEFAULT_STOPWORD_CONFIG: StopWordConfig = {
  stopWord: "thank you",
  caseSensitive: false,
}

/**
 * localStorage key for stop word setting
 */
export const STOPWORD_STORAGE_KEY = "voice-stop-word"

/**
 * Get stop word from localStorage
 */
export const getStopWord = (): string => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem(STOPWORD_STORAGE_KEY)
    if (stored) {
      return stored
    }
  }
  return DEFAULT_STOPWORD_CONFIG.stopWord
}

/**
 * Set stop word to localStorage
 */
export const setStopWord = (stopWord: string): void => {
  if (typeof window !== "undefined") {
    localStorage.setItem(STOPWORD_STORAGE_KEY, stopWord)
  }
}

/**
 * Stop Word Detector Class
 *
 * Detects trigger phrases at the end of transcripts.
 */
export class StopWordDetector {
  private config: StopWordConfig

  constructor(config: Partial<StopWordConfig> = {}) {
    this.config = { ...DEFAULT_STOPWORD_CONFIG, ...config }
  }

  /**
   * Normalize text for comparison
   * - Removes punctuation
   * - Converts to lowercase (if not case-sensitive)
   * - Trims whitespace
   * - Collapses multiple spaces
   *
   * @param text - Text to normalize
   * @returns Normalized text
   */
  normalize(text: string): string {
    let normalized = text
      // Remove common punctuation
      .replace(/[.,!?;:'"()\[\]{}]/g, "")
      // Collapse multiple spaces
      .replace(/\s+/g, " ")
      // Trim
      .trim()

    if (!this.config.caseSensitive) {
      normalized = normalized.toLowerCase()
    }

    return normalized
  }

  /**
   * Check if transcript ends with the stop word
   *
   * @param transcript - The full transcript to check
   * @returns StopWordResult with detection status and cleaned command
   */
  processTranscript(transcript: string): StopWordResult {
    const normalizedTranscript = this.normalize(transcript)
    const normalizedStopWord = this.normalize(this.config.stopWord)

    const detected = normalizedTranscript.endsWith(normalizedStopWord)

    let command = transcript.trim()
    if (detected) {
      command = this.stripStopWord(transcript)
    }

    return {
      detected,
      command,
      originalTranscript: transcript,
    }
  }

  /**
   * Remove stop word from the end of transcript
   * Preserves original casing of the command portion
   *
   * @param transcript - The transcript containing the stop word
   * @returns The command without the stop word
   */
  stripStopWord(transcript: string): string {
    const normalizedTranscript = this.normalize(transcript)
    const normalizedStopWord = this.normalize(this.config.stopWord)

    if (!normalizedTranscript.endsWith(normalizedStopWord)) {
      return transcript.trim()
    }

    // Find where the stop word starts in the normalized version
    const stopWordStartIndex = normalizedTranscript.length - normalizedStopWord.length

    // Map back to original transcript
    // Count characters in original that map to normalized positions
    let origIndex = 0
    let normCount = 0
    const origTrimmed = transcript.trim()

    for (let i = 0; i < origTrimmed.length && normCount < stopWordStartIndex; i++) {
      const char = origTrimmed[i]
      // Check if this character would be kept in normalization
      if (!/[.,!?;:'"()\[\]{}]/.test(char)) {
        if (char === " ") {
          // Only count if not collapsing multiple spaces
          if (i === 0 || origTrimmed[i - 1] !== " ") {
            normCount++
          }
        } else {
          normCount++
        }
      }
      origIndex = i + 1
    }

    // Extract command portion and trim
    return origTrimmed.substring(0, origIndex).trim()
  }

  /**
   * Get current configuration
   */
  getConfig(): StopWordConfig {
    return { ...this.config }
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<StopWordConfig>): void {
    this.config = { ...this.config, ...config }
  }

  /**
   * Update stop word (convenience method)
   */
  setStopWord(stopWord: string): void {
    this.config.stopWord = stopWord
  }

  /**
   * Reset detector state
   * Called when transcript is cleared to start fresh
   */
  reset(): void {
    // StopWordDetector is stateless (only processes current transcript)
    // This method exists for API compatibility with soniox-service.ts
    // No internal state to reset
  }
}
