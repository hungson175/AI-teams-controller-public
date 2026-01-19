import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock AudioContext
class MockAudioContext {
  sampleRate = 24000
  state = 'running'
  createMediaStreamSource = vi.fn().mockReturnValue({
    connect: vi.fn(),
    disconnect: vi.fn(),
  })
  createScriptProcessor = vi.fn().mockReturnValue({
    connect: vi.fn(),
    disconnect: vi.fn(),
    onaudioprocess: null,
  })
  close = vi.fn()
  destination = {}
}

global.AudioContext = MockAudioContext as unknown as typeof AudioContext

// Mock navigator.mediaDevices
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: vi.fn().mockResolvedValue({
      getTracks: () => [{ stop: vi.fn() }],
    }),
  },
})

// Mock Audio
class MockAudio {
  src = ''
  onended: (() => void) | null = null
  onerror: ((e: unknown) => void) | null = null
  play = vi.fn().mockResolvedValue(undefined)
  pause = vi.fn()
}

global.Audio = MockAudio as unknown as typeof Audio

// Mock URL.createObjectURL and revokeObjectURL
global.URL.createObjectURL = vi.fn().mockReturnValue('blob:mock-url')
global.URL.revokeObjectURL = vi.fn()

// Mock btoa/atob
global.btoa = vi.fn((str) => Buffer.from(str).toString('base64'))
global.atob = vi.fn((str) => Buffer.from(str, 'base64').toString())
