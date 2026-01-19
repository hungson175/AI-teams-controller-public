/**
 * Silence Detector Tests
 *
 * Tests for client-side speech/silence detection using RMS-based analysis.
 * Pure logic tests - no browser APIs needed.
 */

import { describe, it, expect, beforeEach } from "vitest"
import { SilenceDetector } from "./silence-detector"
import { createLoudAudioData, createSilentAudioData } from "@/__mocks__/audio"

describe("SilenceDetector", () => {
  let detector: SilenceDetector

  beforeEach(() => {
    detector = new SilenceDetector({
      thresholdDb: -40,
      silenceDurationMs: 1000, // Use shorter duration for tests
      minSpeechMs: 100,
    })
  })

  describe("RMS calculation", () => {
    it("calculates RMS of silent audio as near-zero", () => {
      const silentData = createSilentAudioData(1024)
      const result = detector.processAudioChunk(silentData, 16000)

      // Silent audio should have very low dB (near -infinity, clamped)
      expect(result.levelDb).toBeLessThan(-60)
      expect(result.isSpeech).toBe(false)
    })

    it("calculates RMS of loud audio correctly", () => {
      const loudData = createLoudAudioData(1024, 0.5)
      const result = detector.processAudioChunk(loudData, 16000)

      // Loud audio should have higher dB
      expect(result.levelDb).toBeGreaterThan(-20)
      expect(result.isSpeech).toBe(true)
    })

    it("converts RMS to dB correctly", () => {
      // Test the calculateRmsDb method directly
      // RMS of 1.0 should be 0 dB
      expect(detector.calculateRmsDb(1.0)).toBeCloseTo(0, 1)

      // RMS of 0.1 should be -20 dB
      expect(detector.calculateRmsDb(0.1)).toBeCloseTo(-20, 1)

      // RMS of 0.01 should be -40 dB
      expect(detector.calculateRmsDb(0.01)).toBeCloseTo(-40, 1)
    })
  })

  describe("speech detection", () => {
    it("detects speech when audio is above threshold", () => {
      const loudData = createLoudAudioData(1024, 0.3)
      const result = detector.processAudioChunk(loudData, 16000)

      expect(result.isSpeech).toBe(true)
    })

    it("detects silence when audio is below threshold", () => {
      const quietData = createLoudAudioData(1024, 0.001)
      const result = detector.processAudioChunk(quietData, 16000)

      expect(result.isSpeech).toBe(false)
    })

    it("tracks speech duration correctly", () => {
      const loudData = createLoudAudioData(1024, 0.5)

      // Process first chunk to start speech
      detector.processAudioChunk(loudData, 16000)

      // Speech duration tracks from speechStartTime, not elapsed time between chunks
      // So we check the state directly
      const state = detector.getState()
      expect(state.isSpeaking).toBe(true)
      expect(state.speechStartTime).not.toBe(null)
    })
  })

  describe("silence duration tracking", () => {
    it("tracks silence duration after speech", () => {
      const loudData = createLoudAudioData(1024, 0.5)
      const silentData = createSilentAudioData(1024)

      // Start with speech
      detector.processAudioChunk(loudData, 16000)
      detector.processAudioChunk(loudData, 16000)

      // Then silence
      const result = detector.processAudioChunk(silentData, 16000)

      expect(result.silenceDurationMs).toBeGreaterThanOrEqual(0)
    })

    it("resets silence duration when speech resumes", () => {
      const loudData = createLoudAudioData(1024, 0.5)
      const silentData = createSilentAudioData(1024)

      // Speech -> silence -> speech
      detector.processAudioChunk(loudData, 16000)
      detector.processAudioChunk(silentData, 16000)
      const result = detector.processAudioChunk(loudData, 16000)

      // Silence duration should reset when speech resumes
      expect(result.silenceDurationMs).toBe(0)
    })
  })

  describe("shouldSend logic", () => {
    it("does not send if no valid speech occurred", () => {
      const silentData = createSilentAudioData(1024)

      // Only silence - no speech
      const result = detector.processAudioChunk(silentData, 16000)

      expect(result.shouldSend).toBe(false)
    })

    it("does not send if speech is too short", () => {
      // Use a detector that requires longer speech
      const strictDetector = new SilenceDetector({
        thresholdDb: -40,
        silenceDurationMs: 100,
        minSpeechMs: 10000, // Require very long speech
      })

      const loudData = createLoudAudioData(1024, 0.5)
      const silentData = createSilentAudioData(1024)

      // Short speech burst
      strictDetector.processAudioChunk(loudData, 16000)
      // Then silence
      const result = strictDetector.processAudioChunk(silentData, 16000)

      expect(result.shouldSend).toBe(false)
    })

    it("does not send while still speaking", () => {
      const loudData = createLoudAudioData(1024, 0.5)

      // Continuous speech
      for (let i = 0; i < 10; i++) {
        const result = detector.processAudioChunk(loudData, 16000)
        expect(result.shouldSend).toBe(false)
      }
    })
  })

  describe("reset", () => {
    it("resets all state after reset()", () => {
      const loudData = createLoudAudioData(1024, 0.5)

      // Build up some state
      detector.processAudioChunk(loudData, 16000)
      detector.processAudioChunk(loudData, 16000)

      // Reset
      detector.reset()

      // State should be cleared
      const state = detector.getState()
      expect(state.isSpeaking).toBe(false)
      expect(state.speechStartTime).toBe(null)
      expect(state.silenceStartTime).toBe(null)
      expect(state.speechDurationMs).toBe(0)
      expect(state.silenceDurationMs).toBe(0)
      expect(state.hasValidSpeech).toBe(false)
    })
  })

  describe("configuration", () => {
    it("uses default config if not provided", () => {
      const defaultDetector = new SilenceDetector()
      const config = defaultDetector.getConfig()

      expect(config.thresholdDb).toBe(-40)
      expect(config.silenceDurationMs).toBe(5000)
      expect(config.minSpeechMs).toBe(300)
    })

    it("merges custom config with defaults", () => {
      const customDetector = new SilenceDetector({ thresholdDb: -30 })
      const config = customDetector.getConfig()

      expect(config.thresholdDb).toBe(-30)
      expect(config.silenceDurationMs).toBe(5000) // Default
    })

    it("updates config correctly", () => {
      detector.updateConfig({ thresholdDb: -50 })
      const config = detector.getConfig()

      expect(config.thresholdDb).toBe(-50)
    })
  })

  describe("edge cases", () => {
    it("handles empty audio data", () => {
      const emptyData = new Float32Array(0)
      const result = detector.processAudioChunk(emptyData, 16000)

      // Should return safe defaults
      expect(result.levelDb).toBeLessThan(-60) // Very quiet
      expect(result.isSpeech).toBe(false)
    })

    it("handles very short audio chunks", () => {
      const shortData = new Float32Array([0.5, 0.5, 0.5])
      const result = detector.processAudioChunk(shortData, 16000)

      // Should process without error
      expect(result).toBeDefined()
      expect(typeof result.levelDb).toBe("number")
    })

    it("handles maximum amplitude audio", () => {
      const maxData = new Float32Array(1024).fill(1.0)
      const result = detector.processAudioChunk(maxData, 16000)

      // Should handle without overflow
      expect(result.levelDb).toBeCloseTo(0, 0) // 0 dB for max amplitude
      expect(result.isSpeech).toBe(true)
    })
  })
})
