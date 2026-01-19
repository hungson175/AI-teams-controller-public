#!/usr/bin/env python3
"""Test CreateTeamDialog - capture exact error message."""

from playwright.sync_api import sync_playwright
import time

TEST_EMAIL = "playwright-test@example.com"
TEST_PASSWORD = "testpassword123"

def test_create_team_error():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        # Capture network responses with full body
        api_responses = []
        def on_response(response):
            if "templates" in response.url:
                try:
                    body = response.text()
                except:
                    body = "(unable to read)"
                api_responses.append({
                    "url": response.url,
                    "status": response.status,
                    "body": body[:1000]
                })
        page.on("response", on_response)

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

                if "login" in page.url.lower():
                    print("   Login failed, trying registration...")
                    register_tab = page.locator("button:has-text('Register')").first
                    if register_tab.count() > 0:
                        register_tab.click()
                        page.wait_for_timeout(500)
                    page.locator("#register-email").fill(TEST_EMAIL)
                    page.locator("#register-username").fill("playwright_tester")
                    page.locator("#register-password").fill(TEST_PASSWORD)
                    page.locator("#register-confirm").fill(TEST_PASSWORD)
                    page.locator("button:has-text('Create Account')").click()
                    page.wait_for_timeout(3000)

            print("3. Opening Create Team dialog...")
            page.wait_for_timeout(2000)
            create_btn = page.locator("button:has-text('Create Team')")
            if create_btn.count() == 0:
                print("   ERROR: Create Team button not found!")
                return
            create_btn.first.click()
            page.wait_for_timeout(1000)

            print("4. Filling form...")
            page.wait_for_selector("[role='dialog']", timeout=5000)

            # Select template
            template_trigger = page.locator("#template")
            if template_trigger.count() > 0:
                template_trigger.click()
                page.wait_for_timeout(500)
                options = page.locator("[role='option']")
                if options.count() > 0:
                    options.first.click()
                    page.wait_for_timeout(500)

            # Fill fields
            page.locator("#projectName").fill(f"test-{int(time.time())}")
            page.locator("#prd").fill("Test PRD")

            print("5. Clicking Create button...")
            create_submit = page.locator("button:has-text('Create'):not(:has-text('Cancel'))")
            create_submit.last.click()

            # Wait for response
            print("6. Waiting for response (30s max)...")
            page.wait_for_timeout(30000)

            # Check for error in dialog
            error_el = page.locator(".text-destructive")
            if error_el.count() > 0:
                error_text = error_el.first.text_content()
                print(f"\n=== ERROR IN DIALOG ===\n{error_text}\n")

            # Check dialog state
            creating_btn = page.locator("button:has-text('Creating')")
            if creating_btn.count() > 0:
                print("Dialog still showing 'Creating...'")

            print("\n=== API RESPONSES ===")
            for resp in api_responses:
                print(f"URL: {resp['url']}")
                print(f"Status: {resp['status']}")
                print(f"Body: {resp['body']}\n")

            print("\n=== CONSOLE LOGS (last 20) ===")
            for log in console_logs[-20:]:
                print(log)

            page.screenshot(path="/tmp/create_team_result.png")
            print("\nScreenshot: /tmp/create_team_result.png")

        except Exception as e:
            print(f"EXCEPTION: {e}")
            page.screenshot(path="/tmp/create_team_error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    test_create_team_error()
