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
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Recommendation, RecommendationType, RecommendationStatus
from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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
            recommendation = RecommendationFactory(
                status=RecommendationStatus.ACTIVE
            )
            recommendation.create()

        # Create recommendations with different status
        for _ in range(2):
            recommendation = RecommendationFactory(
                status=RecommendationStatus.INACTIVE
            )
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

    def test_list_recommendations_invalid_product_id(self):
        """It should handle invalid product_id gracefully"""
        # Create some recommendations
        for _ in range(3):
            recommendation = RecommendationFactory()
            recommendation.create()

        # Query with invalid product_id (should be ignored or return empty)
        resp = self.client.get("/recommendations?product_a_id=invalid")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        # Invalid type parameters should be ignored, returning all or none
        self.assertIsInstance(data, list)

    def test_list_recommendations_invalid_relationship_type(self):
        """It should handle invalid relationship_type gracefully"""
        # Create some recommendations
        for _ in range(3):
            recommendation = RecommendationFactory()
            recommendation.create()

        # Query with invalid relationship_type
        resp = self.client.get("/recommendations?relationship_type=invalid_type")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        # Invalid enum values should return all items (no filter applied)
        self.assertEqual(len(data), 3)

    def test_list_recommendations_invalid_status(self):
        """It should handle invalid status gracefully"""
        # Create some recommendations
        for _ in range(3):
            recommendation = RecommendationFactory()
            recommendation.create()

        # Query with invalid status
        resp = self.client.get("/recommendations?status=invalid_status")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        # Invalid enum values should return all items (no filter applied)
        self.assertEqual(len(data), 3)

    def test_list_recommendations_no_matching_results(self):
        """It should return empty array when no recommendations match filters"""
        # Create recommendations with specific values
        for _ in range(3):
            recommendation = RecommendationFactory(base_product_id=101)
            recommendation.create()

        # Query for non-existent product_id
        resp = self.client.get("/recommendations?product_a_id=999")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    # Todo: Add your other test cases here...
