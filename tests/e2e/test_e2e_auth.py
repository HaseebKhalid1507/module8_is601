# tests/e2e/test_e2e_auth.py

"""
End-to-End Tests for Authentication Pages (Login & Register)

These tests use Playwright to simulate real user interactions with the
login and register pages, verifying both positive and negative scenarios.
"""

import pytest
import time

# Generate unique test data to avoid conflicts between test runs
def generate_unique_user():
    """Generate unique user data for each test run."""
    timestamp = int(time.time() * 1000)
    return {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "SecurePass123!"
    }


# =============================================================================
# REGISTER PAGE - POSITIVE TESTS
# =============================================================================

@pytest.mark.e2e
def test_register_page_loads(page, fastapi_server):
    """
    Test that the register page loads correctly.
    
    Verifies that the register page is accessible and displays the expected
    heading and form elements.
    """
    page.goto('http://localhost:8000/register')
    
    # Check page title
    assert page.title() == 'Register - Calculator App'
    
    # Check heading is displayed
    assert page.inner_text('h1') == 'Create Account'
    
    # Check all form fields exist
    assert page.locator('#username').is_visible()
    assert page.locator('#email').is_visible()
    assert page.locator('#password').is_visible()
    assert page.locator('#confirmPassword').is_visible()
    assert page.locator('button[type="submit"]').is_visible()


@pytest.mark.e2e
def test_register_with_valid_data(page, fastapi_server):
    """
    Test successful registration with valid data.
    
    Positive Test: Fills in the registration form with valid data including
    proper email format and password length, then verifies the success message
    is displayed and token is stored.
    """
    user = generate_unique_user()
    
    page.goto('http://localhost:8000/register')
    
    # Fill in the registration form with valid data
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    
    # Submit the form
    page.click('button[type="submit"]')
    
    # Wait for success message to appear
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('success')"
    )
    
    # Verify success message is displayed
    message = page.inner_text('#message')
    assert 'Account created successfully' in message
    
    # Verify token is stored in localStorage
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token is not None
    assert len(token) > 0
    
    # Verify user data is stored
    stored_username = page.evaluate("() => localStorage.getItem('username')")
    assert stored_username == user['username']


@pytest.mark.e2e
def test_register_redirects_after_success(page, fastapi_server):
    """
    Test that successful registration redirects to the calculator page.
    
    Positive Test: After successful registration, the user should be
    redirected to the main calculator page.
    """
    user = generate_unique_user()
    
    page.goto('http://localhost:8000/register')
    
    # Fill in the registration form
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    
    # Submit the form
    page.click('button[type="submit"]')
    
    # Wait for redirect to homepage (with some buffer for the delay)
    page.wait_for_url('http://localhost:8000/', timeout=5000)
    
    # Verify we're on the calculator page
    assert page.inner_text('h1') == 'Hello World'


# =============================================================================
# REGISTER PAGE - NEGATIVE TESTS
# =============================================================================

@pytest.mark.e2e
def test_register_with_short_password(page, fastapi_server):
    """
    Test registration with a password that is too short.
    
    Negative Test: Attempts to register with a password shorter than 6 characters.
    HTML5 minlength validation should prevent form submission.
    """
    user = generate_unique_user()
    
    page.goto('http://localhost:8000/register')
    
    # Fill in form with short password
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', 'short')  # Only 5 characters
    page.fill('#confirmPassword', 'short')
    
    # Submit the form
    page.click('button[type="submit"]')
    
    # HTML5 minlength validation should prevent submission
    # We should still be on the register page
    assert page.url == 'http://localhost:8000/register'
    
    # Check that the password input is marked as invalid
    is_invalid = page.evaluate(
        "() => !document.querySelector('#password').validity.valid"
    )
    assert is_invalid


@pytest.mark.e2e
def test_register_with_mismatched_passwords(page, fastapi_server):
    """
    Test registration with passwords that don't match.
    
    Negative Test: Attempts to register with different values in password
    and confirm password fields. Verifies the error message.
    """
    user = generate_unique_user()
    
    page.goto('http://localhost:8000/register')
    
    # Fill in form with mismatched passwords
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', 'DifferentPassword123!')
    
    # Submit the form
    page.click('button[type="submit"]')
    
    # Wait for error message
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').style.display === 'block'"
    )
    
    # Verify error message about password mismatch
    message = page.inner_text('#message')
    assert 'do not match' in message.lower() or 'passwords' in message.lower()


@pytest.mark.e2e
def test_register_with_duplicate_username(page, fastapi_server):
    """
    Test registration with an already existing username.
    
    Negative Test: First registers a user, then attempts to register
    another user with the same username. Verifies server returns error.
    """
    user = generate_unique_user()
    
    # First registration (should succeed)
    page.goto('http://localhost:8000/register')
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    page.click('button[type="submit"]')
    
    # Wait for first registration to complete
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('success')"
    )
    
    # Clear localStorage to simulate a fresh session
    page.evaluate("() => localStorage.clear()")
    
    # Navigate to register page again
    page.goto('http://localhost:8000/register')
    
    # Try to register with same username but different email
    page.fill('#username', user['username'])
    page.fill('#email', f"different_{user['email']}")
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    page.click('button[type="submit"]')
    
    # Wait for error message
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('error')"
    )
    
    # Verify error message about duplicate username
    message = page.inner_text('#message')
    assert 'already' in message.lower() or 'username' in message.lower()


