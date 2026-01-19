/**
 * Voice notifications for recording on/off
 * Uses pre-recorded audio files instead of generating on-the-fly
 */

// Audio element cache to avoid creating new elements every time
let onAudio: HTMLAudioElement | null = null
let offAudio: HTMLAudioElement | null = null

/**
 * Play voice notification from pre-recorded audio file
 * @param type - 'start' for recording start ("on"), 'stop' for recording stop ("off")
 */
export function playNotificationSound(type: 'start' | 'stop'): void {
  try {
    if (typeof window === 'undefined') {
      console.warn('[Notification] Not in browser environment')
      return
    }

    // Initialize audio elements once
    if (!onAudio) {
      onAudio = new Audio('/sounds/on.mp3')
      onAudio.volume = 0.8
    }
    if (!offAudio) {
      offAudio = new Audio('/sounds/off.mp3')
      offAudio.volume = 0.8
    }

    // Play the appropriate audio
    const audio = type === 'start' ? onAudio : offAudio

    // Reset to start and play
    audio.currentTime = 0
    audio.play().catch(error => {
      console.error(`[Notification] Error playing ${type} sound:`, error)
    })

    console.log(`[Notification] Playing ${type} sound from audio file`)
  } catch (error) {
    console.error('[Notification] Error setting up audio:', error)
  }
}
