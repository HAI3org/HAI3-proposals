"""
Base Page Object class that all page objects inherit from.
Provides common functionality for interacting with pages.
"""
from playwright.sync_api import Page, Locator, expect
from typing import Optional
import os
from tests.utils.locator_loader import LocatorLoader


class BasePage:
    """Base class for all page objects."""

    BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")

    # Override in subclass to specify the YAML file for locators
    LOCATORS_YAML: Optional[str] = None
    _locators: Optional[dict] = None

    def __init__(self, page: Page):
        self.page = page
        # Load locators from YAML if specified
        if self.LOCATORS_YAML:
            self._locators = LocatorLoader.get_all_synced_locators(self.LOCATORS_YAML)

    @property
    def url(self) -> str:
        """Override in subclass to define the page URL path."""
        return "/"

    def navigate(self) -> "BasePage":
        """Navigate to the page URL."""
        full_url = f"{self.BASE_URL}{self.url}"
        self.page.goto(full_url)
        return self

    def wait_for_load(self, timeout: int = 30000) -> "BasePage":
        """Wait for the page to be fully loaded."""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        return self

    def get_element(self, selector: str) -> Locator:
        """Get a locator for an element by selector."""
        return self.page.locator(selector)

    def get_by_test_id(self, test_id: str) -> Locator:
        """Get a locator for an element by data-testid attribute."""
        return self.page.get_by_test_id(test_id)

    def get_locator(self, locator_key: str) -> Locator:
        """
        Get a locator by key from the YAML file.
        The key should match the key in the locators section (e.g., 'aqa_welcome_message').
        """
        if not self._locators:
            raise ValueError(f"No LOCATORS_YAML specified for {self.__class__.__name__}")
        testid = self._locators.get(locator_key)
        if not testid:
            raise ValueError(f"Locator key '{locator_key}' not found in {self.LOCATORS_YAML}")
        return self.page.get_by_test_id(testid)

    def get_by_role(self, role: str, name: Optional[str] = None) -> Locator:
        """Get a locator for an element by ARIA role."""
        if name:
            return self.page.get_by_role(role, name=name)
        return self.page.get_by_role(role)

    def get_by_text(self, text: str, exact: bool = False) -> Locator:
        """Get a locator for an element by text content."""
        return self.page.get_by_text(text, exact=exact)

    def click(self, selector: str) -> "BasePage":
        """Click an element by selector."""
        self.page.locator(selector).click()
        return self

    def fill(self, selector: str, value: str) -> "BasePage":
        """Fill an input field by selector."""
        self.page.locator(selector).fill(value)
        return self

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if an element is visible."""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element(self, selector: str, timeout: int = 30000) -> Locator:
        """Wait for an element to be visible and return its locator."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator

    def expect_visible(self, selector: str) -> None:
        """Assert that an element is visible."""
        expect(self.page.locator(selector)).to_be_visible()

    def expect_text(self, selector: str, text: str) -> None:
        """Assert that an element contains specific text."""
        expect(self.page.locator(selector)).to_contain_text(text)

    def expect_url_contains(self, path: str) -> None:
        """Assert that the current URL contains a path."""
        expect(self.page).to_have_url(f"*{path}*")

    def take_screenshot(self, name: str) -> str:
        """Take a screenshot and return the path."""
        path = f"tests/screenshots/{name}.png"
        self.page.screenshot(path=path)
        return path

    def get_title(self) -> str:
        """Get the page title."""
        return self.page.title()
