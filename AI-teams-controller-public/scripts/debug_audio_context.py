#!/usr/bin/env python3
"""
Debug AudioContext state on mobile - check if it gets suspended.
Monitors console logs for AudioContext state changes.
"""

import time
from datetime import datetime
from playwright.sync_api import sync_playwright

def log_with_timestamp(msg: str):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")

def main():
    log_with_timestamp("Starting AudioContext debug session...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            permissions=["microphone"],  # Grant mic permission
        )
        page = context.new_page()

        console_logs = []

        def handle_console(msg):
            text = msg.text
            log_type = msg.type

            # Filter for relevant logs
            is_relevant = any(kw in text.lower() for kw in [
                'audio', 'soniox', 'voice', 'mic', 'recording',
                'websocket', 'connect', 'disconnect', 'error',
                'suspend', 'resume', 'wakelock', 'visibility'
            ])

            if is_relevant or log_type == 'error':
                entry = {
                    'time': datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    'type': log_type,
                    'text': text[:300]
                }
                console_logs.append(entry)
                log_with_timestamp(f"[CONSOLE-{log_type.upper()}] {text[:200]}")

        page.on('console', handle_console)

        # Navigate to page
        log_with_timestamp("Navigating to https://voice-ui.hungson175.com ...")
        page.goto('https://voice-ui.hungson175.com', wait_until='networkidle')
        log_with_timestamp("Page loaded.")

        # Take screenshot
        page.screenshot(path='/tmp/audio_debug_initial.png', full_page=True)
        log_with_timestamp("Screenshot saved to /tmp/audio_debug_initial.png")

        # Inject AudioContext monitoring script
        page.evaluate("""
        () => {
            // Monitor existing AudioContext instances
            const originalAudioContext = window.AudioContext || window.webkitAudioContext;

            if (originalAudioContext) {
                const OriginalAudioContext = originalAudioContext;

                window.AudioContext = function(...args) {
                    const ctx = new OriginalAudioContext(...args);

                    console.log('[AudioContext-Monitor] New AudioContext created, state:', ctx.state);

                    // Monitor state changes
                    ctx.onstatechange = () => {
                        console.log('[AudioContext-Monitor] State changed to:', ctx.state);
                    };

                    // Intercept resume calls
                    const originalResume = ctx.resume.bind(ctx);
                    ctx.resume = async function() {
                        console.log('[AudioContext-Monitor] resume() called');
                        const result = await originalResume();
                        console.log('[AudioContext-Monitor] After resume, state:', ctx.state);
                        return result;
                    };

                    // Intercept suspend calls
                    const originalSuspend = ctx.suspend.bind(ctx);
                    ctx.suspend = async function() {
                        console.log('[AudioContext-Monitor] suspend() called');
                        const result = await originalSuspend();
                        console.log('[AudioContext-Monitor] After suspend, state:', ctx.state);
                        return result;
                    };

                    return ctx;
                };

                console.log('[AudioContext-Monitor] AudioContext monitoring installed');
            }

            // Monitor visibility changes
            document.addEventListener('visibilitychange', () => {
                console.log('[Visibility-Monitor] visibilityState:', document.visibilityState);
            });

            console.log('[Debug] AudioContext and visibility monitoring active');
        }
        """)

        log_with_timestamp("Monitoring script injected. Watching for 60 seconds...")
        log_with_timestamp("-" * 60)

        # Monitor for 60 seconds
        start_time = time.time()
        while time.time() - start_time < 60:
            time.sleep(1)

        log_with_timestamp("-" * 60)
        log_with_timestamp("Monitoring complete.")

        # Summary
        log_with_timestamp(f"\nTotal relevant console logs: {len(console_logs)}")

        # Print all audio-related logs
        audio_logs = [l for l in console_logs if 'audio' in l['text'].lower() or 'soniox' in l['text'].lower()]
        if audio_logs:
            log_with_timestamp("\nAUDIO/SONIOX LOGS:")
            for log in audio_logs:
                log_with_timestamp(f"  [{log['time']}] {log['text']}")

        browser.close()
        log_with_timestamp("Browser closed.")

if __name__ == '__main__':
    main()
