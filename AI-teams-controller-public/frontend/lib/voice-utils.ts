/**
 * Voice utility functions - extracted for testability
 */

/**
 * Convert Float32 audio to base64 PCM16
 */
export function float32ToPcm16Base64(float32Array: Float32Array): string {
  const int16Array = new Int16Array(float32Array.length)

  for (let i = 0; i < float32Array.length; i++) {
    const s = Math.max(-1, Math.min(1, float32Array[i])) // Clamp
    int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7fff
  }

  // Convert to base64
  const bytes = new Uint8Array(int16Array.buffer)
  let binary = ""
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}

/**
 * Decode base64 MP3 to Blob for audio playback
 */
export function base64ToAudioBlob(base64Audio: string): Blob {
  const binaryString = atob(base64Audio)
  const bytes = new Uint8Array(binaryString.length)
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i)
  }
  return new Blob([bytes], { type: "audio/mp3" })
}
