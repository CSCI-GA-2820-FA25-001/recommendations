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
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse
from service.models import Recommendation, RecommendationType, RecommendationStatus
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Recommendation Demo REST API Service",
    description="This is a sample server Recommendation server.",
    default="recommendations",
    default_label="Recommendation service operations",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# Define models for Swagger documentation
######################################################################
create_model = api.model(
    "Recommendation",
    {
        "name": fields.String(
            required=True, description="The name of the Recommendation"
        ),
        "base_product_id": fields.Integer(
            required=True, description="The base product ID"
        ),
        "recommended_product_id": fields.Integer(
            required=True, description="The recommended product ID"
        ),
        "recommendation_type": fields.String(
            enum=[t.value for t in RecommendationType],  # ← PATCH 1 APPLIED
            required=True,
            description="The type of recommendation relationship",
        ),
        "status": fields.String(
            enum=[s.value for s in RecommendationStatus],  # ← PATCH 1 APPLIED
            description="The status of the recommendation (default: ACTIVE)",
        ),
        "likes": fields.Integer(description="Number of likes (default: 0)"),
        "merchant_send_count": fields.Integer(
            description="Number of times sent by merchant (default: 0)"
        ),
    },
)

recommendation_model = api.inherit(
    "RecommendationModel",
    create_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "created_at": fields.DateTime(
            readOnly=True, description="Timestamp when recommendation was created"
        ),
        "last_sent_at": fields.DateTime(
            readOnly=True, description="Timestamp when recommendation was last sent"
        ),
    },
)

# Query string arguments for listing recommendations
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument(
    "base_product_id",
    type=int,
    location="args",
    required=False,
    help="Filter by base product ID",
)
recommendation_args.add_argument(
    "product_a_id",
    type=int,
    location="args",
    required=False,
    help="Filter by base product ID (alias)",
)
recommendation_args.add_argument(
    "relationship_type",
    type=str,
    location="args",
    required=False,
    help="Filter by recommendation type",
)
recommendation_args.add_argument(
    "status", type=str, location="args", required=False, help="Filter by status"
)
recommendation_args.add_argument(
    "sort",
    type=str,
    location="args",
    required=False,
    help="Sort by field (created_at_asc, created_at_desc, name_asc, name_desc, id_asc, id_desc)",
)


