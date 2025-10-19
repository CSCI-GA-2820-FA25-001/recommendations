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
# Helper functions for list_recommendations
######################################################################
def _apply_filters(query):
    """Apply query parameter filters to the query"""
    # Filter by product_a_id (maps to base_product_id)
    product_a_id = request.args.get("product_a_id", type=int)
    if product_a_id:
        app.logger.info("Filtering by product_a_id: %s", product_a_id)
        query = query.filter(Recommendation.base_product_id == product_a_id)

    # Filter by relationship_type
    query = _apply_relationship_type_filter(query)

    # Filter by status
    query = _apply_status_filter(query)

    return query


def _apply_relationship_type_filter(query):
    """Apply relationship_type filter to query"""
    relationship_type = request.args.get("relationship_type")
    if not relationship_type:
        return query

    try:
        type_enum = RecommendationType(relationship_type)
        app.logger.info("Filtering by relationship_type: %s", relationship_type)
        return query.filter(Recommendation.recommendation_type == type_enum)
    except ValueError:
        app.logger.warning(
            "Invalid relationship_type value: %s. Ignoring filter.",
            relationship_type,
        )
        return query


def _apply_status_filter(query):
    """Apply status filter to query"""
    status_param = request.args.get("status")
    if not status_param:
        return query

    try:
        status_enum = RecommendationStatus(status_param)
        app.logger.info("Filtering by status: %s", status_param)
        return query.filter(Recommendation.status == status_enum)
    except ValueError:
        app.logger.warning(
            "Invalid status value: %s. Ignoring filter.", status_param
        )
        return query


def _validate_and_get_pagination():
    """Validate and return pagination parameters"""
    limit = request.args.get("limit", default=20, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if limit < 1 or limit > 100:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Invalid limit parameter. Must be between 1 and 100.",
        )
    if offset < 0:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Invalid offset parameter. Must be non-negative.",
        )

    return limit, offset


def _apply_sorting(query):
    """Apply sorting to query based on sort parameter"""
    sort_param = request.args.get("sort")
    valid_sort_fields = {
        "created_at_asc": Recommendation.created_at.asc(),
        "created_at_desc": Recommendation.created_at.desc(),
        "name_asc": Recommendation.name.asc(),
        "name_desc": Recommendation.name.desc(),
        "id_asc": Recommendation.id.asc(),
        "id_desc": Recommendation.id.desc(),
    }

    if sort_param:
        if sort_param not in valid_sort_fields:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid sort parameter. Valid options: {', '.join(valid_sort_fields.keys())}",
            )
        app.logger.info("Sorting by: %s", sort_param)
        return query.order_by(valid_sort_fields[sort_param])

    # Default sort by id
    return query.order_by(Recommendation.id.asc())


######################################################################
# LIST A RECOMMENDATION - YOUR RESPONSIBILITY STARTS HERE
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """
    List all Recommendations

    This endpoint returns a list of all Recommendations in the database.
    Query parameters can be used to filter, paginate, and sort the results:
    - product_a_id: Filter by base product ID
    - relationship_type: Filter by recommendation type (e.g., 'accessory', 'cross_sell')
    - status: Filter by status (e.g., 'active', 'inactive')
    - limit: Number of results to return (default 20, max 100)
    - offset: Number of results to skip (default 0)
    - sort: Sort order (e.g., 'created_at_asc', 'created_at_desc', 'name_asc', 'name_desc')

    Returns:
        200: A JSON object with recommendations array and pagination metadata
        400: Bad request if invalid parameters provided
    """
    app.logger.info("Request to list recommendations")

    # Build query with filters and sorting
    query = Recommendation.query
    query = _apply_filters(query)
    query = _apply_sorting(query)

    # Get and validate pagination
    limit, offset = _validate_and_get_pagination()

    # Get total count and execute query
    total_count = query.count()
    recommendations = query.limit(limit).offset(offset).all()

    app.logger.info(
        "Found %d recommendations (total: %d, limit: %d, offset: %d)",
        len(recommendations),
        total_count,
        limit,
        offset,
    )

    # Build response
    results = [rec.serialize() for rec in recommendations]
    response = {
        "recommendations": results,
        "meta": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "count": len(results),
        },
    }
    return jsonify(response), status.HTTP_200_OK


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
