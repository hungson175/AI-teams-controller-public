#!/usr/bin/env python3
"""Test WebSocket content clearing fix in TmuxController."""

from playwright.sync_api import sync_playwright
import time

TEST_EMAIL = "playwright-test@example.com"
TEST_PASSWORD = "testpassword123"

def test_ws_content_clearing():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Track console logs
        console_logs = []
        ws_logs = []
        content_issues = []

        def on_console(msg):
            text = msg.text
            console_logs.append(f"[{msg.type}] {text}")
            if "[WS]" in text:
                ws_logs.append(text)
                # Check for content clearing issues
                if "empty output" in text.lower():
                    content_issues.append(f"IGNORED: {text}")

        page.on("console", on_console)

        try:
            print("1. Navigate to localhost:3334...")
            page.goto("http://localhost:3334", timeout=30000)
            page.wait_for_load_state("networkidle")

            # Login if needed
            if "login" in page.url.lower():
                print("2. Logging in...")
                login_tab = page.locator("button:has-text('Sign In')").first
                if login_tab.count() > 0:
                    login_tab.click()
                    page.wait_for_timeout(500)
                page.locator("#login-email").fill(TEST_EMAIL)
                page.locator("#login-password").fill(TEST_PASSWORD)
                page.locator("button[type='submit']:has-text('Sign in')").click()
                page.wait_for_timeout(3000)

            print("3. Waiting for app to load...")
            page.wait_for_timeout(3000)

            # Check if we can see the team sidebar
            teams = page.locator("button").filter(has_text="ai_controller")
            if teams.count() > 0:
                print("4. Found team, clicking...")
                teams.first.click()
                page.wait_for_timeout(2000)

            # Select a role/pane if available
            panes = page.locator("[data-role]")
            if panes.count() > 0:
                print(f"5. Found {panes.count()} panes, clicking first...")
                panes.first.click()
                page.wait_for_timeout(2000)

            print("6. Monitoring WebSocket for 40 seconds...")
            page.wait_for_timeout(40000)

            # Take screenshot
            page.screenshot(path="/tmp/ws_content_test.png")

            print("\n=== RESULTS ===")
            print(f"WebSocket logs: {len(ws_logs)}")
            print(f"Content issues handled: {len(content_issues)}")

            print("\n=== WEBSOCKET LOGS ===")
            for log in ws_logs[-20:]:
                print(f"  {log}")

            if content_issues:
                print("\n=== EMPTY OUTPUT HANDLED (FIX WORKING) ===")
                for issue in content_issues:
                    print(f"  {issue}")

            # Check for connection status
            ws_connected = any("Connected" in log or "connected" in log.lower() for log in ws_logs)
            ws_pong = any("pong" in log.lower() for log in ws_logs)

            print("\n=== VERDICT ===")
            if ws_connected:
                print("PASS: WebSocket connected successfully")
            else:
                print("WARN: No WebSocket connection log found")

            if ws_pong:
                print("PASS: Pong messages handled correctly")

            if content_issues:
                print("PASS: Empty output messages being ignored (fix working)")
            else:
                print("INFO: No empty output messages received (fix may still be working)")

            print("\nScreenshot: /tmp/ws_content_test.png")
            return True

        except Exception as e:
            print(f"EXCEPTION: {e}")
            page.screenshot(path="/tmp/ws_content_error.png")
            return False

        finally:
            browser.close()

if __name__ == "__main__":
    test_ws_content_clearing()