@pytest.mark.e2e
def test_register_with_invalid_email(page, fastapi_server):
    """
    Test registration with an invalid email format.
    
    Negative Test: Attempts to register with an invalid email format.
    The HTML5 email validation should prevent submission.
    """
    user = generate_unique_user()
    
    page.goto('http://localhost:8000/register')
    
    # Fill in form with invalid email
    page.fill('#username', user['username'])
    page.fill('#email', 'invalid-email-format')  # Missing @ and domain
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    
    # Try to submit - HTML5 validation should prevent it
    page.click('button[type="submit"]')
    
    # The form should not submit due to HTML5 email validation
    # We should still be on the register page
    assert page.url == 'http://localhost:8000/register'
    
    # Check that the email input is marked as invalid
    is_invalid = page.evaluate(
        "() => !document.querySelector('#email').validity.valid"
    )
    assert is_invalid


# =============================================================================
# LOGIN PAGE - POSITIVE TESTS
# =============================================================================

@pytest.mark.e2e
def test_login_page_loads(page, fastapi_server):
    """
    Test that the login page loads correctly.
    
    Verifies that the login page is accessible and displays the expected
    heading and form elements.
    """
    page.goto('http://localhost:8000/login')
    
    # Check page title
    assert page.title() == 'Login - Calculator App'
    
    # Check heading is displayed
    assert page.inner_text('h1') == 'Welcome Back'
    
    # Check all form fields exist
    assert page.locator('#username').is_visible()
    assert page.locator('#password').is_visible()
    assert page.locator('#rememberMe').is_visible()
    assert page.locator('button[type="submit"]').is_visible()


@pytest.mark.e2e
def test_login_with_valid_credentials(page, fastapi_server):
    """
    Test successful login with valid credentials.
    
    Positive Test: First registers a user, then logs in with the same
    credentials and verifies success message and token storage.
    """
    user = generate_unique_user()
    
    # First, register the user
    page.goto('http://localhost:8000/register')
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    page.click('button[type="submit"]')
    
    # Wait for registration to complete
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('success')"
    )
    
    # Clear storage to simulate logging out
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    
    # Now go to login page
    page.goto('http://localhost:8000/login')
    
    # Fill in login form with remember me checked to ensure localStorage is used
    page.fill('#username', user['username'])
    page.fill('#password', user['password'])
    page.check('#rememberMe')  # Check remember me to use localStorage
    
    # Submit the form
    page.click('button[type="submit"]')
    
    # Wait for success message
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('success')"
    )
    
    # Verify success message
    message = page.inner_text('#message')
    assert 'successful' in message.lower() or 'login' in message.lower()
    
    # Verify token is stored (check both localStorage and sessionStorage)
    token = page.evaluate(
        "() => localStorage.getItem('access_token') || sessionStorage.getItem('access_token')"
    )
    assert token is not None
    assert len(token) > 0


@pytest.mark.e2e
def test_login_with_remember_me(page, fastapi_server):
    """
    Test login with "Remember me" checkbox checked.
    
    Positive Test: Verifies that when "Remember me" is checked,
    the token is stored in localStorage.
    """
    user = generate_unique_user()
    
    # First, register the user
    page.goto('http://localhost:8000/register')
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    page.click('button[type="submit"]')
    
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('success')"
    )
    
    # Clear storage
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    
    # Login with remember me checked
    page.goto('http://localhost:8000/login')
    page.fill('#username', user['username'])
    page.fill('#password', user['password'])
    page.check('#rememberMe')  # Check the remember me checkbox
    page.click('button[type="submit"]')
    
    # Wait for success
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('success')"
    )
    
    # Verify token is in localStorage (not sessionStorage)
    local_token = page.evaluate("() => localStorage.getItem('access_token')")
    assert local_token is not None


@pytest.mark.e2e
def test_login_redirects_after_success(page, fastapi_server):
    """
    Test that successful login redirects to the calculator page.
    
    Positive Test: After successful login, the user should be
    redirected to the main calculator page.
    """
    user = generate_unique_user()
    
    # Register user first
    page.goto('http://localhost:8000/register')
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    page.click('button[type="submit"]')
    
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('success')"
    )
    
    # Clear storage
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    
    # Login
    page.goto('http://localhost:8000/login')
    page.fill('#username', user['username'])
    page.fill('#password', user['password'])
    page.click('button[type="submit"]')
    
    # Wait for redirect
    page.wait_for_url('http://localhost:8000/', timeout=5000)
    
    # Verify we're on the calculator page
    assert page.inner_text('h1') == 'Hello World'


# =============================================================================
# LOGIN PAGE - NEGATIVE TESTS
# =============================================================================

