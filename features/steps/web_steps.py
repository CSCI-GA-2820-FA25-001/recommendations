"""
Common web interaction steps for BDD testing
"""

from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@given('I am on the home page')
@given('I am on the "{page}" page')
def step_navigate_to_page(context, page="home"):
    """Navigate to a specific page"""
    context.driver.get(context.base_url)
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )


@when('I click the "{button_name}" button')
def step_click_button(context, button_name):
    """Click a button by its ID or visible text"""
    button_id = f"{button_name.lower().replace(' ', '-')}-btn"
    try:
        button = WebDriverWait(context.driver, context.wait_seconds).until(
            EC.element_to_be_clickable((By.ID, button_id))
        )
        button.click()
    except TimeoutException:
        button = context.driver.find_element(
            By.XPATH, 
            f"//button[contains(text(), '{button_name}')]"
        )
        button.click()


@when('I click the "{element_id}" element')
def step_click_element_by_id(context, element_id):
    """Click an element by its ID"""
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.element_to_be_clickable((By.ID, element_id))
    )
    element.click()


@when('I fill in "{field_name}" with "{value}"')
@when('I set the "{field_name}" to "{value}"')
def step_fill_field(context, field_name, value):
    """Fill a text input field with a value"""
    field_id = f"recommendation_{field_name.lower().replace(' ', '_')}"
    field = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, field_id))
    )
    field.clear()
    field.send_keys(value)


@when('I select "{option}" from the "{field_name}" dropdown')
def step_select_dropdown(context, option, field_name):
    """Select an option from a dropdown"""
    field_id = f"recommendation_{field_name.lower().replace(' ', '_')}"
    dropdown = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, field_id))
    )
    select = Select(dropdown)
    select.select_by_value(option)


@when('I clear the form')
def step_clear_form(context):
    """Clear all form fields"""
    clear_button = context.driver.find_element(By.ID, "clear-btn")
    clear_button.click()


@then('I should see "{message}"')
@then('I should see the message "{message}"')
def step_verify_message(context, message):
    """Verify that a specific message is displayed"""
    flash_message = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, "flash_message"))
    )
    assert message.lower() in flash_message.text.lower(), \
        f"Expected message '{message}' not found. Actual: '{flash_message.text}'"


@then('the "{field_name}" field should contain "{value}"')
@then('the "{field_name}" field should be "{value}"')
def step_verify_field_value(context, field_name, value):
    """Verify that a field contains a specific value"""
    field_id = f"recommendation_{field_name.lower().replace(' ', '_')}"
    field = context.driver.find_element(By.ID, field_id)
    actual_value = field.get_attribute("value")
    assert actual_value == value, \
        f"Expected '{value}' but got '{actual_value}'"


@then('I should see a table with recommendation data')
@then('I should see the recommendations table')
def step_verify_table_exists(context):
    """Verify that the recommendations table is displayed"""
    table = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#search_results table"))
    )
    assert table.is_displayed(), "Recommendations table is not visible"


@then('the table should have {count:d} rows')
@then('I should see {count:d} recommendations in the table')
def step_verify_table_row_count(context, count):
    """Verify the number of rows in the recommendations table"""
    rows = context.driver.find_elements(
        By.CSS_SELECTOR, 
        "#search_results table tbody tr"
    )
    actual_count = len(rows)
    assert actual_count == count, \
        f"Expected {count} rows but found {actual_count}"


@then('the table should have columns: {columns}')
def step_verify_table_columns(context, columns):
    """Verify that the table has specific column headers"""
    expected_columns = [col.strip() for col in columns.split(',')]
    headers = context.driver.find_elements(
        By.CSS_SELECTOR, 
        "#search_results table thead th"
    )
    actual_columns = [header.text for header in headers]
    
    for expected in expected_columns:
        assert expected in actual_columns, \
            f"Column '{expected}' not found in table headers"


@then('the page should contain "{text}"')
def step_verify_page_contains_text(context, text):
    """Verify that the page contains specific text"""
    page_source = context.driver.page_source
    assert text in page_source, \
        f"Text '{text}' not found on the page"


@when('I wait for {seconds:d} seconds')
def step_wait(context, seconds):
    """Wait for a specified number of seconds"""
    import time
    time.sleep(seconds)


@when('I wait for the "{element_id}" element to appear')
def step_wait_for_element(context, element_id):
    """Wait for a specific element to appear"""
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
