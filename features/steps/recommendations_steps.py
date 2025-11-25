"""
Business-specific step definitions for Recommendations testing
"""

import os
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from service.models import Recommendation, RecommendationType, RecommendationStatus
import requests
from compare3 import expect


# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following recommendations")
def step_impl(context):
    """Delete all Recommendations and load new ones"""

    # Get a list all of the recommendations
    rest_endpoint = f"{context.base_url}/recommendations"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for recommendation in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{recommendation['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new recommendations
    for row in context.table:
        payload = {
            "Name": row["Name"],
            "Base Product ID": row["Base Product ID"],
            "Recommended Product ID": row["Recommended Product ID"],
            "Recommendation Type": row["Recommendation Type"] in RecommendationType,
            "Status": row["Recommendation Type"] in RecommendationStatus,
            "Likes": row["Likes"],
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given("the server is started")
def step_impl(context):
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080")
    context.resp = requests.get(context.base_url + "/")
    print(context.resp.text)
    assert context.resp.status_code == 200


# @when('I visit the "home page"')
# def step_impl(context):
#     context.resp = requests.get(context.base_url + "/")
#     assert context.resp.status_code == 200


# @then('I should see "{message}"')
# def step_impl(context, message):
#     """I should see a message"""
#     assert message in str(context.resp.text)

# @then('I should not see "{message}"')
# def step_impl(context, message):
#     """I should not see a message"""
#     assert message not in str(context.resp.text)


# @given("the recommendations service is running")
# def step_service_is_running(context):
#     """Verify that the recommendations service is accessible"""
#     try:
#         response = requests.get(f"{context.base_url}/health", timeout=5)
#         assert (
#             response.status_code == 200
#         ), f"Service health check failed with status {response.status_code}"
#     except requests.exceptions.RequestException as e:
#         raise AssertionError(f"Service is not running: {e}")


# @given('a recommendation exists with ID "{rec_id}"')
# def step_recommendation_exists(context, rec_id):
#     """Verify that a recommendation with specific ID exists"""
#     response = requests.get(f"{context.base_url}/recommendations/{rec_id}")
#     assert response.status_code == 200, f"Recommendation {rec_id} does not exist"
#     context.recommendation = response.json()


# @given("no recommendations exist")
# @given("the database is empty")
# def step_no_recommendations_exist(context):
#     """Ensure the database has no recommendations"""
#     # Note: This step assumes you have a way to clear the database
#     # For now, we just verify the list is empty or skip this check
#     response = requests.get(f"{context.base_url}/recommendations")
#     recommendations = response.json()
#     context.initial_count = (
#         len(recommendations) if isinstance(recommendations, list) else 0
#     )


# @given("{count:d} recommendations exist")
# def step_multiple_recommendations_exist(context, count):
#     """Verify that a specific number of recommendations exist"""
#     response = requests.get(f"{context.base_url}/recommendations")
#     recommendations = response.json()
#     actual_count = len(recommendations) if isinstance(recommendations, list) else 0
#     assert (
#         actual_count >= count
#     ), f"Expected at least {count} recommendations but found {actual_count}"


# @when(
#     'I create a recommendation with base product "{base_id}" and recommended product "{rec_id}"'
# )
# def step_create_recommendation(context, base_id, rec_id):
#     """Create a new recommendation via the UI"""
#     # Fill in the form fields
#     context.execute_steps(
#         f"""
#         When I fill in "name" with "Test Recommendation"
#         And I fill in "base_product_id" with "{base_id}"
#         And I fill in "recommended_product_id" with "{rec_id}"
#         And I select "cross_sell" from the "recommendation_type" dropdown
#         And I select "active" from the "status" dropdown
#         And I fill in "likes" with "0"
#         And I click the "Create" button
#     """
#     )


# @when("I list all recommendations")
# def step_list_recommendations(context):
#     """Click the List button to display all recommendations"""
#     context.execute_steps(
#         """
#         When I click the "List" button
#     """
#     )


# @when('I retrieve recommendation "{rec_id}"')
# @when('I retrieve the recommendation with ID "{rec_id}"')
# def step_retrieve_recommendation(context, rec_id):
#     """Retrieve a specific recommendation by ID via the UI"""
#     context.execute_steps(
#         f"""
#         When I fill in "id" with "{rec_id}"
#         And I click the "Retrieve" button
#     """
#     )


# @when('I update the recommendation name to "{new_name}"')
# def step_update_recommendation_name(context, new_name):
#     """Update the name field and save the recommendation"""
#     context.execute_steps(
#         f"""
#         When I fill in "name" with "{new_name}"
#         And I click the "Update" button
#     """
#     )


# @when("I delete the recommendation")
# @when('I delete recommendation "{rec_id}"')
# def step_delete_recommendation(context, rec_id=None):
#     """Delete a recommendation via the UI"""
#     if rec_id:
#         context.execute_steps(
#             f"""
#             When I fill in "id" with "{rec_id}"
#         """
#         )
#     context.execute_steps(
#         """
#         When I click the "Delete" button
#     """
#     )


# @when('I filter recommendations by base_product_id "{product_id}"')
# def step_filter_by_base_product(context, product_id):
#     """Filter recommendations by base product ID"""
#     context.execute_steps(
#         f"""
#         When I fill in "base_product_id" with "{product_id}"
#         And I click the "Search" button
#     """
#     )


# @when('I filter recommendations by status "{status}"')
# def step_filter_by_status(context, status):
#     """Filter recommendations by status"""
#     context.execute_steps(
#         f"""
#         When I select "{status}" from the "status" dropdown
#         And I click the "Search" button
#     """
#     )


# @when('I filter recommendations by type "{rec_type}"')
# def step_filter_by_type(context, rec_type):
#     """Filter recommendations by recommendation type"""
#     context.execute_steps(
#         f"""
#         When I select "{rec_type}" from the "recommendation_type" dropdown
#         And I click the "Search" button
#     """
#     )


# @then('the recommendation should have type "{rec_type}"')
# def step_verify_recommendation_type(context, rec_type):
#     """Verify the recommendation type field value"""
#     context.execute_steps(
#         f"""
#         Then the "recommendation_type" field should contain "{rec_type}"
#     """
#     )


# @then('the recommendation should have status "{status}"')
# def step_verify_recommendation_status(context, status):
#     """Verify the recommendation status field value"""
#     context.execute_steps(
#         f"""
#         Then the "status" field should contain "{status}"
#     """
#     )


# @then('the recommendation should have base product ID "{product_id}"')
# def step_verify_base_product_id(context, product_id):
#     """Verify the base product ID field value"""
#     context.execute_steps(
#         f"""
#         Then the "base_product_id" field should contain "{product_id}"
#     """
#     )


# @then("each recommendation should display correct data")
# @then("the table should contain valid recommendation data")
# def step_verify_table_data(context):
#     """Verify that the recommendations table contains valid data"""
#     # Get all table rows
#     rows = context.driver.find_elements(
#         By.CSS_SELECTOR, "#search_results table tbody tr"
#     )

#     assert len(rows) > 0, "No recommendations found in table"

#     # Verify each row has the expected number of columns
#     for row in rows:
#         cells = row.find_elements(By.TAG_NAME, "td")
#         assert len(cells) >= 7, f"Expected at least 7 columns but found {len(cells)}"

#         # Verify ID is a number
#         rec_id = cells[0].text
#         assert rec_id.isdigit(), f"Invalid ID: {rec_id}"


# @then("the new recommendation should appear in the table")
# @then("the recommendation should appear in the list")
# def step_verify_recommendation_in_table(context):
#     """Verify that a recommendation appears in the table"""
#     # Wait for table to update
#     WebDriverWait(context.driver, context.wait_seconds).until(
#         EC.presence_of_element_located(
#             (By.CSS_SELECTOR, "#search_results table tbody tr")
#         )
#     )

#     # Verify table has at least one row
#     rows = context.driver.find_elements(
#         By.CSS_SELECTOR, "#search_results table tbody tr"
#     )
#     assert len(rows) > 0, "No recommendations found in table after creation"


# @then("the table should be empty")
# @then("I should see an empty table")
# def step_verify_empty_table(context):
#     """Verify that the recommendations table is empty"""
#     rows = context.driver.find_elements(
#         By.CSS_SELECTOR, "#search_results table tbody tr"
#     )
#     assert len(rows) == 0, f"Expected empty table but found {len(rows)} rows"


# @then("I should see a success message")
# def step_verify_success_message(context):
#     """Verify that a success message is displayed"""
#     flash_message = WebDriverWait(context.driver, context.wait_seconds).until(
#         EC.presence_of_element_located((By.ID, "flash_message"))
#     )
#     message_text = flash_message.text.lower()
#     assert (
#         "success" in message_text
#         or "created" in message_text
#         or "updated" in message_text
#     ), f"Expected success message but got: {flash_message.text}"
