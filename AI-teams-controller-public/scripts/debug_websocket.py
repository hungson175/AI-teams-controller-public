#!/usr/bin/env python3
"""
Debug WebSocket disconnection issues on voice-ui.hungson175.com
Monitors console logs for WebSocket events, ping/pong, and errors.
"""

import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

def log_with_timestamp(msg: str):
    """Print message with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")

def main():
    log_with_timestamp("Starting WebSocket debug session...")

    with sync_playwright() as p:
        # Launch browser with devtools enabled for better debugging
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Track WebSocket events
        ws_events = []
        console_logs = []

        # Listen to all console messages
        def handle_console(msg):
            text = msg.text
            log_type = msg.type

            # Filter for relevant logs
            is_relevant = any(kw in text.lower() for kw in [
                'websocket', 'ws', 'socket', 'connect', 'disconnect',
                'ping', 'pong', 'close', 'error', 'feedback', 'pubsub',
                'reconnect', 'keepalive', 'timeout'
            ])

            if is_relevant or log_type == 'error':
                entry = {
                    'time': datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    'type': log_type,
                    'text': text[:500]  # Truncate long messages
                }
                console_logs.append(entry)
                log_with_timestamp(f"[CONSOLE-{log_type.upper()}] {text[:200]}")

        page.on('console', handle_console)

        # Listen for page errors
        def handle_error(error):
            log_with_timestamp(f"[PAGE-ERROR] {error}")

        page.on('pageerror', handle_error)

        # Listen for WebSocket events via CDP
        client = context.new_cdp_session(page)
        client.send('Network.enable')

        def handle_ws_created(params):
            url = params.get('url', '')
            ws_id = params.get('requestId', '')
            log_with_timestamp(f"[WS-CREATED] {url}")
            ws_events.append({'event': 'created', 'url': url, 'id': ws_id, 'time': datetime.now().isoformat()})

        def handle_ws_closed(params):
            ws_id = params.get('requestId', '')
            log_with_timestamp(f"[WS-CLOSED] WebSocket closed (ID: {ws_id})")
            ws_events.append({'event': 'closed', 'id': ws_id, 'time': datetime.now().isoformat()})

        def handle_ws_frame_received(params):
            payload = params.get('response', {}).get('payloadData', '')
            # Log all frames for debugging ping/pong
            log_with_timestamp(f"[WS-RECV] {payload[:100]}")

        def handle_ws_frame_sent(params):
            payload = params.get('request', {}).get('payloadData', '')
            # Log all frames for debugging ping/pong
            log_with_timestamp(f"[WS-SENT] {payload[:100]}")

        def handle_ws_error(params):
            error = params.get('errorMessage', 'Unknown error')
            log_with_timestamp(f"[WS-ERROR] {error}")
            ws_events.append({'event': 'error', 'error': error, 'time': datetime.now().isoformat()})

        client.on('Network.webSocketCreated', handle_ws_created)
        client.on('Network.webSocketClosed', handle_ws_closed)
        client.on('Network.webSocketFrameReceived', handle_ws_frame_received)
        client.on('Network.webSocketFrameSent', handle_ws_frame_sent)
        client.on('Network.webSocketFrameError', handle_ws_error)

        # Navigate to the page
        log_with_timestamp("Navigating to https://voice-ui.hungson175.com ...")
        page.goto('https://voice-ui.hungson175.com', wait_until='networkidle')
        log_with_timestamp("Page loaded. Waiting for WebSocket connections...")

        # Take initial screenshot
        page.screenshot(path='/tmp/ws_debug_initial.png', full_page=True)
        log_with_timestamp("Initial screenshot saved to /tmp/ws_debug_initial.png")

        # Monitor for 3 minutes (180 seconds)
        MONITOR_DURATION = 180
        log_with_timestamp(f"Monitoring for {MONITOR_DURATION} seconds...")
        log_with_timestamp("Looking for: WebSocket close events, ping/pong, errors")
        log_with_timestamp("-" * 60)

        start_time = time.time()
        last_status = start_time

        while time.time() - start_time < MONITOR_DURATION:
            # Print status every 30 seconds
            if time.time() - last_status >= 30:
                elapsed = int(time.time() - start_time)
                log_with_timestamp(f"--- Status: {elapsed}s elapsed, {len(ws_events)} WS events, {len(console_logs)} console logs ---")
                last_status = time.time()

            # Small sleep to avoid busy waiting
            time.sleep(1)

        log_with_timestamp("-" * 60)
        log_with_timestamp("Monitoring complete.")

        # Take final screenshot
        page.screenshot(path='/tmp/ws_debug_final.png', full_page=True)
        log_with_timestamp("Final screenshot saved to /tmp/ws_debug_final.png")

        # Summary
        log_with_timestamp("\n" + "=" * 60)
        log_with_timestamp("SUMMARY")
        log_with_timestamp("=" * 60)
        log_with_timestamp(f"Total WebSocket events: {len(ws_events)}")
        log_with_timestamp(f"Total relevant console logs: {len(console_logs)}")

        # Count event types
        created = sum(1 for e in ws_events if e['event'] == 'created')
        closed = sum(1 for e in ws_events if e['event'] == 'closed')
        errors = sum(1 for e in ws_events if e['event'] == 'error')

        log_with_timestamp(f"  - WebSocket created: {created}")
        log_with_timestamp(f"  - WebSocket closed: {closed}")
        log_with_timestamp(f"  - WebSocket errors: {errors}")

        # Print error logs
        error_logs = [l for l in console_logs if l['type'] == 'error']
        if error_logs:
            log_with_timestamp("\nERROR LOGS:")
            for log in error_logs:
                log_with_timestamp(f"  [{log['time']}] {log['text']}")

        # Print WebSocket events
        if ws_events:
            log_with_timestamp("\nWEBSOCKET EVENTS:")
            for event in ws_events:
                log_with_timestamp(f"  {event}")

        browser.close()
        log_with_timestamp("Browser closed. Debug session complete.")

if __name__ == '__main__':
    main()
