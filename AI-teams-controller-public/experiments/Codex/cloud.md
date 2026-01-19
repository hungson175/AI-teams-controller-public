# Mobile Wake Lock Notes

- The web app uses the Wake Lock API in `frontend/hooks/useVoiceRecorder.ts` to keep the screen awake while recording. It requests a screen wake lock on `startRecording`, releases it on stop, and re-acquires if the tab becomes visible again.
- Constraints: wake lock only works while the page is visible and in the foreground; if the screen is turned off/locked or the browser background-suspends the tab, microphone capture stops. There is no background recording on mobile Chrome when the screen is off.
- Practical guidance: keep the screen on during recording; if you need uninterrupted capture on mobile, avoid locking the device. A native app would be required for true background audio capture.
