# Headphone Button Voice Input Control - Research & Demo

## Research Summary

### Goal
Control voice input toggle via Bluetooth headphone hardware button (play/pause).

### Approach Comparison

| Approach | Viability | Notes |
|----------|-----------|-------|
| **Media Session API** | **Recommended** | Works with headphone buttons via play/pause handlers |
| Web Bluetooth API | **Not viable** | Only supports BLE devices, not headphones (Bluetooth Classic) |
| Bluetooth HID | **Not viable** | Not available in web browsers |

### Media Session API - Key Findings

**How it works:**
1. Browser's Media Session API captures hardware media key events
2. Headphone buttons send play/pause signals via Bluetooth AVRCP profile
3. Browser routes these to registered `mediaSession.setActionHandler()` callbacks

**Critical Requirement: Active Audio**
- Browsers intentionally require active audio playback for Media Session to work
- Chrome requires minimum 5 seconds of audio to show media controls
- **Workaround:** Play nearly-silent audio to keep session active

**Silent Audio Workaround:**
```javascript
// Create nearly-silent audio element
const audio = new Audio('silent.wav');
audio.loop = true;
audio.volume = 0.01; // Nearly silent but not zero

// Start playing to activate media session
await audio.play();

// Now handlers will receive headphone button events
navigator.mediaSession.setActionHandler('play', () => { ... });
navigator.mediaSession.setActionHandler('pause', () => { ... });
```

**Firefox Quirk:**
- Volume cannot be exactly 0 (silent audio doesn't work)
- Requires actual audio content at very low volume (~0.01)

### Available Action Handlers

| Action | Use Case |
|--------|----------|
| `play` | Resume voice recording |
| `pause` | Stop voice recording |
| `togglemicrophone` | Toggle mic state (video conferencing) |
| `stop` | Full stop |

### Browser Support

| Browser | Support |
|---------|---------|
| Chrome | Full |
| Edge | Full |
| Opera | Full |
| Android Chrome | Full |
| Firefox | Partial (needs non-silent audio) |
| Safari | Limited |

## Demo Usage

### How to Test

1. **Serve the demo** (HTTPS or localhost required for some features):
   ```bash
   cd frontend/experiments/headphone-button-demo
   python3 -m http.server 8080
   # Open http://localhost:8080
   ```

2. **Connect Bluetooth headphones** to your device

3. **Click "Initialize Media Session"** button in the demo

4. **Press play/pause button** on your headphones

5. **Watch the indicator toggle** and check console for events

### What to Observe

- Mic indicator should toggle between ON (red, pulsing) and OFF (gray)
- Button press count increments
- Event log shows "Play action received" or "Pause action received"

## Integration Considerations

### For Voice Input Toggle

```javascript
// In useVoiceRecorder.ts or similar
function initHeadphoneControl() {
  // Create silent audio for session activation
  const silentAudio = new Audio('silent.wav');
  silentAudio.loop = true;
  silentAudio.volume = 0.01;

  // Set up handlers
  navigator.mediaSession.setActionHandler('play', () => {
    if (!isRecording) startRecording();
  });

  navigator.mediaSession.setActionHandler('pause', () => {
    if (isRecording) stopRecording();
  });

  // Activate session
  silentAudio.play();
}
```

### Mobile Considerations

1. **AudioContext suspension** - Must handle `audioContext.onstatechange` and resume when suspended
2. **Visibility changes** - Resume audio when tab becomes visible
3. **Wake Lock** - Already implemented in project, keeps screen on during recording

### Potential Issues

1. **Other apps competing** - If Spotify/YouTube is playing, they may capture button events
2. **Audio focus** - Browser may lose focus to other audio sources
3. **Bluetooth reconnection** - May need to reinitialize after headphones reconnect

## Files

- `index.html` - Complete working demo with visual UI
- `README.md` - This documentation

## Sources

- [MDN - MediaSession setActionHandler](https://developer.mozilla.org/en-US/docs/Web/API/MediaSession/setActionHandler)
- [MDN - Media Session API](https://developer.mozilla.org/en-US/docs/Web/API/Media_Session_API)
- [web.dev - Media Session API](https://web.dev/media-session/)
- [Can I Use - Web Bluetooth](https://caniuse.com/web-bluetooth)
- [GitHub - w3c/mediasession Issue #244](https://github.com/w3c/mediasession/issues/244)
