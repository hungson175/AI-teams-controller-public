"""
Example Android Tests using Appium + Espresso Driver

Full test scenarios demonstrating common testing patterns.
AI agents can use these as templates for similar test cases.

Last Updated: 2026-01-12
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
import time


# ============================================================================
# FIXTURE: Setup and Teardown
# ============================================================================

@pytest.fixture
def driver():
    """
    Pytest fixture to create and cleanup Appium session.

    Usage in test:
        def test_something(driver):
            # driver is automatically created and cleaned up
    """
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "Espresso"
    options.app = "/path/to/app.apk"  # Replace with actual APK path
    options.device_name = "Android Emulator"
    options.auto_grant_permissions = True
    options.no_reset = True

    # Create session
    driver = webdriver.Remote("http://localhost:4723", options=options)

    yield driver

    # Cleanup
    driver.quit()


# ============================================================================
# EXAMPLE 1: Login Flow Test
# ============================================================================

def test_login_success(driver):
    """
    Test successful login flow.

    Steps:
    1. Launch app
    2. Enter valid credentials
    3. Tap login button
    4. Verify home screen appears
    """
    # Find and fill username field
    username_field = driver.find_element(by=AppiumBy.ID, value="username_edit_text")
    username_field.clear()
    username_field.send_keys("testuser@example.com")

    # Find and fill password field
    password_field = driver.find_element(by=AppiumBy.ID, value="password_edit_text")
    password_field.clear()
    password_field.send_keys("password123")

    # Hide keyboard (optional, for better visibility)
    try:
        driver.hide_keyboard()
    except:
        pass

    # Tap login button
    login_button = driver.find_element(by=AppiumBy.ID, value="login_button")
    login_button.click()

    # Verify home screen loads (Espresso auto-waits for UI idle)
    home_indicator = driver.find_element(by=AppiumBy.ID, value="home_screen_title")
    assert home_indicator.is_displayed()
    assert "Welcome" in home_indicator.text


def test_login_invalid_credentials(driver):
    """
    Test login with invalid credentials shows error.

    Steps:
    1. Enter invalid credentials
    2. Tap login button
    3. Verify error message appears
    """
    # Enter invalid credentials
    username_field = driver.find_element(by=AppiumBy.ID, value="username_edit_text")
    username_field.send_keys("invalid@example.com")

    password_field = driver.find_element(by=AppiumBy.ID, value="password_edit_text")
    password_field.send_keys("wrongpassword")

    # Tap login
    login_button = driver.find_element(by=AppiumBy.ID, value="login_button")
    login_button.click()

    # Verify error message appears
    error_message = driver.find_element(by=AppiumBy.ID, value="error_text_view")
    assert error_message.is_displayed()
    assert "Invalid credentials" in error_message.text


# ============================================================================
# EXAMPLE 2: Form Input and Validation
# ============================================================================

def test_registration_form(driver):
    """
    Test registration form with validation.

    Steps:
    1. Navigate to registration screen
    2. Fill all required fields
    3. Submit form
    4. Verify success message
    """
    # Navigate to registration screen
    register_link = driver.find_element(by=AppiumBy.ID, value="register_link")
    register_link.click()

    # Fill registration form
    driver.find_element(by=AppiumBy.ID, value="name_field").send_keys("John Doe")
    driver.find_element(by=AppiumBy.ID, value="email_field").send_keys("john@example.com")
    driver.find_element(by=AppiumBy.ID, value="phone_field").send_keys("1234567890")
    driver.find_element(by=AppiumBy.ID, value="password_field").send_keys("SecurePass123!")
    driver.find_element(by=AppiumBy.ID, value="confirm_password_field").send_keys("SecurePass123!")

    # Accept terms and conditions (checkbox)
    terms_checkbox = driver.find_element(by=AppiumBy.ID, value="terms_checkbox")
    if not terms_checkbox.is_selected():
        terms_checkbox.click()

    # Submit form
    submit_button = driver.find_element(by=AppiumBy.ID, value="submit_button")
    submit_button.click()

    # Verify success
    success_message = driver.find_element(by=AppiumBy.ID, value="success_message")
    assert "Registration successful" in success_message.text


# ============================================================================
# EXAMPLE 3: List/RecyclerView Interaction
# ============================================================================

def test_scroll_and_select_item(driver):
    """
    Test scrolling through list and selecting item.

    Steps:
    1. Navigate to list screen
    2. Scroll to find specific item
    3. Tap item
    4. Verify detail screen opens
    """
    # Navigate to list screen
    list_tab = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="List Tab")
    list_tab.click()

    # Scroll to item using UiScrollable
    target_item = driver.find_element(
        by=AppiumBy.ANDROID_UIAUTOMATOR,
        value='new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("Item 50"))'
    )

    # Tap the item
    target_item.click()

    # Verify detail screen
    detail_title = driver.find_element(by=AppiumBy.ID, value="detail_title")
    assert "Item 50" in detail_title.text


def test_pull_to_refresh(driver):
    """
    Test pull-to-refresh functionality.

    Steps:
    1. Navigate to list screen
    2. Perform swipe down gesture
    3. Verify refresh indicator appears
    4. Wait for content to reload
    """
    # Get list container
    list_view = driver.find_element(by=AppiumBy.ID, value="recycler_view")

    # Perform pull-to-refresh (swipe down)
    driver.execute_script('mobile: swipeGesture', {
        'elementId': list_view.id,
        'direction': 'down',
        'percent': 0.8
    })

    # Verify refresh indicator (may disappear quickly with Espresso)
    # Check updated timestamp or content instead
    timestamp = driver.find_element(by=AppiumBy.ID, value="last_updated_text")
    initial_time = timestamp.text

    # Wait a moment for refresh
    time.sleep(2)

    # Verify timestamp updated
    updated_time = timestamp.text
    assert updated_time != initial_time


# ============================================================================
# EXAMPLE 4: Navigation and Back Button
# ============================================================================

def test_navigation_flow(driver):
    """
    Test multi-screen navigation and back button.

    Steps:
    1. Navigate through 3 screens
    2. Press back button
    3. Verify returned to previous screen
    """
    # Screen 1 -> Screen 2
    driver.find_element(by=AppiumBy.ID, value="settings_button").click()

    # Verify on Screen 2
    assert driver.find_element(by=AppiumBy.ID, value="settings_title").is_displayed()

    # Screen 2 -> Screen 3
    driver.find_element(by=AppiumBy.ID, value="privacy_option").click()

    # Verify on Screen 3
    assert driver.find_element(by=AppiumBy.ID, value="privacy_title").is_displayed()

    # Press back button
    driver.press_keycode(4)  # KEYCODE_BACK

    # Verify back on Screen 2
    assert driver.find_element(by=AppiumBy.ID, value="settings_title").is_displayed()

    # Press back again
    driver.press_keycode(4)

    # Verify back on Screen 1 (home)
    assert driver.find_element(by=AppiumBy.ID, value="home_screen_title").is_displayed()


# ============================================================================
# EXAMPLE 5: Search Functionality
# ============================================================================

def test_search_with_results(driver):
    """
    Test search functionality with results.

    Steps:
    1. Open search
    2. Enter search query
    3. Press enter/search
    4. Verify results appear
    """
    # Open search
    search_button = driver.find_element(by=AppiumBy.ID, value="search_button")
    search_button.click()

    # Enter search query
    search_field = driver.find_element(by=AppiumBy.ID, value="search_edit_text")
    search_field.send_keys("Android Testing")

    # Press Enter key to submit
    driver.press_keycode(66)  # KEYCODE_ENTER

    # Verify results appear
    results_list = driver.find_element(by=AppiumBy.ID, value="search_results_list")
    assert results_list.is_displayed()

    # Verify at least one result
    first_result = driver.find_element(by=AppiumBy.ID, value="result_item_0")
    assert first_result.is_displayed()


def test_search_no_results(driver):
    """
    Test search with no results shows empty state.

    Steps:
    1. Search for nonexistent term
    2. Verify empty state message
    """
    # Open search
    search_button = driver.find_element(by=AppiumBy.ID, value="search_button")
    search_button.click()

    # Enter query with no results
    search_field = driver.find_element(by=AppiumBy.ID, value="search_edit_text")
    search_field.send_keys("xyznonexistent123")
    driver.press_keycode(66)

    # Verify empty state
    empty_message = driver.find_element(by=AppiumBy.ID, value="empty_state_text")
    assert empty_message.is_displayed()
    assert "No results found" in empty_message.text


# ============================================================================
# EXAMPLE 6: Swipe Gestures (Carousel/ViewPager)
# ============================================================================

def test_swipe_through_carousel(driver):
    """
    Test swiping through image carousel/ViewPager.

    Steps:
    1. Navigate to carousel screen
    2. Swipe left 3 times
    3. Verify reached 4th item
    """
    # Navigate to carousel
    carousel_tab = driver.find_element(by=AppiumBy.ID, value="carousel_tab")
    carousel_tab.click()

    # Get initial position indicator
    position_indicator = driver.find_element(by=AppiumBy.ID, value="position_text")
    assert "1 / 10" in position_indicator.text

    # Swipe left 3 times
    carousel_view = driver.find_element(by=AppiumBy.ID, value="view_pager")
    for _ in range(3):
        driver.execute_script('mobile: swipeGesture', {
            'elementId': carousel_view.id,
            'direction': 'left',
            'percent': 0.75
        })
        time.sleep(0.5)  # Brief pause between swipes

    # Verify position
    position_indicator = driver.find_element(by=AppiumBy.ID, value="position_text")
    assert "4 / 10" in position_indicator.text


# ============================================================================
# EXAMPLE 7: Long Press and Context Menu
# ============================================================================

def test_long_press_context_menu(driver):
    """
    Test long press to open context menu.

    Steps:
    1. Navigate to item list
    2. Long press on item
    3. Verify context menu appears
    4. Select menu option
    """
    # Navigate to list
    list_item = driver.find_element(by=AppiumBy.ID, value="list_item_0")

    # Long press on item (2 seconds)
    driver.execute_script('mobile: longClickGesture', {
        'elementId': list_item.id,
        'duration': 2000
    })

    # Verify context menu appears
    context_menu = driver.find_element(by=AppiumBy.ID, value="context_menu")
    assert context_menu.is_displayed()

    # Select "Delete" option
    delete_option = driver.find_element(by=AppiumBy.ID, value="menu_delete")
    delete_option.click()

    # Verify confirmation dialog
    confirm_dialog = driver.find_element(by=AppiumBy.ID, value="confirm_dialog_title")
    assert "Delete" in confirm_dialog.text


# ============================================================================
# EXAMPLE 8: Permissions Handling
# ============================================================================

def test_camera_permission_grant(driver):
    """
    Test granting camera permission.

    Steps:
    1. Trigger camera permission request
    2. Grant permission via system dialog
    3. Verify camera opens

    Note: This assumes auto_grant_permissions=False in capabilities.
    """
    # Trigger camera permission
    camera_button = driver.find_element(by=AppiumBy.ID, value="open_camera_button")
    camera_button.click()

    # Wait for permission dialog
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((
            AppiumBy.ID,
            "com.android.permissioncontroller:id/permission_allow_button"
        ))
    )

    # Grant permission
    allow_button = driver.find_element(
        by=AppiumBy.ID,
        value="com.android.permissioncontroller:id/permission_allow_button"
    )
    allow_button.click()

    # Verify camera opened
    camera_preview = driver.find_element(by=AppiumBy.ID, value="camera_preview")
    assert camera_preview.is_displayed()


# ============================================================================
# EXAMPLE 9: Multi-Element Interactions
# ============================================================================

def test_add_multiple_items_to_cart(driver):
    """
    Test adding multiple items to shopping cart.

    Steps:
    1. Navigate to product list
    2. Add 3 different items to cart
    3. Verify cart count updates
    4. Open cart and verify items
    """
    # Navigate to products
    products_tab = driver.find_element(by=AppiumBy.ID, value="products_tab")
    products_tab.click()

    # Add 3 items to cart
    for i in range(3):
        add_button = driver.find_element(by=AppiumBy.ID, value=f"add_to_cart_button_{i}")
        add_button.click()
        time.sleep(0.5)  # Wait for animation

    # Verify cart badge shows 3
    cart_badge = driver.find_element(by=AppiumBy.ID, value="cart_badge")
    assert cart_badge.text == "3"

    # Open cart
    cart_button = driver.find_element(by=AppiumBy.ID, value="cart_button")
    cart_button.click()

    # Verify 3 items in cart
    cart_items = driver.find_elements(by=AppiumBy.CLASS_NAME, value="cart_item_view")
    assert len(cart_items) == 3


# ============================================================================
# EXAMPLE 10: Screenshot and Debugging
# ============================================================================

def test_with_screenshot_on_failure(driver):
    """
    Test with screenshot capture on assertion failure.

    Demonstrates debugging pattern for failed tests.
    """
    try:
        # Navigate to screen
        settings_button = driver.find_element(by=AppiumBy.ID, value="settings_button")
        settings_button.click()

        # Perform action that might fail
        save_button = driver.find_element(by=AppiumBy.ID, value="save_button")
        save_button.click()

        # Assert success
        success_toast = driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@text, 'Saved')]")
        assert success_toast.is_displayed()

    except AssertionError as e:
        # Take screenshot on failure
        screenshot_path = f"/tmp/test_failure_{int(time.time())}.png"
        driver.save_screenshot(screenshot_path)
        print(f"❌ Test failed. Screenshot saved: {screenshot_path}")
        raise e


# ============================================================================
# EXAMPLE 11: App State Management
# ============================================================================

def test_app_background_and_resume(driver):
    """
    Test app behavior when backgrounded and resumed.

    Steps:
    1. Open screen with data
    2. Send app to background (press home)
    3. Resume app
    4. Verify data persisted
    """
    # Navigate and load data
    data_screen = driver.find_element(by=AppiumBy.ID, value="data_screen_button")
    data_screen.click()

    # Get initial data
    data_field = driver.find_element(by=AppiumBy.ID, value="data_text")
    initial_data = data_field.text

    # Send app to background (press home button)
    driver.press_keycode(3)  # KEYCODE_HOME
    time.sleep(2)

    # Resume app
    driver.activate_app(driver.current_package)

    # Verify data persisted
    data_field = driver.find_element(by=AppiumBy.ID, value="data_text")
    resumed_data = data_field.text
    assert resumed_data == initial_data


# ============================================================================
# RUNNING TESTS
# ============================================================================

if __name__ == "__main__":
    """
    Run tests with pytest:

    # Run all tests
    pytest example_tests.py -v

    # Run specific test
    pytest example_tests.py::test_login_success -v

    # Run with screenshots on failure
    pytest example_tests.py -v --tb=short

    # Run in parallel (requires pytest-xdist)
    pytest example_tests.py -v -n 4
    """
    pytest.main([__file__, "-v"])
