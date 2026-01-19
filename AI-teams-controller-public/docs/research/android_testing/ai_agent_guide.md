# Android Testing Guide for AI Agents

**Audience:** QA AI agents in multi-agent teams
**Purpose:** How to test Android apps using Appium + Espresso driver
**Last Updated:** 2026-01-12

---

## Quick Start for AI Agents

### 1. Prerequisites Check

Before writing tests, verify these are installed:

```bash
# Check Appium 3
appium --version  # Must be 3.x

# Check Espresso driver
appium driver list | grep espresso

# Check Python client
python3 -c "from appium import webdriver; print('OK')"

# Check device/emulator
adb devices  # Should show connected device
```

If any missing, see `README.md` Installation section.

### 2. Your Test Writing Workflow

**Step 1: Copy session setup from `common_actions.py`**
```python
from common_actions import create_session, close_session

driver = create_session("/path/to/app.apk")
```

**Step 2: Use reusable actions from `common_actions.py`**
```python
from common_actions import tap_element, input_text, assert_element_exists

tap_element(driver, "id", "login_button")
input_text(driver, "id", "username", "testuser")
assert_element_exists(driver, "text", "Welcome")
```

**Step 3: Reference examples from `example_tests.py`**
- Login test → See `test_login_success()`
- List scrolling → See `test_scroll_and_select_item()`
- Form input → See `test_registration_form()`

**Step 4: Always clean up**
```python
close_session(driver)
```

---

## DO's and DON'Ts for AI Agents

### ✅ DO

1. **Use resource IDs first** (fastest locator):
   ```python
   find_by_id(driver, "button_login")  # FAST ✅
   ```

2. **Copy patterns from `common_actions.py`** instead of writing from scratch:
   ```python
   # Don't rewrite, just import!
   from common_actions import tap_element, input_text
   ```

3. **Reference examples** when testing similar scenarios:
   - Need to test login? → See `test_login_success()` in `example_tests.py`
   - Need to scroll a list? → See `test_scroll_and_select_item()`

4. **Let Espresso handle waits** (no manual `time.sleep()` needed):
   ```python
   # Just find and click - Espresso auto-waits
   driver.find_element(by=AppiumBy.ID, value="button").click()
   ```

5. **Take screenshots on failures** for debugging:
   ```python
   try:
       assert_element_exists(driver, "id", "result")
   except:
       driver.save_screenshot("/tmp/failure.png")
       raise
   ```

### ❌ DON'T

1. **Don't use XPath unless absolutely necessary** (very slow):
   ```python
   # AVOID ❌
   find_by_xpath(driver, "//android.widget.Button[@text='Login']")

   # PREFER ✅
   find_by_id(driver, "login_button")
   ```

2. **Don't use TouchAction class** (removed in Appium 2.0+):
   ```python
   # WRONG ❌ (Appium 1.x)
   from appium.webdriver.common.touch_action import TouchAction
   TouchAction(driver).tap(...).perform()

   # CORRECT ✅ (Appium 2.0+)
   driver.execute_script('mobile: clickGesture', {'x': 100, 'y': 200})
   ```

3. **Don't add explicit waits with Espresso** (auto-waits built-in):
   ```python
   # UNNECESSARY with Espresso ❌
   WebDriverWait(driver, 10).until(...)

   # Espresso auto-waits ✅
   element = driver.find_element(by=AppiumBy.ID, value="id")
   ```

4. **Don't hardcode paths** - make configurable:
   ```python
   # BAD ❌
   app_path = "/Users/me/app.apk"

   # GOOD ✅
   app_path = os.getenv("APP_PATH", "/default/path/app.apk")
   ```

5. **Don't forget cleanup** (always close session):
   ```python
   try:
       # Your test code
   finally:
       close_session(driver)  # ✅ Always cleanup
   ```

---

## Test Pattern Selection Guide

Use this decision tree to pick the right example:

```
What are you testing?
│
├─ Login/Authentication? → test_login_success()
│
├─ Form with multiple inputs? → test_registration_form()
│
├─ List/RecyclerView?
│   ├─ Scrolling to item? → test_scroll_and_select_item()
│   ├─ Pull-to-refresh? → test_pull_to_refresh()
│   └─ Multiple items? → test_add_multiple_items_to_cart()
│
├─ Navigation?
│   ├─ Back button? → test_navigation_flow()
│   └─ Multi-screen? → test_navigation_flow()
│
├─ Search functionality? → test_search_with_results()
│
├─ Gestures?
│   ├─ Swipe carousel? → test_swipe_through_carousel()
│   ├─ Long press? → test_long_press_context_menu()
│   └─ Scroll? → test_scroll_and_select_item()
│
├─ Permissions? → test_camera_permission_grant()
│
└─ App state (background/resume)? → test_app_background_and_resume()
```

