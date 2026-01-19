/**
 * Mock Audio APIs for testing
 *
 * Provides mocks for:
 * - AudioContext (oscillator, gain, etc.)
 * - Audio element (playback)
 * - MediaDevices (getUserMedia)
 * - MediaStream
 */

import { vi } from "vitest"

/**
 * Mock AudioContext with common methods
 */
export class MockAudioContext {
  sampleRate = 16000
  currentTime = 0
  state: AudioContextState = "running"
  destination = {}

  createOscillator = vi.fn(() => ({
    type: "sine" as OscillatorType,
    frequency: {
      value: 440,
      setValueAtTime: vi.fn(),
    },
    connect: vi.fn(),
    start: vi.fn(),
    stop: vi.fn(),
    onended: null as (() => void) | null,
  }))

  createGain = vi.fn(() => ({
    gain: {
      value: 1,
      setValueAtTime: vi.fn(),
      linearRampToValueAtTime: vi.fn(),
    },
    connect: vi.fn(),
  }))

  createMediaStreamSource = vi.fn(() => ({
    connect: vi.fn(),
    disconnect: vi.fn(),
  }))

  createScriptProcessor = vi.fn((bufferSize: number) => ({
    bufferSize,
    connect: vi.fn(),
    disconnect: vi.fn(),
    onaudioprocess: null as ((event: AudioProcessingEvent) => void) | null,
  }))

  createAnalyser = vi.fn(() => ({
    fftSize: 2048,
    frequencyBinCount: 1024,
    getByteFrequencyData: vi.fn(),
    getFloatTimeDomainData: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
  }))

  close = vi.fn().mockResolvedValue(undefined)
  suspend = vi.fn().mockResolvedValue(undefined)
  resume = vi.fn().mockResolvedValue(undefined)
}

/**
 * Mock Audio element for playback
 */
export class MockAudio {
  src = ""
  currentTime = 0
  duration = 0
  paused = true
  volume = 1
  muted = false

  onended: (() => void) | null = null
  onerror: ((e: unknown) => void) | null = null
  oncanplay: (() => void) | null = null
  onloadeddata: (() => void) | null = null

  play = vi.fn().mockImplementation(() => {
    this.paused = false
    return Promise.resolve()
  })

  pause = vi.fn().mockImplementation(() => {
    this.paused = true
  })

  load = vi.fn()

  // Helper to simulate playback completion
  simulateEnded(): void {
    this.paused = true
    this.onended?.()
  }

  // Helper to simulate error
  simulateError(error: Error): void {
    this.onerror?.(error)
  }
}

/**
 * Mock MediaStream
 */
export class MockMediaStream {
  id = "mock-stream-id"
  active = true

  private tracks: { stop: ReturnType<typeof vi.fn>; kind: string }[] = [
    { stop: vi.fn(), kind: "audio" },
  ]

  getTracks = vi.fn(() => this.tracks)
  getAudioTracks = vi.fn(() => this.tracks.filter((t) => t.kind === "audio"))
  getVideoTracks = vi.fn(() => this.tracks.filter((t) => t.kind === "video"))

  addTrack = vi.fn((track) => {
    this.tracks.push(track)
  })

  removeTrack = vi.fn((track) => {
    const index = this.tracks.indexOf(track)
    if (index > -1) this.tracks.splice(index, 1)
  })
}

/**
 * Mock navigator.mediaDevices
 */
export const mockMediaDevices = {
  getUserMedia: vi.fn().mockResolvedValue(new MockMediaStream()),
  enumerateDevices: vi.fn().mockResolvedValue([
    { kind: "audioinput", deviceId: "default", label: "Default Microphone" },
  ]),
}

/**
 * Install all audio mocks globally
 */
export function installAudioMocks(): void {
  global.AudioContext = MockAudioContext as unknown as typeof AudioContext
  global.Audio = MockAudio as unknown as typeof Audio
  Object.defineProperty(navigator, "mediaDevices", {
    value: mockMediaDevices,
    writable: true,
  })
}

/**
 * Create audio data for testing
 */
export function createMockAudioData(
  length = 1024,
  amplitude = 0.5
): { float32: Float32Array; int16: Int16Array } {
  const float32 = new Float32Array(length)
  const int16 = new Int16Array(length)

  for (let i = 0; i < length; i++) {
    // Generate a sine wave
    const sample = Math.sin((2 * Math.PI * 440 * i) / 16000) * amplitude
    float32[i] = sample
    int16[i] = Math.round(sample * 32767)
  }

  return { float32, int16 }
}

/**
 * Create silent audio data (for silence detection tests)
 */
export function createSilentAudioData(length = 1024): Float32Array {
  return new Float32Array(length).fill(0)
}

/**
 * Create loud audio data (for speech detection tests)
 */
export function createLoudAudioData(length = 1024, amplitude = 0.8): Float32Array {
  const data = new Float32Array(length)
  for (let i = 0; i < length; i++) {
    data[i] = Math.sin((2 * Math.PI * 440 * i) / 16000) * amplitude
  }
  return data
}
