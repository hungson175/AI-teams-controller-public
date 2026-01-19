#!/usr/bin/env python3
"""Detailed test for CreateTeamDialog - capture full API responses."""

from playwright.sync_api import sync_playwright
import time
import json

TEST_EMAIL = "playwright-test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_USERNAME = "playwright_tester"

def test_create_team_detailed():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        # Capture any errors
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        # Capture full API responses
        api_responses = []
        def on_response(response):
            if "templates" in response.url:
                try:
                    body = response.text()
                except:
                    body = "(unable to read body)"
                api_responses.append({
                    "url": response.url,
                    "status": response.status,
                    "body": body[:2000]  # Limit length
                })

        page.on("response", on_response)

        try:
            print("1. Navigating to http://localhost:3334...")
            page.goto("http://localhost:3334", timeout=30000)
            page.wait_for_load_state("networkidle")

            # Check if we're on login page
            if "login" in page.url.lower():
                print("2. On login page, authenticating...")

                # Try login first
                login_tab = page.locator("button:has-text('Sign In')").first
                if login_tab.count() > 0:
                    login_tab.click()
                    page.wait_for_timeout(500)

                page.locator("#login-email").fill(TEST_EMAIL)
                page.locator("#login-password").fill(TEST_PASSWORD)
                page.locator("button[type='submit']:has-text('Sign in')").click()
                page.wait_for_timeout(3000)

                if "login" in page.url.lower():
                    # Registration needed
                    print("   Login failed, trying registration...")
                    register_tab = page.locator("button:has-text('Register')").first
                    if register_tab.count() > 0:
                        register_tab.click()
                        page.wait_for_timeout(500)

                    page.locator("#register-email").fill(TEST_EMAIL)
                    page.locator("#register-username").fill(TEST_USERNAME)
                    page.locator("#register-password").fill(TEST_PASSWORD)
                    page.locator("#register-confirm").fill(TEST_PASSWORD)
                    page.locator("button:has-text('Create Account')").click()
                    page.wait_for_timeout(3000)

                if "login" in page.url.lower():
                    print("   ERROR: Auth failed!")
                    return

                print("   Auth successful!")

            print("3. Looking for Create Team button...")
            page.wait_for_timeout(2000)

            create_team_btn = page.locator("button:has-text('Create Team')")
            if create_team_btn.count() == 0:
                print("   ERROR: Create Team button not found!")
                page.screenshot(path="/tmp/detailed_no_button.png")
                return

            create_team_btn.first.click()
            page.wait_for_timeout(1000)

            print("4. Filling in the form...")
            page.wait_for_selector("[role='dialog']", timeout=5000)

            # Select template
            template_trigger = page.locator("#template")
            if template_trigger.count() > 0:
                template_trigger.click()
                page.wait_for_timeout(500)

                options = page.locator("[role='option']")
                print(f"   Found {options.count()} template options")
                if options.count() > 0:
                    # Get the option text
                    for i in range(options.count()):
                        opt_text = options.nth(i).text_content()
                        print(f"   Option {i}: {opt_text}")
                    options.first.click()
                    page.wait_for_timeout(500)

            # Fill project name
            project_name = f"test-proj-{int(time.time())}"
            page.locator("#projectName").fill(project_name)
            print(f"   Project name: {project_name}")

            # Fill PRD
            page.locator("#prd").fill("Test project for debugging.")

            page.screenshot(path="/tmp/detailed_form_filled.png")

            print("5. Submitting form...")
            create_btn = page.locator("button:has-text('Create'):not(:has-text('Cancel'))")
            create_btn.last.click()

            # Wait and capture response
            print("   Waiting for API response...")
            page.wait_for_timeout(15000)

            page.screenshot(path="/tmp/detailed_after_submit.png")

            print("\n=== API RESPONSES ===")
            for resp in api_responses:
                print(f"\nURL: {resp['url']}")
                print(f"Status: {resp['status']}")
                print(f"Body: {resp['body'][:500]}")

            print("\n=== CONSOLE LOGS (last 30) ===")
            for log in console_logs[-30:]:
                print(log)

            if errors:
                print("\n=== PAGE ERRORS ===")
                for err in errors:
                    print(err)

            # Check dialog state
            dialog = page.locator("[role='dialog']")
            if dialog.count() > 0:
                print("\n=== DIALOG STILL OPEN ===")
                creating_btn = page.locator("button:has-text('Creating')")
                if creating_btn.count() > 0:
                    print("Button still shows 'Creating...'")

        except Exception as e:
            print(f"\nEXCEPTION: {e}")
            page.screenshot(path="/tmp/detailed_error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    test_create_team_detailed()
