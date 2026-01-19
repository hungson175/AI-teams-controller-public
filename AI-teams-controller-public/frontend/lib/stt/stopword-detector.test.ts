/**
 * Stop Word Detector Tests
 *
 * Tests for trigger-based speech detection using configurable stop words.
 * Pure logic tests - no browser APIs needed.
 */

import { describe, it, expect, beforeEach, vi } from "vitest"
import {
  StopWordDetector,
  DEFAULT_STOPWORD_CONFIG,
  getStopWord,
  setStopWord,
  STOPWORD_STORAGE_KEY,
} from "./stopword-detector"

describe("StopWordDetector", () => {
  let detector: StopWordDetector

  beforeEach(() => {
    detector = new StopWordDetector()
  })

  describe("stop word detection", () => {
    it("detects default stop word 'thank you'", () => {
      const result = detector.processTranscript("fix the login bug thank you")

      expect(result.detected).toBe(true)
      expect(result.command).toBe("fix the login bug")
    })

    it("does not detect partial stop word", () => {
      const result = detector.processTranscript("go to the login page")

      expect(result.detected).toBe(false)
      expect(result.command).toBe("go to the login page")
    })

    it("does not detect stop word in middle of text", () => {
      const result = detector.processTranscript("thank you and then do something else")

      expect(result.detected).toBe(false)
    })

    it("handles stop word with extra spaces", () => {
      const result = detector.processTranscript("fix bug   thank   you")

      expect(result.detected).toBe(true)
      expect(result.command).toBe("fix bug")
    })
  })

  describe("case insensitivity", () => {
    it("detects stop word regardless of case", () => {
      const result1 = detector.processTranscript("fix bug THANK YOU")
      const result2 = detector.processTranscript("fix bug Thank You")
      const result3 = detector.processTranscript("fix bug THANK you")

      expect(result1.detected).toBe(true)
      expect(result2.detected).toBe(true)
      expect(result3.detected).toBe(true)
    })

    it("respects case sensitivity when enabled", () => {
      const caseSensitive = new StopWordDetector({
        stopWord: "THANK YOU",
        caseSensitive: true,
      })

      const result1 = caseSensitive.processTranscript("fix bug THANK YOU")
      const result2 = caseSensitive.processTranscript("fix bug thank you")

      expect(result1.detected).toBe(true)
      expect(result2.detected).toBe(false)
    })
  })

  describe("punctuation handling", () => {
    it("detects stop word with punctuation", () => {
      const result1 = detector.processTranscript("fix bug, thank you!")
      const result2 = detector.processTranscript("fix bug. thank you?")

      expect(result1.detected).toBe(true)
      expect(result2.detected).toBe(true)
    })

    it("preserves command punctuation", () => {
      const result = detector.processTranscript("Hello, world! thank you")

      expect(result.detected).toBe(true)
      // Command should preserve original punctuation where possible
      expect(result.command).toContain("Hello")
    })
  })

  describe("custom stop words", () => {
    it("works with custom single-word stop word", () => {
      const customDetector = new StopWordDetector({ stopWord: "send" })
      const result = customDetector.processTranscript("fix the login bug send")

      expect(result.detected).toBe(true)
      expect(result.command).toBe("fix the login bug")
    })

    it("works with custom multi-word stop word", () => {
      const customDetector = new StopWordDetector({ stopWord: "send now please" })
      const result = customDetector.processTranscript("fix bug send now please")

      expect(result.detected).toBe(true)
      expect(result.command).toBe("fix bug")
    })

    it("can update stop word after creation", () => {
      detector.setStopWord("execute")
      const result = detector.processTranscript("run the tests execute")

      expect(result.detected).toBe(true)
      expect(result.command).toBe("run the tests")
    })
  })

  describe("normalization", () => {
    it("normalizes whitespace correctly", () => {
      const result = detector.normalize("  hello   world  ")
      expect(result).toBe("hello world")
    })

    it("removes punctuation for comparison", () => {
      const result = detector.normalize("hello, world!")
      expect(result).toBe("hello world")
    })

    it("converts to lowercase when not case-sensitive", () => {
      const result = detector.normalize("HELLO World")
      expect(result).toBe("hello world")
    })
  })

  describe("strip stop word", () => {
    it("removes stop word from end of transcript", () => {
      const result = detector.stripStopWord("fix the bug thank you")
      expect(result).toBe("fix the bug")
    })

    it("returns original text if stop word not at end", () => {
      const result = detector.stripStopWord("thank you fix the bug")
      expect(result).toBe("thank you fix the bug")
    })

    it("handles trailing whitespace", () => {
      const result = detector.stripStopWord("fix the bug thank you   ")
      expect(result).toBe("fix the bug")
    })
  })

  describe("configuration", () => {
    it("uses default config", () => {
      const config = detector.getConfig()
      expect(config.stopWord).toBe("thank you")
      expect(config.caseSensitive).toBe(false)
    })

    it("updates config correctly", () => {
      detector.updateConfig({ stopWord: "done" })
      const config = detector.getConfig()
      expect(config.stopWord).toBe("done")
    })
  })

  describe("result structure", () => {
    it("returns correct result structure when detected", () => {
      const result = detector.processTranscript("test thank you")

      expect(result).toHaveProperty("detected", true)
      expect(result).toHaveProperty("command")
      expect(result).toHaveProperty("originalTranscript", "test thank you")
    })

    it("returns correct result structure when not detected", () => {
      const result = detector.processTranscript("just a test")

      expect(result).toHaveProperty("detected", false)
      expect(result).toHaveProperty("command", "just a test")
      expect(result).toHaveProperty("originalTranscript", "just a test")
    })
  })

  describe("edge cases", () => {
    it("handles empty transcript", () => {
      const result = detector.processTranscript("")

      expect(result.detected).toBe(false)
      expect(result.command).toBe("")
    })

    it("handles transcript that is only stop word", () => {
      const result = detector.processTranscript("thank you")

      expect(result.detected).toBe(true)
      expect(result.command).toBe("")
    })

    it("handles very long transcript", () => {
      const longText = "a ".repeat(1000) + "thank you"
      const result = detector.processTranscript(longText)

      expect(result.detected).toBe(true)
    })

    it("handles special characters in command", () => {
      const result = detector.processTranscript("fix bug #123 @user thank you")

      expect(result.detected).toBe(true)
      expect(result.command).toContain("#123")
    })
  })
})

describe("localStorage integration", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  it("returns default stop word when localStorage is empty", () => {
    const result = getStopWord()
    expect(result).toBe(DEFAULT_STOPWORD_CONFIG.stopWord)
  })

  it("saves stop word to localStorage", () => {
    setStopWord("custom word")
    expect(localStorage.getItem(STOPWORD_STORAGE_KEY)).toBe("custom word")
  })

  it("retrieves stop word from localStorage", () => {
    localStorage.setItem(STOPWORD_STORAGE_KEY, "saved word")
    const result = getStopWord()
    expect(result).toBe("saved word")
  })
})