---

## Common Testing Scenarios

### Scenario 1: Testing a Login Screen

**Given:** App has login screen with username, password, and login button
**When:** User enters credentials and taps login
**Then:** Home screen appears

**Code:**
```python
from common_actions import create_session, input_text, tap_element, assert_element_exists

driver = create_session("/path/to/app.apk")

# Input credentials
input_text(driver, "id", "username_field", "testuser")
input_text(driver, "id", "password_field", "password123")

# Tap login
tap_element(driver, "id", "login_button")

# Verify success
assert_element_exists(driver, "id", "home_screen")

driver.quit()
```

**Full example:** See `test_login_success()` in `example_tests.py`

---

### Scenario 2: Testing a List with Scroll

**Given:** App has scrollable list with 100 items
**When:** User scrolls to item 50
**Then:** Item 50 is visible and tappable

**Code:**
```python
from common_actions import create_session, scroll_to_text, tap_element

driver = create_session("/path/to/app.apk")

# Scroll to specific item
scroll_to_text(driver, "Item 50")

# Tap the item
tap_element(driver, "text", "Item 50")

# Verify detail screen
assert driver.find_element(by=AppiumBy.ID, value="detail_title").text == "Item 50"

driver.quit()
```

**Full example:** See `test_scroll_and_select_item()` in `example_tests.py`

---

### Scenario 3: Testing Form Submission

**Given:** App has registration form with name, email, password
**When:** User fills form and submits
**Then:** Success message appears

**Code:**
```python
from common_actions import create_session, input_text, tap_element, assert_text_contains

driver = create_session("/path/to/app.apk")

# Fill form
input_text(driver, "id", "name_field", "John Doe")
input_text(driver, "id", "email_field", "john@example.com")
input_text(driver, "id", "password_field", "SecurePass123")

# Submit
tap_element(driver, "id", "submit_button")

# Verify success
assert_text_contains(driver, "id", "result_message", "Success")

driver.quit()
```

**Full example:** See `test_registration_form()` in `example_tests.py`

---

### Scenario 4: Testing Search

**Given:** App has search functionality
**When:** User searches for "Android"
**Then:** Results containing "Android" appear

**Code:**
```python
from common_actions import create_session, tap_element, input_text, press_enter_key, assert_element_exists

driver = create_session("/path/to/app.apk")

# Open search
tap_element(driver, "id", "search_button")

# Enter query
input_text(driver, "id", "search_field", "Android")
press_enter_key(driver)

# Verify results
assert_element_exists(driver, "id", "search_results")

driver.quit()
```

**Full example:** See `test_search_with_results()` in `example_tests.py`

---

## Espresso-Specific Advantages for AI Agents

### 1. No Manual Waits Required

**UI Automator 2** (old way):
```python
# Manual wait needed ❌
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((AppiumBy.ID, "result"))
)
element.click()
```

**Espresso** (automatic):
```python
# Just find and click - automatic wait ✅
driver.find_element(by=AppiumBy.ID, value="result").click()
```

### 2. Better RecyclerView/ListView Handling

**UI Automator 2:**
```python
# Scroll and hope element loaded ⚠️
scroll_gesture(driver, "down")
time.sleep(2)  # Wait for data load
element = driver.find_element(by=AppiumBy.ID, value="item_50")
```

**Espresso:**
```python
# Direct scroll to view - Espresso handles loading ✅
scroll_to_text(driver, "Item 50")
# Element is guaranteed visible and loaded
```

### 3. Faster Test Execution

**Speed comparison (approximate):**
- UI Automator 2: 100 test actions = ~60 seconds
- Espresso: 100 test actions = ~30 seconds

**Why?** Espresso has direct UI thread access, no cross-process communication overhead.

---

## Debugging Failed Tests

### Step 1: Take Screenshot

```python
try:
    assert_element_exists(driver, "id", "result")
except AssertionError:
    screenshot_path = f"/tmp/failure_{int(time.time())}.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot: {screenshot_path}")
    raise
```

### Step 2: Print Current Screen Info

