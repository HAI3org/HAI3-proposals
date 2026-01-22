# Python BDD Test Framework

This directory contains the Python BDD test framework using pytest-bdd and Playwright.

## Prerequisites

Before running tests, ensure the following are in place:

**App is running**: `npm run dev` (default: http://localhost:5173)
**Virtual environment exists**: `venv/` at project root
**Dependencies installed in venv**: See setup below

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r tests/requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with HTML report
pytest tests/ --html=report.html

# Run specific feature
pytest tests/features/test_any_example_screen.py

# Run by marker
pytest tests/ -m smoke
pytest tests/ -m regression

# Run with headed browser (visible)
pytest tests/ --headed

# Run specific browser
pytest tests/ --browser chromium
pytest tests/ --browser firefox
pytest tests/ --browser webkit
```

## Structure

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── pytest.ini            # Pytest settings
├── requirements.txt      # Python dependencies
├── features/             # BDD feature files and test modules
│   ├── *.feature         # Gherkin feature files
│   └── test_*.py         # Test modules linking features to steps
├── pages/                # Page Object classes
│   ├── __init__.py
│   └── base_page.py      # Base page object with common methods
└── steps/                # Step definitions
    ├── __init__.py
    └── common_steps.py   # Reusable step definitions
```

## Creating Tests for New Pages

Use the `/generatetests` workflow or follow these steps:

1. **Create Page Object** in `tests/pages/{screen_name}_page.py`
2. **Create Feature File** in `tests/features/{screen_name}.feature`
3. **Create Test Module** in `tests/features/test_{screen_name}.py`
4. **Add Screen-Specific Steps** in `tests/steps/{screen_name}_steps.py` (if needed)

## Environment Variables

- `BASE_URL`: Application URL (default: `http://localhost:5173`)

## AI-Assisted Test Development

> **Recommended models**: Claude Opus or Claude Sonnet (latest versions) for best results.

When using an AI assistant to implement new UI features with tests, use a prompt like this:

```
Create and implement a "Web Search" button on the /{target_page} page.

Requirements:
1. Create OpenSpec change proposal (add-web-search-button)
2. Add a button with:
   - Text: "Web Search"
   - data-testid="{target_page}-web-search-button"
   - Appropriate icon (e.g., search/globe icon)
3. Follow SCREENSETS.md rules:
   - Update tests/locators/{target_page}.yaml with the new data-testid
4. Create/update BDD tests following TESTING.md:
   - Update Page Object in tests/pages/{target_page}_page.py (add web_search_button property)
   - Add scenario to tests/features/{target_page}.feature for button visibility
   - Update test module if needed
5. Execute tests with --headed to verify all pass
6. Mark tasks complete in tasks.md
```

This ensures the AI follows the project's conventions for OpenSpec proposals, locator management, and BDD testing.
