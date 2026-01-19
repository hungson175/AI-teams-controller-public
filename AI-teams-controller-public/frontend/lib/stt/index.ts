/**
 * STT (Speech-to-Text) Module
 *
 * Exports detection strategies and utilities for voice input processing.
 */

// Detection strategy interface and types
export type {
  DetectionStrategy,
  DetectionResult,
  DetectionConfig,
} from "./detection-strategy"

export { DEFAULT_DETECTION_CONFIG } from "./detection-strategy"

// Silence detector implementation
export { SilenceDetector } from "./silence-detector"

// Stop word detector
export type { StopWordResult, StopWordConfig } from "./stopword-detector"
export {
  StopWordDetector,
  DEFAULT_STOPWORD_CONFIG,
  STOPWORD_STORAGE_KEY,
  getStopWord,
  setStopWord,
} from "./stopword-detector"

// Audio capture
export type { AudioCaptureConfig, AudioChunkCallback } from "./audio-capture"
export { AudioCapture, DEFAULT_AUDIO_CAPTURE_CONFIG } from "./audio-capture"

// Soniox STT service
export type {
  SonioxDetectionMode,
  SonioxServiceConfig,
  SonioxServiceCallbacks,
} from "./soniox-service"
export { SonioxSTTService, DEFAULT_SONIOX_SERVICE_CONFIG } from "./soniox-service"
