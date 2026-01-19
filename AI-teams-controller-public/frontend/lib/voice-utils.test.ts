import { describe, it, expect } from 'vitest'
import { float32ToPcm16Base64, base64ToAudioBlob } from './voice-utils'

describe('float32ToPcm16Base64', () => {
  it('should convert Float32Array to base64 string', () => {
    const input = new Float32Array([0, 0.5, -0.5, 1, -1])
    const result = float32ToPcm16Base64(input)
    expect(typeof result).toBe('string')
    expect(result.length).toBeGreaterThan(0)
  })

  it('should clamp values outside [-1, 1]', () => {
    const input = new Float32Array([2, -2]) // Out of range
    const result = float32ToPcm16Base64(input)
    expect(typeof result).toBe('string')
    // Should not throw
  })

  it('should handle empty array', () => {
    const input = new Float32Array([])
    const result = float32ToPcm16Base64(input)
    expect(result).toBe('')
  })

  it('should handle silence (all zeros)', () => {
    const input = new Float32Array([0, 0, 0, 0])
    const result = float32ToPcm16Base64(input)
    expect(typeof result).toBe('string')
  })
})

describe('base64ToAudioBlob', () => {
  it('should convert base64 string to Blob', () => {
    const base64 = btoa('test audio data')
    const blob = base64ToAudioBlob(base64)
    expect(blob).toBeInstanceOf(Blob)
    expect(blob.type).toBe('audio/mp3')
  })

  it('should handle empty base64', () => {
    const blob = base64ToAudioBlob(btoa(''))
    expect(blob).toBeInstanceOf(Blob)
    expect(blob.size).toBe(0)
  })
})
