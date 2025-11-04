# tests/e2e/test_e2e_calculator.py

import pytest


@pytest.mark.e2e
def test_calculator_subtract(page, fastapi_server):
    page.goto('http://localhost:8000')
    page.fill('#a', '10')
    page.fill('#b', '5')
    page.click('button:text("Subtract")')
    assert page.inner_text('#result') == 'Calculation Result: 5'


@pytest.mark.e2e
def test_calculator_multiply(page, fastapi_server):
    page.goto('http://localhost:8000')
    page.fill('#a', '10')
    page.fill('#b', '5')
    page.click('button:text("Multiply")')
    page.wait_for_function(
        "() => document.querySelector('#result') && document.querySelector('#result').innerText.includes('Calculation Result: 50')"
    )
    assert page.inner_text('#result') == 'Calculation Result: 50'


@pytest.mark.e2e
@pytest.mark.parametrize("a,b", [("", "5"), ("5", "")])
def test_missing_input_shows_error(page, fastapi_server, a, b):
    """Missing one of the inputs should result in an error being displayed."""
    page.goto('http://localhost:8000')
    if a != "":
        page.fill('#a', a)
    if b != "":
        page.fill('#b', b)
    page.click('button:text("Add")')
    assert page.inner_text('#result').startswith('Error: ')
