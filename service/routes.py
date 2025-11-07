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
from datetime import datetime
import uuid
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Recommendation, RecommendationType, RecommendationStatus
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


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
# H E A L T H   C H E C K
######################################################################
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return {"status": "OK"}, status.HTTP_200_OK


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
# UPDATE AN EXISTING RECOMMENDATION
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
            status.HTTP_204_NO_CONTENT,
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
    # Support both ?product_a_id= and ?base_product_id= as filters on base_product_id
    product_a_id = request.args.get("product_a_id", type=int)
    base_product_id = request.args.get("base_product_id", type=int)

    # If either is provided, use it to filter by Recommendation.base_product_id
    filter_id = product_a_id if product_a_id is not None else base_product_id
    if filter_id is not None:
        app.logger.info("Filtering by base_product_id: %s", filter_id)
        query = query.filter(Recommendation.base_product_id == filter_id)

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
        app.logger.warning("Invalid status value: %s. Ignoring filter.", status_param)
        return query


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

    This endpoint returns a list of Recommendations in the database.
    Query parameters can be used to filter the results:
    - base_product_id / product_a_id
    - relationship_type
    - status
    - sort (optional, if you keep _apply_sorting)

    Returns:
        200: JSON array of recommendations (may be empty)
    """
    app.logger.info("Request to list recommendations")

    # Build query with filters (and sorting if you want to keep it)
    query = Recommendation.query
    query = _apply_filters(query)
    query = _apply_sorting(query)  # <-- keep this if you want sort support

    # Execute query (no pagination; get everything)
    recommendations = query.all()

    app.logger.info("Found %d recommendations", len(recommendations))

    # Directly return serialized list
    results = [rec.serialize() for rec in recommendations]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# LIKE a Recommendation
######################################################################
@app.route("/recommendations/<int:recommendation_id>/like", methods=["PUT"])
def like_a_recommendation(recommendation_id):
    """Increase the likes of a recommendation"""
    app.logger.info("Request to like a recommendation with id: %d", recommendation_id)

    # Attempt to find the Recommendation and abort if not found
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    # you can only like recommendations that are active
    if not recommendation.status == RecommendationStatus.ACTIVE:
        abort(
            status.HTTP_409_CONFLICT,
            f"Recommendation with id '{recommendation_id}' is not active.",
        )

    recommendation.likes += 1
    recommendation.update()

    app.logger.info("Recommendation with ID: %d has been liked.", recommendation_id)
    return recommendation.serialize(), status.HTTP_200_OK


######################################################################
# DISLIKE a Recommendation
######################################################################
@app.route("/recommendations/<int:recommendation_id>/like", methods=["DELETE"])
def dislike_a_recommendation(recommendation_id):
    """decrease the likes of a recommendation"""
    app.logger.info("Request to like a recommendation with id: %d", recommendation_id)

    # Attempt to find the Recommendation and abort if not found
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    # you can only like recommendations that are active
    if not recommendation.status == RecommendationStatus.ACTIVE:
        abort(
            status.HTTP_409_CONFLICT,
            f"Recommendation with id '{recommendation_id}' is not active.",
        )
    if recommendation.likes > 0:
        recommendation.likes -= 1
        recommendation.update()

    app.logger.info("Recommendation with ID: %d has been disliked.", recommendation_id)
    return recommendation.serialize(), status.HTTP_200_OK


######################################################################
# SEND a Recommendation
######################################################################
@app.route("/recommendations/<int:recommendation_id>/send", methods=["POST"])
def send_a_recommendation(recommendation_id):
    """Send a recommendation to users"""

    app.logger.info("Request to send a recommendation with id: %d", recommendation_id)

    # Attempt to find the Recommendation and abort if not found
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    # Only return 200 when found (no other checks for now)

    recommendation.merchant_send_count += 1
    recommendation.last_sent_at = datetime.utcnow()
    recommendation.update()

    tracking_code = uuid.uuid4().hex
    app.logger.info(
        "Recommendation with ID: %d has been sent successfully.", recommendation_id
    )

    result = {
        "message": f"Recommendation {recommendation.id} sent successfully.",
        "recommendation": recommendation.serialize(),
        "sent": {
            "tracking_code": tracking_code,
            "sent_at": datetime.utcnow().isoformat() + "Z",
        },
    }

    return result, status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
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


######################################################################
# CANCEL (DEACTIVATE) A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/cancel", methods=["PUT"])
def cancel_recommendation(recommendation_id):
    """
    Cancel (deactivate) a Recommendation

    This endpoint sets a recommendation's status to INACTIVE (i.e., temporarily
    disables it) without deleting the record. It is idempotent: calling it on an
    already INACTIVE recommendation returns 200 with the current representation.
    """
    app.logger.info(
        "Request to cancel (deactivate) recommendation id [%s]", recommendation_id
    )

    # Find it or 404
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )
    if recommendation.status != RecommendationStatus.INACTIVE:
        recommendation.status = RecommendationStatus.INACTIVE
        recommendation.update()
        app.logger.info("Recommendation id [%d] set to INACTIVE.", recommendation_id)
    else:
        app.logger.info(
            "Recommendation id [%d] already INACTIVE (idempotent).", recommendation_id
        )

    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# REACTIVATE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/activate", methods=["PUT"])
def reactivate_recommendation(recommendation_id):
    """reactivate a recommendation"""

    app.logger.info("Request to reactivate recommendation id [%s]", recommendation_id)

    # Find it or 404
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )
    if recommendation.status != RecommendationStatus.ACTIVE:
        recommendation.status = RecommendationStatus.ACTIVE
        recommendation.update()
        app.logger.info("Recommendation id [%d] set to ACTIVE.", recommendation_id)
    else:
        app.logger.info(
            "Recommendation id [%d] already ACTIVE (idempotent).", recommendation_id
        )

    return jsonify(recommendation.serialize()), status.HTTP_200_OK
