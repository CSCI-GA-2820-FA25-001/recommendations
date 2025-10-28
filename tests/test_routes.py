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
Recommendation API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import (
    DataValidationError,
    db,
    Recommendation,
    RecommendationType,
    RecommendationStatus,
)
from .factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRecommendation(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create recommendations
    ############################################################
    def _create_recommendations(self, count: int = 1) -> list:
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test recommendation",
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------

    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        test_recommendation = RecommendationFactory()
        logging.debug("Test Recommendation: %s", test_recommendation.serialize())
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_recommendation = response.get_json()
        self.assertIn("id", new_recommendation)
        self.assertEqual(new_recommendation["name"], test_recommendation.name)
        self.assertEqual(
            new_recommendation["base_product_id"], test_recommendation.base_product_id
        )
        self.assertEqual(
            new_recommendation["recommendation_type"],
            test_recommendation.recommendation_type.value,
        )
        self.assertEqual(
            new_recommendation["recommended_product_id"],
            test_recommendation.recommended_product_id,
        )
        self.assertEqual(new_recommendation["status"], test_recommendation.status.value)
        self.assertEqual(new_recommendation["likes"], test_recommendation.likes)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_recommendation = response.get_json()
        self.assertIn("id", new_recommendation)
        self.assertEqual(new_recommendation["name"], test_recommendation.name)
        self.assertEqual(
            new_recommendation["base_product_id"], test_recommendation.base_product_id
        )
        self.assertEqual(
            new_recommendation["recommendation_type"],
            test_recommendation.recommendation_type.value,
        )
        self.assertIn("id", new_recommendation)
        self.assertEqual(new_recommendation["status"], test_recommendation.status.value)
        self.assertEqual(new_recommendation["likes"], test_recommendation.likes)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------

    def test_get_recommendation(self):
        """It should Get a single Recommendation"""
        # get the id of a recommendation
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_recommendation.name)

    def test_get_recommendation_not_found(self):
        """It should not Get a Recommendation thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("Not Found", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_recommendation(self):
        """It should Update an existing Recommendation"""
        # Create a recommendation to update
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Prepare the update payload
        new_recommendation = response.get_json()
        new_recommendation["name"] = "Updated Recommendation Name"
        new_recommendation["status"] = "inactive"

        # Send PUT request to update
        response = self.client.put(
            f"{BASE_URL}/{new_recommendation['id']}", json=new_recommendation
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_recommendation = response.get_json()
        self.assertEqual(updated_recommendation["id"], new_recommendation["id"])
        self.assertEqual(updated_recommendation["name"], "Updated Recommendation Name")
        self.assertEqual(updated_recommendation["status"], "inactive")

        get_response = self.client.get(f"{BASE_URL}/{new_recommendation['id']}")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        fetched = get_response.get_json()
        self.assertEqual(fetched["name"], "Updated Recommendation Name")

    # ==========================================================
    # TEST DELETE
    # ==========================================================
    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_recommendation(self):
        """It should raise DataValidationError when deleting a non-persisted Recommendation"""
        # Create a recommendation that is NOT saved to the database
        recommendation = RecommendationFactory()

        # Attempting to delete should raise DataValidationError,
        # because SQLAlchemy will complain that the instance is not persisted
        with self.assertRaises(DataValidationError):
            recommendation.delete()

    ######################################################################
    #  L I S T   R E C O M M E N D A T I O N S   T E S T S
    ######################################################################

    def test_list_all_recommendations(self):
        """It should list all recommendations"""
        # Create 5 recommendations
        for _ in range(5):
            recommendation = RecommendationFactory()
            recommendation.create()

        # Get all recommendations
        resp = self.client.get("/recommendations")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 5)

    def test_list_recommendations_empty(self):
        """It should return an empty list when no recommendations exist"""
        resp = self.client.get("/recommendations")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_list_recommendations_by_product_a_id(self):
        """It should list recommendations filtered by product_a_id"""
        # Create recommendations with specific base_product_id
        target_product_id = 101
        for _ in range(3):
            recommendation = RecommendationFactory(base_product_id=target_product_id)
            recommendation.create()

        # Create recommendations with different base_product_id
        for _ in range(2):
            recommendation = RecommendationFactory(base_product_id=999)
            recommendation.create()

        # Query by product_a_id
        resp = self.client.get(f"/recommendations?product_a_id={target_product_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 3)
        for rec in data:
            self.assertEqual(rec["base_product_id"], target_product_id)

    def test_list_recommendations_by_relationship_type(self):
        """It should list recommendations filtered by relationship_type"""
        # Create recommendations with ACCESSORY type
        for _ in range(3):
            recommendation = RecommendationFactory(
                recommendation_type=RecommendationType.ACCESSORY
            )
            recommendation.create()

        # Create recommendations with different types
        for _ in range(2):
            recommendation = RecommendationFactory(
                recommendation_type=RecommendationType.CROSS_SELL
            )
            recommendation.create()

        # Query by relationship_type
        resp = self.client.get("/recommendations?relationship_type=accessory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 3)
        for rec in data:
            self.assertEqual(rec["recommendation_type"], "accessory")

    def test_list_recommendations_by_status(self):
        """It should list recommendations filtered by status"""
        # Create recommendations with ACTIVE status
        for _ in range(4):
            recommendation = RecommendationFactory(status=RecommendationStatus.ACTIVE)
            recommendation.create()

        # Create recommendations with different status
        for _ in range(2):
            recommendation = RecommendationFactory(status=RecommendationStatus.INACTIVE)
            recommendation.create()

        # Query by status
        resp = self.client.get("/recommendations?status=active")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 4)
        for rec in data:
            self.assertEqual(rec["status"], "active")

    def test_list_recommendations_with_multiple_filters(self):
        """It should list recommendations with multiple filters"""
        target_product_id = 101
        target_type = RecommendationType.ACCESSORY
        target_status = RecommendationStatus.ACTIVE

        # Create matching recommendations
        for _ in range(2):
            recommendation = RecommendationFactory(
                base_product_id=target_product_id,
                recommendation_type=target_type,
                status=target_status,
            )
            recommendation.create()

        # Create non-matching recommendations
        for _ in range(3):
            recommendation = RecommendationFactory(
                base_product_id=999,
                recommendation_type=RecommendationType.CROSS_SELL,
                status=RecommendationStatus.INACTIVE,
            )
            recommendation.create()

        # Query with multiple filters
        resp = self.client.get(
            f"/recommendations?product_a_id={target_product_id}"
            f"&relationship_type=accessory&status=active"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)
        for rec in data:
            self.assertEqual(rec["base_product_id"], target_product_id)
            self.assertEqual(rec["recommendation_type"], "accessory")
            self.assertEqual(rec["status"], "active")

    def test_list_recommendations_invalid_relationship_type(self):
        """It should handle invalid relationship_type gracefully"""
        # Create some recommendations
        for _ in range(3):
            recommendation = RecommendationFactory()
            recommendation.create()

        # Use invalid type value
        resp = self.client.get("/recommendations?relationship_type=invalid_type")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        # Invalid enum value should be ignored, return all records
        self.assertEqual(len(data), 3)

    def test_list_recommendations_invalid_status(self):
        """It should handle invalid status gracefully"""
        # Create some recommendations
        for _ in range(3):
            recommendation = RecommendationFactory()
            recommendation.create()

        # Use invalid status value
        resp = self.client.get("/recommendations?status=invalid_status")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        # Invalid enum value should be ignored, return all records
        self.assertEqual(len(data), 3)

    def test_list_recommendations_no_matching_results(self):
        """It should return empty array when no recommendations match filters"""
        # Create recommendations with product_id=101
        for _ in range(3):
            recommendation = RecommendationFactory(base_product_id=101)
            recommendation.create()

        # Query for non-existent product_id
        resp = self.client.get("/recommendations?product_a_id=999")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    # ----------------------------------------------------------
    # TEST ACTIONS
    # ----------------------------------------------------------
    def test_like_a_recommendation(self):
        """It should like a recommendation and increase one like."""
        recommendations = self._create_recommendations(10)
        active_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.status == RecommendationStatus.ACTIVE
        ]
        recommendation = active_recommendations[0]
        response = self.client.put(f"{BASE_URL}/{recommendation.id}/like")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f"{BASE_URL}/{recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["likes"], recommendation.likes + 1)

    def test_like_inactive_recommendation(self):
        """It should not like a recommendation that is not active"""
        recommendations = self._create_recommendations(10)
        inactive_recommendations = [
            recommendation
            for recommendation in recommendations
            if not recommendation.status == RecommendationStatus.ACTIVE
        ]
        recommendation = inactive_recommendations[0]
        response = self.client.put(f"{BASE_URL}/{recommendation.id}/like")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_dislike_a_recommendation(self):
        """It should dislike a recommendation and reduce one like"""
        recommendations = self._create_recommendations(10)
        active_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.status == RecommendationStatus.ACTIVE
            and recommendation.likes > 0
        ]
        recommendation = active_recommendations[0]
        response = self.client.delete(f"{BASE_URL}/{recommendation.id}/like")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f"{BASE_URL}/{recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["likes"], recommendation.likes - 1)

    def test_dislike_not_active(self):
        """It should not like a recommendation that is not active or likes <= 0"""
        recommendations = self._create_recommendations(10)
        inactive_recommendations = [
            recommendation
            for recommendation in recommendations
            if not recommendation.status == RecommendationStatus.ACTIVE
            or recommendation.likes <= 0
        ]
        recommendation = inactive_recommendations[0]
        response = self.client.delete(f"{BASE_URL}/{recommendation.id}/like")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # ----------------------------------------------------------
    # TEST ACTIONS
    # ----------------------------------------------------------
    def test_cancel_a_recommendation(self):
        """It should cancel a recommendation"""
        # Create a recommendation that is available for purchase
        rec = RecommendationFactory()
        rec.status = "active"
        response = self.client.post(BASE_URL, json=rec.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.get_json()
        rec.id = data["id"]
        self.assertEqual(data["status"], RecommendationStatus.ACTIVE)

        # Call cancel on the created id and check the results
        response = self.client.put(f"{BASE_URL}/{rec.id}/cancel")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f"{BASE_URL}/{rec.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["status"], RecommendationStatus.INACTIVE)

    def test_cancel_recommendation_not_found(self):
        """It should not cancel a Recommendation thats not found"""
        response = self.client.put(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("Not Found", data["message"])


######################################################################
#  T E S T   S A D   P A T H S
######################################################################
class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_method_not_allowed(self):
        """It should not allow update without a recommendation id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_recommendation_no_data(self):
        """It should not Create a Recommendation with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_no_content_type(self):
        """It should not Create a Recommendation with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_wrong_content_type(self):
        """It should not Create a Recommendation with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_bad_recommendation_type(self):
        """It should not Create a Recommendation with bad recommendation type"""
        bad_data = {
            "name": "Invalid Rec Type",
            "recommendation_type": 123,  # intentionally invalid type (not string)
            "base_product_id": 1,
            "recommended_product_id": 2,
            "status": "active",
        }

        response = self.client.post(BASE_URL, json=bad_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.get_json()
        self.assertIn("Invalid data", body["message"])

    def test_create_recommendation_bad_status(self):
        """It should not Create a Recommendation with bad status data"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        # change status to a bad string
        test_recommendation = recommendation.serialize()
        test_recommendation["status"] = "long"
        response = self.client.post(BASE_URL, json=test_recommendation)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_recommendation_not_found(self):
        """It should not Update a Recommendation that does not exist"""
        # Create a dummy update payload
        update_data = {
            "name": "Nonexistent Recommendation",
            "recommendation_type": "cross_sell",
            "base_product_id": 1,
            "recommended_product_id": 2,
            "status": "active",
        }

        # Try updating a recommendation that doesn't exist (ID = 999)
        response = self.client.put(f"{BASE_URL}/999", json=update_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        body = response.get_json()
        self.assertIn("not found", body["message"].lower())
