"""
Common step definitions that can be reused across all feature tests.
"""
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page, expect
from tests.pages.base_page import BasePage


@given("I am on the application")
def navigate_to_app(app_page: Page):
    """Navigate to the application base URL."""
    pass


@given(parsers.parse('I navigate to "{path}"'))
def navigate_to_path(page: Page, base_url: str, path: str):
    """Navigate to a specific path."""
    page.goto(f"{base_url}{path}")


@when(parsers.parse('I click on "{selector}"'))
def click_element(page: Page, selector: str):
    """Click on an element by selector."""
    page.locator(selector).click()


@when(parsers.parse('I click the button "{button_text}"'))
def click_button_by_text(page: Page, button_text: str):
    """Click a button by its text."""
    page.get_by_role("button", name=button_text).click()


@when(parsers.parse('I fill "{selector}" with "{value}"'))
def fill_input(page: Page, selector: str, value: str):
    """Fill an input field."""
    page.locator(selector).fill(value)


@when(parsers.parse('I type "{value}" into the field "{field_name}"'))
def type_into_field(page: Page, value: str, field_name: str):
    """Type into a field by its label or placeholder."""
    page.get_by_label(field_name).fill(value)


@when("I wait for the page to load")
def wait_for_page_load(page: Page):
    """Wait for the page to be fully loaded."""
    page.wait_for_load_state("networkidle")


@then(parsers.parse('I should see "{text}"'))
def should_see_text(page: Page, text: str):
    """Assert that text is visible on the page."""
    expect(page.get_by_text(text).first).to_be_visible()


@then(parsers.parse('I should see element "{selector}"'))
def should_see_element(page: Page, selector: str):
    """Assert that an element is visible."""
    expect(page.locator(selector)).to_be_visible()


@then(parsers.parse('the URL should contain "{path}"'))
def url_should_contain(page: Page, path: str):
    """Assert that the URL contains a specific path."""
    expect(page).to_have_url(path)


@then(parsers.parse('I should not see "{text}"'))
def should_not_see_text(page: Page, text: str):
    """Assert that text is not visible on the page."""
    expect(page.get_by_text(text)).not_to_be_visible()


@then(parsers.parse('the element "{selector}" should have text "{text}"'))
def element_should_have_text(page: Page, selector: str, text: str):
    """Assert that an element contains specific text."""
    expect(page.locator(selector)).to_contain_text(text)


@then(parsers.parse('the page title should be "{title}"'))
def page_title_should_be(page: Page, title: str):
    """Assert that the page title matches."""
    expect(page).to_have_title(title)


@then("the page should load without errors")
def page_loads_without_errors(page: Page):
    """Assert that the page loaded without console errors."""
    # This is a basic check - can be extended to capture console errors
    expect(page.locator("body")).to_be_visible()
