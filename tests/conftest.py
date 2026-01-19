"""
Pytest configuration and fixtures for BDD tests.
"""
import pytest
from playwright.sync_api import Page, Browser, BrowserContext
from typing import Generator
import os

# Base URL for the application
BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Configure browser context with viewport and other settings."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture
def app_page(page: Page) -> Generator[Page, None, None]:
    """Fixture that provides a page navigated to the app base URL."""
    page.goto(BASE_URL)
    yield page


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the application."""
    return BASE_URL