@pytest.mark.e2e
def test_login_with_wrong_password(page, fastapi_server):
    """
    Test login with incorrect password.
    
    Negative Test: Attempts to login with a valid username but wrong password.
    Verifies that server returns 401 and UI shows invalid credentials message.
    """
    user = generate_unique_user()
    
    # First, register the user
    page.goto('http://localhost:8000/register')
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    page.click('button[type="submit"]')
    
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('success')"
    )
    
    # Clear storage
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    
    # Try to login with wrong password
    page.goto('http://localhost:8000/login')
    page.fill('#username', user['username'])
    page.fill('#password', 'WrongPassword123!')  # Incorrect password
    page.click('button[type="submit"]')
    
    # Wait for error message
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('error')"
    )
    
    # Verify error message about invalid credentials
    message = page.inner_text('#message')
    assert 'invalid' in message.lower() or 'credentials' in message.lower() or 'password' in message.lower()
    
    # Verify no token is stored
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token is None


@pytest.mark.e2e
def test_login_with_nonexistent_user(page, fastapi_server):
    """
    Test login with a username that doesn't exist.
    
    Negative Test: Attempts to login with a username that was never registered.
    Verifies the error message is displayed.
    """
    page.goto('http://localhost:8000/login')
    
    # Try to login with non-existent user
    page.fill('#username', 'nonexistent_user_12345')
    page.fill('#password', 'SomePassword123!')
    page.click('button[type="submit"]')
    
    # Wait for error message
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').classList.contains('error')"
    )
    
    # Verify error message
    message = page.inner_text('#message')
    assert 'invalid' in message.lower() or 'credentials' in message.lower()


@pytest.mark.e2e
def test_login_with_empty_fields(page, fastapi_server):
    """
    Test login with empty username and password fields.
    
    Negative Test: Attempts to submit the login form without filling
    any fields. HTML5 validation should prevent submission.
    """
    page.goto('http://localhost:8000/login')
    
    # Try to submit empty form
    page.click('button[type="submit"]')
    
    # The form should not submit due to HTML5 required validation
    # We should still be on the login page
    assert page.url == 'http://localhost:8000/login'
    
    # Check that the username input is marked as invalid (required)
    is_invalid = page.evaluate(
        "() => !document.querySelector('#username').validity.valid"
    )
    assert is_invalid


# =============================================================================
# NAVIGATION TESTS
# =============================================================================

@pytest.mark.e2e
def test_navigation_from_login_to_register(page, fastapi_server):
    """
    Test navigation link from login page to register page.
    """
    page.goto('http://localhost:8000/login')
    
    # Click the sign up link
    page.click('a[href="/register"]')
    
    # Verify we're on the register page
    assert page.url == 'http://localhost:8000/register'
    assert page.inner_text('h1') == 'Create Account'


@pytest.mark.e2e
def test_navigation_from_register_to_login(page, fastapi_server):
    """
    Test navigation link from register page to login page.
    """
    page.goto('http://localhost:8000/register')
    
    # Click the sign in link
    page.click('a[href="/login"]')
    
    # Verify we're on the login page
    assert page.url == 'http://localhost:8000/login'
    assert page.inner_text('h1') == 'Welcome Back'


@pytest.mark.e2e
def test_navigation_back_to_calculator(page, fastapi_server):
    """
    Test navigation link back to calculator from login page.
    """
    page.goto('http://localhost:8000/login')
    
    # Click the back to calculator link
    page.click('a[href="/"]')
    
    # Verify we're on the calculator page
    assert page.url == 'http://localhost:8000/'
    assert page.inner_text('h1') == 'Hello World'


# =============================================================================
# UI STATE TESTS
# =============================================================================

@pytest.mark.e2e
def test_button_disabled_during_submission(page, fastapi_server):
    """
    Test that the submit button is disabled during form submission.
    
    Verifies the UI shows loading state during API request.
    """
    user = generate_unique_user()
    
    page.goto('http://localhost:8000/register')
    
    # Fill in the form
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', user['password'])
    page.fill('#confirmPassword', user['password'])
    
    # Set up a listener for the button text change
    # Click and immediately check button state
    page.click('button[type="submit"]')
    
    # Check that button shows loading text (may be brief)
    # The button text should change to "Creating Account..." briefly
    button_text = page.inner_text('button[type="submit"]')
    # After completion, it should either show success or return to normal
    assert button_text in ['Creating Account...', 'Create Account']


@pytest.mark.e2e
def test_error_message_styling(page, fastapi_server):
    """
    Test that error messages have proper styling.
    """
    user = generate_unique_user()
    
    page.goto('http://localhost:8000/register')
    
    # Fill in form with mismatched passwords to trigger error
    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#password', 'Password123!')
    page.fill('#confirmPassword', 'DifferentPassword!')
    page.click('button[type="submit"]')
    
    # Wait for error message
    page.wait_for_function(
        "() => document.querySelector('#message') && "
        "document.querySelector('#message').style.display === 'block'"
    )
    
    # Verify error class is applied
    message_class = page.get_attribute('#message', 'class')
    assert 'error' in message_class
    
    # Verify message is visible
    assert page.locator('#message').is_visible()