```python
# Get current activity
package = driver.current_package
activity = driver.current_activity
print(f"Current: {package}/{activity}")

# Get page source (XML hierarchy)
page_source = driver.page_source
print(page_source)
```

### Step 3: Verify Element Locator

```python
# Try different locator strategies
try:
    element = driver.find_element(by=AppiumBy.ID, value="button")
except:
    print("ID failed, trying text...")
    element = driver.find_element(
        by=AppiumBy.ANDROID_UIAUTOMATOR,
        value='new UiSelector().text("Login")'
    )
```

### Step 4: Check Element Properties

```python
element = driver.find_element(by=AppiumBy.ID, value="button")
print(f"Text: {element.text}")
print(f"Enabled: {element.is_enabled()}")
print(f"Displayed: {element.is_displayed()}")
print(f"Size: {element.size}")
print(f"Location: {element.location}")
```

---

## Integration with Multi-Agent Workflow

### Your Role (QA Agent)

1. **Receive test spec from TL** (Tech Lead)
   - Example: "Test login with valid/invalid credentials"

2. **Write test using reusable actions**
   - Copy patterns from `common_actions.py`
   - Reference similar examples from `example_tests.py`

3. **Run test and report results**
   - ✅ PASS: Report to SM with details
   - ❌ FAIL: Take screenshot, report to SM with evidence

4. **Update WHITEBOARD**
   - Log test results in team WHITEBOARD.md

### Communication Pattern

```bash
# After writing test
tm-send SM "QA [HH:mm]: Test written for login flow. Running now."

# After test passes
tm-send SM "QA [HH:mm]: Login test PASSED (3/3 scenarios). Screenshot: /tmp/test_pass.png"

# After test fails
tm-send SM "QA [HH:mm]: Login test FAILED on invalid credentials scenario. Screenshot: /tmp/test_fail.png. Error: Element 'error_message' not found."
```

---

## Performance Tips for AI Agents

### 1. Prefer ID > Accessibility ID > Text > XPath

```python
# Fastest (use this!) ⭐⭐⭐⭐⭐
find_by_id(driver, "button_login")

# Fast ⭐⭐⭐⭐
find_by_accessibility_id(driver, "Login Button")

# Moderate ⭐⭐⭐
find_by_text(driver, "Login")

# Slow (avoid) ⭐
find_by_xpath(driver, "//android.widget.Button[@text='Login']")
```

### 2. Reuse Driver Session

```python
# BAD ❌ - Create new session for each test (slow)
def test_1():
    driver = create_session(...)
    # test code
    driver.quit()

def test_2():
    driver = create_session(...)  # Slow startup again!
    # test code
    driver.quit()

# GOOD ✅ - Reuse session with pytest fixture
@pytest.fixture(scope="module")
def driver():
    driver = create_session(...)
    yield driver
    driver.quit()

def test_1(driver):  # Reuses same session
    # test code

def test_2(driver):  # Reuses same session
    # test code
```

### 3. Use `no_reset=True` for Faster Sessions

```python
options.no_reset = True  # Don't uninstall/reinstall app between sessions
```

---

## Checklist: Before Running Tests

- [ ] Appium server running (`appium`)
- [ ] Device/emulator connected (`adb devices`)
- [ ] App APK path correct
- [ ] `common_actions.py` imported
- [ ] Session cleanup in `finally` block
- [ ] Screenshots on failure implemented

---

## Summary: Your AI Agent Workflow

1. **Read test spec** from TL
2. **Find similar example** in `example_tests.py`
3. **Copy reusable actions** from `common_actions.py`
4. **Write test** following example pattern
5. **Run test** with `pytest test_file.py -v`
6. **Take screenshot** if test fails
7. **Report results** to SM via `tm-send`
8. **Update WHITEBOARD** with test status

**Remember:** Don't rewrite code from scratch - reuse patterns from `common_actions.py` and `example_tests.py`!

---

## Sources

- [Appium Finding Elements](https://appium.github.io/appium.io/docs/en/writing-running-appium/finding-elements/)
- [Appium Locators Guide - TestGrid](https://testgrid.io/blog/locators-in-appium/)
- [Mastering Mobile Automation - Medium](https://medium.com/@ntiinsd/mastering-mobile-automation-swipe-scroll-and-tap-gestures-with-appium-in-2025-319feabe09db)
- [Android Mobile Gestures - Appium GitHub](https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md)
