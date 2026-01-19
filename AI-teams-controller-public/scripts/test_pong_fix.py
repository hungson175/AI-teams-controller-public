#!/usr/bin/env python3
"""Test that pong JSON parse error is fixed."""

from playwright.sync_api import sync_playwright
import time

TEST_EMAIL = "playwright-test@example.com"
TEST_PASSWORD = "testpassword123"

def test_pong_fix():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs - specifically looking for pong errors
        console_logs = []
        pong_errors = []
        pong_success = []

        def on_console(msg):
            text = msg.text
            console_logs.append(f"[{msg.type}] {text}")
            if "pong" in text.lower():
                if msg.type == "error":
                    pong_errors.append(text)
                else:
                    pong_success.append(text)

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

            print("3. Waiting for WebSocket connection...")
            page.wait_for_timeout(5000)

            # Wait for at least one ping/pong cycle (30 seconds + buffer)
            print("4. Waiting 35 seconds for ping/pong cycle...")
            page.wait_for_timeout(35000)

            print("\n=== RESULTS ===")
            print(f"Pong errors found: {len(pong_errors)}")
            print(f"Pong success logs: {len(pong_success)}")

            if pong_errors:
                print("\n=== PONG ERRORS (BUG NOT FIXED) ===")
                for err in pong_errors:
                    print(f"  ERROR: {err}")
            else:
                print("\n=== NO PONG ERRORS (BUG FIXED!) ===")

            if pong_success:
                print("\n=== PONG SUCCESS LOGS ===")
                for log in pong_success:
                    print(f"  OK: {log}")

            # Show WebSocket related logs
            print("\n=== WEBSOCKET LOGS ===")
            for log in console_logs:
                if "websocket" in log.lower() or "voicefeedback" in log.lower() or "ping" in log.lower():
                    print(f"  {log}")

            # Verdict
            print("\n=== VERDICT ===")
            if pong_errors:
                print("FAIL: Pong parse errors still occurring")
                return False
            elif pong_success:
                print("PASS: Pong handled correctly")
                return True
            else:
                print("INCONCLUSIVE: No pong messages observed (may need longer wait)")
                return None

        except Exception as e:
            print(f"EXCEPTION: {e}")
            return False

        finally:
            browser.close()

if __name__ == "__main__":
    test_pong_fix()
