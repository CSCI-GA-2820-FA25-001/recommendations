######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Recommendations Service

This service implements a REST API that allows you to Create, Read, Update,
Delete, and List Recommendations.
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Recommendation, RecommendationType, RecommendationStatus
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    info = {
        "service": "Recommendations Service",
        "version": "1.0",
        "description": (
            "This microservice manages product-to-product recommendations "
            "for the eCommerce platform. It supports Create, Read, Update, "
            "Delete, and List operations for recommendation relationships."
        ),
        "endpoints": {
            "list": "/recommendations",
            "create": "/recommendations",
            "read": "/recommendations/<id>",
            "update": "/recommendations/<id>",
            "delete": "/recommendations/<id>",
        },
        "status": "OK",
    }
    return jsonify(info), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################
######################################################################
# READ A Recommendation
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
def get_recommendations(recommendation_id):
    """
    Retrieve a single Recommendation by ID
    This endpoint will return a Recommendation based on its ID
    """
    app.logger.info("Request for Recommendation with id: %s", recommendation_id)
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id {recommendation_id} not found",
        )

    app.logger.info("Returning recommendation: %s", recommendation.name)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW Recommendation
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Create a Recommendation
    This endpoint will create a Recommendation based the data in the body that is posted
    """
    app.logger.info("Request to Create a Recommendation...")
    check_content_type("application/json")

    recommendation = Recommendation()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    recommendation.deserialize(data)

    # Save the new Recommendation to the database
    recommendation.create()
    app.logger.info("Recommendation with new id [%s] saved!", recommendation.id)

    # Return the location of the new Recommendation
    location_url = url_for(
        "get_recommendations", recommendation_id=recommendation.id, _external=True
    )
    return (
        jsonify(recommendation.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update_recommendations(recommendation_id):
    """
    Update a Recommendation

    This endpoint will update a Recommendation based the body that is posted
    """
    app.logger.info(
        "Request to Update a recommendation with id [%s]", recommendation_id
    )
    check_content_type("application/json")

    # Attempt to find the Recommendation and abort if not found
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    # Update the Recommendation with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    recommendation.deserialize(data)

    # Save the updates to the database
    recommendation.update()

    app.logger.info("Recommendation with ID: %d updated.", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A RECOMMENDATION - YOUR RESPONSIBILITY STARTS HERE
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendations(recommendation_id):
    """
    Delete a Recommendation

    This endpoint will delete a Recommendation based on the id specified in the path
    """
    app.logger.info(
        "Request to Delete a recommendation with id [%s]", recommendation_id
    )

    # Attempt to find the Recommendation and abort if not found
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    # Delete the Recommendation
    recommendation.delete()
    app.logger.info("Recommendation with ID: %d delete complete.", recommendation_id)

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST A RECOMMENDATION - YOUR RESPONSIBILITY STARTS HERE
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """
    List all Recommendations

    This endpoint returns a list of all Recommendations in the database.
    Query parameters can be used to filter the results:
    - product_a_id: Filter by base product ID
    - relationship_type: Filter by recommendation type (e.g., 'accessory', 'cross_sell')
    - status: Filter by status (e.g., 'active', 'inactive')

    Returns:
        200: A JSON array of recommendations (may be empty)
    """
    app.logger.info("Request to list recommendations")

    # Start with base query
    query = Recommendation.query

    # Filter by product_a_id (maps to base_product_id)
    product_a_id = request.args.get("product_a_id", type=int)
    if product_a_id:
        app.logger.info("Filtering by product_a_id: %s", product_a_id)
        query = query.filter(Recommendation.base_product_id == product_a_id)

    # Filter by relationship_type (maps to recommendation_type)
    relationship_type = request.args.get("relationship_type")
    if relationship_type:
        try:
            # Convert string to enum
            type_enum = RecommendationType(relationship_type)
            app.logger.info("Filtering by relationship_type: %s", relationship_type)
            query = query.filter(Recommendation.recommendation_type == type_enum)
        except ValueError:
            # Invalid enum value, log warning but don't filter
            app.logger.warning(
                "Invalid relationship_type value: %s. Ignoring filter.",
                relationship_type,
            )

    # Filter by status
    status_param = request.args.get("status")
    if status_param:
        try:
            # Convert string to enum
            status_enum = RecommendationStatus(status_param)
            app.logger.info("Filtering by status: %s", status_param)
            query = query.filter(Recommendation.status == status_enum)
        except ValueError:
            # Invalid enum value, log warning but don't filter
            app.logger.warning(
                "Invalid status value: %s. Ignoring filter.", status_param
            )

    # Execute query and serialize results
    recommendations = query.all()
    app.logger.info("Found %d recommendations", len(recommendations))

    results = [rec.serialize() for rec in recommendations]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
