/**
 * Tests: Voice Speed Setting (TDD)
 *
 * Tests for speech speed configuration:
 * - Default speed should be 0.58 (20% slower than normal)
 * - Speed range: 0.5 - 2.0
 * - localStorage persistence
 * - Speed sent with voice command API requests
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest"
import {
  DEFAULT_SPEECH_SPEED,
  MIN_SPEECH_SPEED,
  MAX_SPEECH_SPEED,
  SPEECH_SPEED_STORAGE_KEY,
  getSpeechSpeed,
  setSpeechSpeed,
} from "../voice-types"

describe("Voice Speed Configuration", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  describe("Constants", () => {
    it("should have default speed of 0.58 (20% slower than normal)", () => {
      expect(DEFAULT_SPEECH_SPEED).toBe(0.58)
    })

    it("should have min speed of 0.5", () => {
      expect(MIN_SPEECH_SPEED).toBe(0.5)
    })

    it("should have max speed of 2.0", () => {
      expect(MAX_SPEECH_SPEED).toBe(2.0)
    })

    it("should use 'speech-speed' as localStorage key", () => {
      expect(SPEECH_SPEED_STORAGE_KEY).toBe("speech-speed")
    })
  })

  describe("getSpeechSpeed", () => {
    it("should return default speed when localStorage is empty", () => {
      const speed = getSpeechSpeed()
      expect(speed).toBe(0.58)
    })

    it("should return stored speed from localStorage", () => {
      localStorage.setItem(SPEECH_SPEED_STORAGE_KEY, "1.2")
      const speed = getSpeechSpeed()
      expect(speed).toBe(1.2)
    })

    it("should return default for invalid values (below min)", () => {
      localStorage.setItem(SPEECH_SPEED_STORAGE_KEY, "0.3")
      const speed = getSpeechSpeed()
      expect(speed).toBe(0.58) // Falls back to default
    })

    it("should return default for invalid values (above max)", () => {
      localStorage.setItem(SPEECH_SPEED_STORAGE_KEY, "3.0")
      const speed = getSpeechSpeed()
      expect(speed).toBe(0.58) // Falls back to default
    })

    it("should return default for non-numeric values", () => {
      localStorage.setItem(SPEECH_SPEED_STORAGE_KEY, "invalid")
      const speed = getSpeechSpeed()
      expect(speed).toBe(0.58) // Falls back to default
    })

    it("should handle edge case: minimum boundary (0.5)", () => {
      localStorage.setItem(SPEECH_SPEED_STORAGE_KEY, "0.5")
      const speed = getSpeechSpeed()
      expect(speed).toBe(0.5)
    })

    it("should handle edge case: maximum boundary (2.0)", () => {
      localStorage.setItem(SPEECH_SPEED_STORAGE_KEY, "2.0")
      const speed = getSpeechSpeed()
      expect(speed).toBe(2.0)
    })
  })

  describe("setSpeechSpeed", () => {
    it("should save speed to localStorage", () => {
      setSpeechSpeed(1.0)
      expect(localStorage.getItem(SPEECH_SPEED_STORAGE_KEY)).toBe("1") // JS toString() drops trailing zero
    })

    it("should clamp values below minimum to 0.5", () => {
      setSpeechSpeed(0.3)
      expect(localStorage.getItem(SPEECH_SPEED_STORAGE_KEY)).toBe("0.5")
    })

    it("should clamp values above maximum to 2.0", () => {
      setSpeechSpeed(3.0)
      expect(localStorage.getItem(SPEECH_SPEED_STORAGE_KEY)).toBe("2") // JS toString() drops trailing zero
    })

    it("should accept minimum boundary (0.5)", () => {
      setSpeechSpeed(0.5)
      expect(localStorage.getItem(SPEECH_SPEED_STORAGE_KEY)).toBe("0.5")
    })

    it("should accept maximum boundary (2.0)", () => {
      setSpeechSpeed(2.0)
      expect(localStorage.getItem(SPEECH_SPEED_STORAGE_KEY)).toBe("2") // JS toString() drops trailing zero
    })

    it("should handle decimal precision", () => {
      setSpeechSpeed(0.75)
      expect(localStorage.getItem(SPEECH_SPEED_STORAGE_KEY)).toBe("0.75")
    })

    it("should round-trip: set and get", () => {
      setSpeechSpeed(1.5)
      expect(getSpeechSpeed()).toBe(1.5)
    })
  })

  describe("Speed Range Validation", () => {
    it("should support 0.5x (slowest)", () => {
      setSpeechSpeed(0.5)
      expect(getSpeechSpeed()).toBe(0.5)
    })

    it("should support 1.0x (normal speed)", () => {
      setSpeechSpeed(1.0)
      expect(getSpeechSpeed()).toBe(1.0)
    })

    it("should support 2.0x (fastest)", () => {
      setSpeechSpeed(2.0)
      expect(getSpeechSpeed()).toBe(2.0)
    })

    it("should support 0.58 (default, slightly slow)", () => {
      setSpeechSpeed(0.58)
      expect(getSpeechSpeed()).toBe(0.58)
    })
  })
})