######################################################################
#  PATH: /recommendations/{id}
######################################################################
@api.route("/recommendations/<int:recommendation_id>")
@api.param("recommendation_id", "The Recommendation identifier")
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single Recommendation
    GET /recommendations/{id} - Returns a Recommendation with the id
    PUT /recommendations/{id} - Update a Recommendation with the id
    DELETE /recommendations/{id} - Deletes a Recommendation with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("get_recommendations")
    @api.response(404, "Recommendation not found")
    @api.marshal_with(recommendation_model)
    def get(self, recommendation_id):
        """
        Retrieve a single Recommendation

        This endpoint will return a Recommendation based on its id
        """
        app.logger.info("Request for Recommendation with id: %s", recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation Not Found")
        app.logger.info("Returning recommendation: %s", recommendation.name)
        return recommendation.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("update_recommendations")
    @api.response(404, "Recommendation not found")
    @api.response(400, "The posted Recommendation data was not valid")
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Update a Recommendation

        This endpoint will update a Recommendation based on the body that is posted
        """
        app.logger.info(
            "Request to Update a recommendation with id [%s]", recommendation_id
        )
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation Not Found")
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        recommendation.deserialize(data)
        recommendation.id = recommendation_id
        recommendation.update()
        app.logger.info("Recommendation with ID: %d updated.", recommendation.id)
        return recommendation.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("delete_recommendations")
    @api.response(204, "Recommendation deleted")
    def delete(self, recommendation_id):
        """
        Delete a Recommendation

        This endpoint will delete a Recommendation based on the id specified in the path
        """
        app.logger.info(
            "Request to Delete a recommendation with id [%s]", recommendation_id
        )
        recommendation = Recommendation.find(recommendation_id)
        if recommendation:
            recommendation.delete()
            app.logger.info(
                "Recommendation with ID: %d delete complete.", recommendation_id
            )
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /recommendations
######################################################################
@api.route("/recommendations", strict_slashes=False)
class RecommendationCollection(Resource):
    """Handles all interactions with collections of Recommendations"""

    # ------------------------------------------------------------------
    # LIST ALL RECOMMENDATIONS
    # ------------------------------------------------------------------
    @api.doc("list_recommendations")
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """Returns all of the Recommendations"""
        app.logger.info("Request to list Recommendations...")

        args = recommendation_args.parse_args()
        query = Recommendation.query

        # Apply filters
        # Support both product_a_id and base_product_id
        product_a_id = args.get("product_a_id")
        base_product_id = args.get("base_product_id")
        filter_id = product_a_id if product_a_id is not None else base_product_id

        if filter_id is not None:
            app.logger.info("Filtering by base_product_id: %s", filter_id)
            query = query.filter(Recommendation.base_product_id == filter_id)

        # Filter by relationship_type
        relationship_type = args.get("relationship_type")
        if relationship_type:
            try:
                type_enum = RecommendationType(relationship_type)
                app.logger.info("Filtering by relationship_type: %s", relationship_type)
                query = query.filter(Recommendation.recommendation_type == type_enum)
            except ValueError:
                app.logger.warning(
                    "Invalid relationship_type value: %s. Ignoring filter.",
                    relationship_type,
                )

        # Filter by status
        status_param = args.get("status")
        if status_param:
            try:
                status_enum = RecommendationStatus(status_param)
                app.logger.info("Filtering by status: %s", status_param)
                query = query.filter(Recommendation.status == status_enum)
            except ValueError:
                app.logger.warning(
                    "Invalid status value: %s. Ignoring filter.", status_param
                )

        # Apply sorting
        sort_param = args.get("sort")
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
            query = query.order_by(valid_sort_fields[sort_param])
        else:
            query = query.order_by(Recommendation.id.asc())

        # Execute query
        recommendations = query.all()
        app.logger.info("[%s] Recommendations returned", len(recommendations))

        results = [rec.serialize() for rec in recommendations]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("create_recommendations")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Recommendation

        This endpoint will create a Recommendation based on the data in the body that is posted
        """
        app.logger.info("Request to Create a Recommendation...")
        recommendation = Recommendation()
        app.logger.debug("Payload = %s", api.payload)
        recommendation.deserialize(api.payload)
        recommendation.create()
        app.logger.info("Recommendation with new id [%s] created!", recommendation.id)
        location_url = api.url_for(
            RecommendationResource, recommendation_id=recommendation.id, _external=True
        )
        return (
            recommendation.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  PATH: /recommendations/{id}/like
######################################################################
@api.route("/recommendations/<int:recommendation_id>/like")
@api.param("recommendation_id", "The Recommendation identifier")
class LikeResource(Resource):
    """Like/Dislike actions on a Recommendation"""

    @api.doc("like_recommendations")
    @api.response(404, "Recommendation not found")
    @api.response(409, "The Recommendation is not active")
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Like a Recommendation

        This endpoint will increase the likes of a recommendation
        """
        app.logger.info(
            "Request to like a recommendation with id: %d", recommendation_id
        )
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation Not Found")
        if recommendation.status != RecommendationStatus.ACTIVE:
            abort(
                status.HTTP_409_CONFLICT,
                f"Recommendation with id '{recommendation_id}' is not active.",
            )
        recommendation.likes += 1
        recommendation.update()
        app.logger.info("Recommendation with ID: %d has been liked.", recommendation_id)
        return recommendation.serialize(), status.HTTP_200_OK

    @api.doc("dislike_recommendations")
    @api.response(404, "Recommendation not found")
    @api.response(409, "The Recommendation is not active")
    @api.marshal_with(recommendation_model)
    def delete(self, recommendation_id):
        """
        Dislike a Recommendation

        This endpoint will decrease the likes of a recommendation
        """
        app.logger.info(
            "Request to dislike a recommendation with id: %d", recommendation_id
        )
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation Not Found")
        if recommendation.status != RecommendationStatus.ACTIVE:
            abort(
                status.HTTP_409_CONFLICT,
                f"Recommendation with id '{recommendation_id}' is not active.",
            )
        if recommendation.likes > 0:
            recommendation.likes -= 1
            recommendation.update()
        app.logger.info(
            "Recommendation with ID: %d has been disliked.", recommendation_id
        )
        return recommendation.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /recommendations/{id}/send
######################################################################
@api.route("/recommendations/<int:recommendation_id>/send")
@api.param("recommendation_id", "The Recommendation identifier")
class SendResource(Resource):
    """Send action on a Recommendation"""

    @api.doc("send_recommendations")
    @api.response(404, "Recommendation not found")
    def post(self, recommendation_id):
        """
        Send a Recommendation

        This endpoint will send a recommendation to users
        """
        app.logger.info(
            "Request to send a recommendation with id: %d", recommendation_id
        )
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation Not Found")
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
#  PATH: /recommendations/{id}/cancel
######################################################################
@api.route("/recommendations/<int:recommendation_id>/cancel")
@api.param("recommendation_id", "The Recommendation identifier")
class CancelResource(Resource):
    """Cancel (deactivate) action on a Recommendation"""

    @api.doc("cancel_recommendations")
    @api.response(404, "Recommendation not found")
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Cancel (deactivate) a Recommendation

        This endpoint sets a recommendation's status to INACTIVE
        """
        app.logger.info(
            "Request to cancel (deactivate) recommendation id [%s]", recommendation_id
        )
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation Not Found")
        if recommendation.status != RecommendationStatus.INACTIVE:
            recommendation.status = RecommendationStatus.INACTIVE
            recommendation.update()
            app.logger.info(
                "Recommendation id [%d] set to INACTIVE.", recommendation_id
            )
        else:
            app.logger.info(
                "Recommendation id [%d] already INACTIVE (idempotent).",
                recommendation_id,
            )
        return recommendation.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /recommendations/{id}/activate
######################################################################
@api.route("/recommendations/<int:recommendation_id>/activate")
@api.param("recommendation_id", "The Recommendation identifier")
class ActivateResource(Resource):
    """Activate (reactivate) action on a Recommendation"""

    @api.doc("activate_recommendations")
    @api.response(404, "Recommendation not found")
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Reactivate a Recommendation

        This endpoint sets a recommendation's status to ACTIVE
        """
        app.logger.info(
            "Request to reactivate recommendation id [%s]", recommendation_id
        )
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation Not Found")
        if recommendation.status != RecommendationStatus.ACTIVE:
            recommendation.status = RecommendationStatus.ACTIVE
            recommendation.update()
            app.logger.info("Recommendation id [%d] set to ACTIVE.", recommendation_id)
        else:
            app.logger.info(
                "Recommendation id [%d] already ACTIVE (idempotent).", recommendation_id
            )
        return recommendation.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
