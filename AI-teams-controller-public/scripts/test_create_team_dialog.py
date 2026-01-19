#!/usr/bin/env python3
"""Test CreateTeamDialog - capture any errors during team creation."""

from playwright.sync_api import sync_playwright
import time

TEST_EMAIL = "playwright-test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_USERNAME = "playwright_tester"

def test_create_team_dialog():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        # Capture any errors
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        # Capture network requests
        network_requests = []
        def on_request(request):
            if "templates" in request.url or "create" in request.url:
                network_requests.append(f"REQUEST: {request.method} {request.url}")

        def on_response(response):
            if "templates" in response.url or "create" in response.url:
                network_requests.append(f"RESPONSE: {response.status} {response.url}")

        page.on("request", on_request)
        page.on("response", on_response)

        try:
            print("1. Navigating to http://localhost:3334...")
            page.goto("http://localhost:3334", timeout=30000)
            page.wait_for_load_state("networkidle")

            # Take initial screenshot
            page.screenshot(path="/tmp/01_initial.png", full_page=True)
            print("   Screenshot: /tmp/01_initial.png")

            # Check if we're on login page
            if "login" in page.url.lower():
                print("2. On login page, authenticating...")
                page.screenshot(path="/tmp/02_login_page.png")

                # First try to register (will fail if user exists, that's OK)
                print("   Trying to register test user...")
                register_tab = page.locator("button:has-text('Register')")
                if register_tab.count() > 0:
                    register_tab.click()
                    page.wait_for_timeout(500)

                    # Fill registration form
                    page.locator("#register-email").fill(TEST_EMAIL)
                    page.locator("#register-username").fill(TEST_USERNAME)
                    page.locator("#register-password").fill(TEST_PASSWORD)
                    page.locator("#register-confirm").fill(TEST_PASSWORD)
                    page.locator("button:has-text('Create Account')").click()
                    page.wait_for_timeout(3000)

                    # Check if we got redirected (success)
                    if "login" not in page.url.lower():
                        print("   Registration successful!")
                    else:
                        # Registration failed (user exists), try login
                        print("   Registration failed (user may exist), trying login...")
                        login_tab = page.locator("button:has-text('Sign In')").first
                        if login_tab.count() > 0:
                            login_tab.click()
                            page.wait_for_timeout(500)

                        page.locator("#login-email").fill(TEST_EMAIL)
                        page.locator("#login-password").fill(TEST_PASSWORD)
                        page.locator("button[type='submit']:has-text('Sign in')").click()

                        print("   Waiting for login...")
                        page.wait_for_timeout(3000)

                # Verify we're logged in
                page.screenshot(path="/tmp/03_after_auth.png")
                print("   Screenshot: /tmp/03_after_auth.png")

                if "login" in page.url.lower():
                    print("   ERROR: Auth failed - still on login page")
                    error_el = page.locator(".text-destructive")
                    if error_el.count() > 0:
                        print(f"   Error message: {error_el.text_content()}")
                    browser.close()
                    return

                print("   Authentication successful!")

            print("2. Looking for Create Team button in sidebar...")
            # Wait for sidebar to load
            page.wait_for_timeout(2000)

            # Try to find and click "Create Team" button
            create_team_btn = page.locator("button:has-text('Create Team')")
            if create_team_btn.count() > 0:
                print("   Found Create Team button, clicking...")
                create_team_btn.first.click()
                page.wait_for_timeout(1000)
                page.screenshot(path="/tmp/03_dialog_open.png")
                print("   Screenshot: /tmp/03_dialog_open.png")
            else:
                print("   ERROR: Create Team button not found!")
                # List all buttons for debugging
                buttons = page.locator("button").all()
                print(f"   Found {len(buttons)} buttons:")
                for i, btn in enumerate(buttons[:10]):
                    text = btn.text_content()
                    print(f"     {i}: {text[:50] if text else '(no text)'}")
                page.screenshot(path="/tmp/03_no_button.png")
                browser.close()
                return

            print("3. Filling in the form...")
            # Wait for dialog to be visible
            page.wait_for_selector("[role='dialog']", timeout=5000)

            # Select template from dropdown
            template_trigger = page.locator("#template")
            if template_trigger.count() > 0:
                print("   Clicking template dropdown...")
                template_trigger.click()
                page.wait_for_timeout(500)
                page.screenshot(path="/tmp/04_dropdown_open.png")

                # Select first template option
                options = page.locator("[role='option']")
                if options.count() > 0:
                    print(f"   Found {options.count()} template options, selecting first...")
                    options.first.click()
                    page.wait_for_timeout(500)

            # Fill project name
            project_name_input = page.locator("#projectName")
            if project_name_input.count() > 0:
                print("   Filling project name...")
                project_name_input.fill("test-project-" + str(int(time.time())))

            # Fill PRD
            prd_input = page.locator("#prd")
            if prd_input.count() > 0:
                print("   Filling PRD...")
                prd_input.fill("Test project for debugging CreateTeamDialog errors.")

            page.screenshot(path="/tmp/05_form_filled.png")
            print("   Screenshot: /tmp/05_form_filled.png")

            print("4. Submitting form...")
            # Find and click Create button (not the Cancel button)
            create_btn = page.locator("button:has-text('Create'):not(:has-text('Cancel'))")
            if create_btn.count() > 0:
                create_btn.last.click()
                print("   Clicked Create button, waiting for response...")

                # Wait for either success or error (longer wait - team creation can take time)
                print("   Waiting up to 60s for response...")
                page.wait_for_timeout(10000)
                page.screenshot(path="/tmp/06_after_submit.png")
                print("   Screenshot: /tmp/06_after_submit.png")

                # Check for error messages in dialog
                error_msgs = page.locator(".text-destructive, [class*='error'], [class*='Error']")
                if error_msgs.count() > 0:
                    print("   ERRORS FOUND IN DIALOG:")
                    for i in range(error_msgs.count()):
                        text = error_msgs.nth(i).text_content()
                        if text and text.strip():
                            print(f"     - {text.strip()}")

                # Check if dialog is still open (stuck in Creating state)
                dialog = page.locator("[role='dialog']")
                if dialog.count() > 0:
                    print("   Dialog still open - checking state...")
                    creating_btn = page.locator("button:has-text('Creating')")
                    if creating_btn.count() > 0:
                        print("   WARNING: Still in 'Creating...' state")

                # Wait more and take final screenshot
                page.wait_for_timeout(5000)
                page.screenshot(path="/tmp/07_final.png")
                print("   Screenshot: /tmp/07_final.png")

            print("\n5. Network requests (templates/create):")
            for req in network_requests:
                print(f"   {req}")

            print("\n6. Console logs:")
            for log in console_logs[-20:]:
                print(f"   {log}")

            if errors:
                print("\n7. Page errors:")
                for err in errors:
                    print(f"   {err}")

        except Exception as e:
            print(f"\nEXCEPTION: {e}")
            page.screenshot(path="/tmp/error_screenshot.png")
            print("Error screenshot: /tmp/error_screenshot.png")

        finally:
            browser.close()

if __name__ == "__main__":
    test_create_team_dialog()
