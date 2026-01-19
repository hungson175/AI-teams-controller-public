"""
Common Android Testing Actions for AI Agents

Reusable patterns for Appium + Espresso driver testing.
AI agents can copy/paste these patterns instead of rewriting from scratch.

Last Updated: 2026-01-12
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Tuple, Optional
import time


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def create_session(app_path: str, device_name: str = "Android Emulator") -> webdriver.Remote:
    """
    Create Appium session with Espresso driver.

    Args:
        app_path: Absolute path to APK file
        device_name: Device name from 'adb devices' or "Android Emulator"

    Returns:
        WebDriver instance

    Example:
        driver = create_session("/path/to/app.apk")
    """
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "Espresso"  # Use Espresso for speed
    options.app = app_path
    options.device_name = device_name
    options.auto_grant_permissions = True  # Auto-grant runtime permissions

    # Optional: Faster session creation
    options.skip_unlock = True  # Skip device unlock
    options.no_reset = True  # Don't reset app state between sessions

    driver = webdriver.Remote("http://localhost:4723", options=options)
    return driver


def close_session(driver: webdriver.Remote):
    """
    Properly close Appium session.

    Example:
        close_session(driver)
    """
    if driver:
        driver.quit()


# ============================================================================
# ELEMENT FINDING (Ordered by Speed: Fastest to Slowest)
# ============================================================================

def find_by_id(driver: webdriver.Remote, resource_id: str):
    """
    Find element by resource ID (FASTEST method).

    Args:
        resource_id: Full resource ID (e.g., "com.example.app:id/button_login")
                     or short ID (e.g., "button_login")

    Example:
        element = find_by_id(driver, "button_login")

    Source: https://www.skill2lead.com/appium-python/appium-python-find-elements-method.php
    """
    return driver.find_element(by=AppiumBy.ID, value=resource_id)


def find_by_accessibility_id(driver: webdriver.Remote, accessibility_id: str):
    """
    Find element by accessibility ID (content-desc).
    Fast and accessibility-friendly.

    Args:
        accessibility_id: Value of android:contentDescription attribute

    Example:
        element = find_by_accessibility_id(driver, "Login Button")

    Source: https://testgrid.io/blog/locators-in-appium/
    """
    return driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value=accessibility_id)


def find_by_text(driver: webdriver.Remote, text: str):
    """
    Find element by exact text match.
    Moderate speed, human-readable.

    Args:
        text: Exact text to match

    Example:
        element = find_by_text(driver, "Sign In")

    Source: https://discuss.appium.io/t/search-and-click-element-by-text/31120
    """
    return driver.find_element(
        by=AppiumBy.ANDROID_UIAUTOMATOR,
        value=f'new UiSelector().text("{text}")'
    )


def find_by_partial_text(driver: webdriver.Remote, partial_text: str):
    """
    Find element containing partial text.

    Args:
        partial_text: Partial text to match

    Example:
        element = find_by_partial_text(driver, "Sign")  # Matches "Sign In"
    """
    return driver.find_element(
        by=AppiumBy.ANDROID_UIAUTOMATOR,
        value=f'new UiSelector().textContains("{partial_text}")'
    )


def find_by_class(driver: webdriver.Remote, class_name: str):
    """
    Find element by class name.

    Args:
        class_name: Android widget class (e.g., "android.widget.Button")

    Example:
        element = find_by_class(driver, "android.widget.EditText")

    Source: https://www.browserstack.com/guide/findelement-in-appium
    """
    return driver.find_element(by=AppiumBy.CLASS_NAME, value=class_name)


def find_by_xpath(driver: webdriver.Remote, xpath: str):
    """
    Find element by XPath (SLOWEST - use as last resort).

    Args:
        xpath: XPath expression

    Example:
        element = find_by_xpath(driver, "//android.widget.Button[@text='Login']")

    Warning: XPath is slow and brittle. Prefer ID or accessibility ID.
    Source: https://www.waldo.com/blog/testing-appium-xpath-locators
    """
    return driver.find_element(by=AppiumBy.XPATH, value=xpath)


# ============================================================================
# BASIC ACTIONS
# ============================================================================

def tap_element(driver: webdriver.Remote, locator_type: str, locator_value: str):
    """
    Tap/click an element.

    Args:
        locator_type: "id", "accessibility_id", "text", "xpath"
        locator_value: Value to find element

    Example:
        tap_element(driver, "id", "button_login")
        tap_element(driver, "text", "Sign In")

    Note: Espresso automatically waits for element, no manual wait needed.
    """
    locator_map = {
        "id": AppiumBy.ID,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        "text": AppiumBy.ANDROID_UIAUTOMATOR,
        "xpath": AppiumBy.XPATH,
    }

    by = locator_map.get(locator_type, AppiumBy.ID)

    # Special handling for text locator
    if locator_type == "text":
        locator_value = f'new UiSelector().text("{locator_value}")'

    element = driver.find_element(by=by, value=locator_value)
    element.click()


def input_text(driver: webdriver.Remote, locator_type: str, locator_value: str, text: str, clear_first: bool = True):
    """
    Input text into element (e.g., EditText).

    Args:
        locator_type: "id", "accessibility_id", "text", "xpath"
        locator_value: Value to find element
        text: Text to input
        clear_first: Clear field before typing (default: True)

    Example:
        input_text(driver, "id", "edit_username", "testuser")

    Source: https://medium.com/@BuzonXXXX/python-appium-android-f5cd576668df
    """
    locator_map = {
        "id": AppiumBy.ID,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        "xpath": AppiumBy.XPATH,
    }

    by = locator_map.get(locator_type, AppiumBy.ID)
    element = driver.find_element(by=by, value=locator_value)

    if clear_first:
        element.clear()

    element.send_keys(text)


def get_text(driver: webdriver.Remote, locator_type: str, locator_value: str) -> str:
    """
    Get text content of element.

    Args:
        locator_type: "id", "accessibility_id", "xpath"
        locator_value: Value to find element

    Returns:
        Text content of element

    Example:
        text = get_text(driver, "id", "text_result")
        assert text == "Success"
    """
    locator_map = {
        "id": AppiumBy.ID,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        "xpath": AppiumBy.XPATH,
    }

    by = locator_map.get(locator_type, AppiumBy.ID)
    element = driver.find_element(by=by, value=locator_value)
    return element.text


def is_element_visible(driver: webdriver.Remote, locator_type: str, locator_value: str) -> bool:
    """
    Check if element is visible on screen.

    Args:
        locator_type: "id", "accessibility_id", "text", "xpath"
        locator_value: Value to find element

    Returns:
        True if element is visible, False otherwise

    Example:
        if is_element_visible(driver, "id", "error_message"):
            print("Error displayed")
    """
    try:
        locator_map = {
            "id": AppiumBy.ID,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "xpath": AppiumBy.XPATH,
        }

        by = locator_map.get(locator_type, AppiumBy.ID)

        if locator_type == "text":
            by = AppiumBy.ANDROID_UIAUTOMATOR
            locator_value = f'new UiSelector().text("{locator_value}")'

        element = driver.find_element(by=by, value=locator_value)
        return element.is_displayed()
    except:
        return False


def wait_for_element(driver: webdriver.Remote, locator_type: str, locator_value: str, timeout: int = 10):
    """
    Wait for element to appear (explicit wait).

    Args:
        locator_type: "id", "accessibility_id", "xpath"
        locator_value: Value to find element
        timeout: Maximum wait time in seconds (default: 10)

    Returns:
        Element when found

    Example:
        wait_for_element(driver, "id", "loading_spinner")

    Note: Espresso has automatic waits, but this is useful for edge cases.
    """
    locator_map = {
        "id": AppiumBy.ID,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        "xpath": AppiumBy.XPATH,
    }

    by = locator_map.get(locator_type, AppiumBy.ID)

    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, locator_value)))


# ============================================================================
# GESTURES (Appium 2.0+ Mobile Commands)
# ============================================================================

def swipe_gesture(driver: webdriver.Remote, direction: str, element_id: Optional[str] = None, percent: float = 0.75):
    """
    Swipe gesture (Appium 2.0+ mobile command).

    Args:
        direction: "up", "down", "left", "right"
        element_id: Optional element to swipe on (if None, swipes on screen)
        percent: Swipe distance as percentage (0.0-1.0, default: 0.75)

    Example:
        swipe_gesture(driver, "up")  # Swipe up on screen
        swipe_gesture(driver, "left", element_id="carousel_view", percent=0.5)

    Source: https://medium.com/@ntiinsd/mastering-mobile-automation-swipe-scroll-and-tap-gestures-with-appium-in-2025-319feabe09db
    Source: https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
    """
    params = {
        'direction': direction.lower(),
        'percent': percent
    }

    if element_id:
        params['elementId'] = element_id
    else:
        # Default to screen center area
        params['left'] = 100
        params['top'] = 100
        params['width'] = 200
        params['height'] = 200

    driver.execute_script('mobile: swipeGesture', params)


def scroll_gesture(driver: webdriver.Remote, direction: str, element_id: Optional[str] = None, percent: float = 0.75):
    """
    Scroll gesture (Appium 2.0+ mobile command).

    Args:
        direction: "up", "down", "left", "right"
        element_id: Optional element to scroll (if None, scrolls screen)
        percent: Scroll distance as percentage (0.0-1.0, default: 0.75)

    Example:
        scroll_gesture(driver, "down")  # Scroll down on screen
        scroll_gesture(driver, "up", element_id="scrollview_id")

    Source: https://testgrid.io/blog/appium-scroll/
    """
    params = {
        'direction': direction.lower(),
        'percent': percent
    }

    if element_id:
        params['elementId'] = element_id
    else:
        # Default to screen center area
        params['left'] = 100
        params['top'] = 100
        params['width'] = 200
        params['height'] = 200

    driver.execute_script('mobile: scrollGesture', params)


def scroll_to_text(driver: webdriver.Remote, text: str):
    """
    Scroll until text is visible (Android UiScrollable).

    Args:
        text: Text to scroll to

    Example:
        scroll_to_text(driver, "Privacy Policy")

    Source: https://testgrid.io/blog/appium-scroll/
    """
    driver.find_element(
        by=AppiumBy.ANDROID_UIAUTOMATOR,
        value=f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("{text}"))'
    )


def tap_at_coordinates(driver: webdriver.Remote, x: int, y: int):
    """
    Tap at specific screen coordinates.

    Args:
        x: X coordinate in pixels
        y: Y coordinate in pixels

    Example:
        tap_at_coordinates(driver, 500, 800)

    Source: https://www.browserstack.com/docs/app-automate/appium/advanced-features/appium-gestures
    """
    driver.execute_script('mobile: clickGesture', {'x': x, 'y': y})


def long_press_element(driver: webdriver.Remote, locator_type: str, locator_value: str, duration: int = 1000):
    """
    Long press on element.

    Args:
        locator_type: "id", "accessibility_id", "xpath"
        locator_value: Value to find element
        duration: Hold duration in milliseconds (default: 1000ms = 1s)

    Example:
        long_press_element(driver, "id", "context_menu_item", duration=2000)

    Source: https://www.headspin.io/blog/automating-mobile-gestures-with-appium
    """
    locator_map = {
        "id": AppiumBy.ID,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        "xpath": AppiumBy.XPATH,
    }

    by = locator_map.get(locator_type, AppiumBy.ID)
    element = driver.find_element(by=by, value=locator_value)
    element_id = element.id

    driver.execute_script('mobile: longClickGesture', {
        'elementId': element_id,
        'duration': duration
    })


def double_tap_element(driver: webdriver.Remote, locator_type: str, locator_value: str):
    """
    Double tap on element.

    Args:
        locator_type: "id", "accessibility_id", "xpath"
        locator_value: Value to find element

    Example:
        double_tap_element(driver, "id", "zoom_image")

    Source: https://procodebase.com/article/handling-gestures-and-touch-actions-in-appium
    """
    locator_map = {
        "id": AppiumBy.ID,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        "xpath": AppiumBy.XPATH,
    }

    by = locator_map.get(locator_type, AppiumBy.ID)
    element = driver.find_element(by=by, value=locator_value)
    element_id = element.id

    driver.execute_script('mobile: doubleClickGesture', {'elementId': element_id})


# ============================================================================
# DEVICE ACTIONS
# ============================================================================

def press_back_button(driver: webdriver.Remote):
    """
    Press Android back button.

    Example:
        press_back_button(driver)
    """
    driver.press_keycode(4)  # KEYCODE_BACK = 4


def press_home_button(driver: webdriver.Remote):
    """
    Press Android home button.

    Example:
        press_home_button(driver)
    """
    driver.press_keycode(3)  # KEYCODE_HOME = 3


def press_enter_key(driver: webdriver.Remote):
    """
    Press Enter/Return key (e.g., to submit form).

    Example:
        input_text(driver, "id", "search_field", "query")
        press_enter_key(driver)
    """
    driver.press_keycode(66)  # KEYCODE_ENTER = 66


def hide_keyboard(driver: webdriver.Remote):
    """
    Hide on-screen keyboard.

    Example:
        hide_keyboard(driver)
    """
    try:
        driver.hide_keyboard()
    except:
        # Keyboard already hidden or not supported
        pass


def get_screen_size(driver: webdriver.Remote) -> Tuple[int, int]:
    """
    Get device screen dimensions.

    Returns:
        Tuple of (width, height) in pixels

    Example:
        width, height = get_screen_size(driver)
        print(f"Screen: {width}x{height}")
    """
    size = driver.get_window_size()
    return size['width'], size['height']


def take_screenshot(driver: webdriver.Remote, filename: str):
    """
    Take screenshot and save to file.

    Args:
        filename: Path to save screenshot (e.g., "screenshot.png")

    Example:
        take_screenshot(driver, "/tmp/test_result.png")
    """
    driver.save_screenshot(filename)


# ============================================================================
# ASSERTIONS (Common Test Validations)
# ============================================================================

def assert_element_exists(driver: webdriver.Remote, locator_type: str, locator_value: str):
    """
    Assert element exists on screen.

    Raises AssertionError if element not found.

    Example:
        assert_element_exists(driver, "id", "success_message")
    """
    assert is_element_visible(driver, locator_type, locator_value), \
        f"Element not found: {locator_type}={locator_value}"


def assert_text_equals(driver: webdriver.Remote, locator_type: str, locator_value: str, expected_text: str):
    """
    Assert element text equals expected value.

    Example:
        assert_text_equals(driver, "id", "result_label", "Success")
    """
    actual_text = get_text(driver, locator_type, locator_value)
    assert actual_text == expected_text, \
        f"Text mismatch: expected '{expected_text}', got '{actual_text}'"


def assert_text_contains(driver: webdriver.Remote, locator_type: str, locator_value: str, substring: str):
    """
    Assert element text contains substring.

    Example:
        assert_text_contains(driver, "id", "status_text", "completed")
    """
    actual_text = get_text(driver, locator_type, locator_value)
    assert substring in actual_text, \
        f"Text does not contain '{substring}': got '{actual_text}'"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def wait_seconds(seconds: float):
    """
    Wait for specified seconds (use sparingly with Espresso).

    Note: Espresso has automatic waits, so explicit waits are rarely needed.
    Only use for specific delays (e.g., animation completion).

    Example:
        wait_seconds(2.5)
    """
    time.sleep(seconds)


def get_app_package_and_activity(driver: webdriver.Remote) -> Tuple[str, str]:
    """
    Get current app package and activity.

    Returns:
        Tuple of (package, activity)

    Example:
        package, activity = get_app_package_and_activity(driver)
        print(f"Current: {package}/{activity}")
    """
    package = driver.current_package
    activity = driver.current_activity
    return package, activity


def restart_app(driver: webdriver.Remote):
    """
    Restart the app under test.

    Example:
        restart_app(driver)
    """
    driver.terminate_app(driver.current_package)
    driver.activate_app(driver.current_package)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Login test
    driver = create_session("/path/to/app.apk")

    try:
        # Input credentials
        input_text(driver, "id", "username_field", "testuser")
        input_text(driver, "id", "password_field", "testpass123")

        # Tap login button
        tap_element(driver, "id", "login_button")

        # Wait and verify success
        wait_for_element(driver, "id", "home_screen")
        assert_element_exists(driver, "text", "Welcome")

        print("✅ Login test passed")

    finally:
        close_session(driver)
