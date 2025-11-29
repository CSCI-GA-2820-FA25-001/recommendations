"""
Business-specific step definitions for Recommendations testing
"""

import os
from behave import given, when, then
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
    rest_endpoint = f"{context.base_url}/api/recommendations"
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
            "name": row["name"],
            "base_product_id": int(row["base_product_id"]),
            "recommended_product_id": int(row["recommended_product_id"]),
            "recommendation_type": row["recommendation_type"],
            "status": row["status"],
            "likes": int(row["likes"] or 0),
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
