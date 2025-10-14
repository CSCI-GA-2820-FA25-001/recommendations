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


# Todo: Place your REST API code here ...
