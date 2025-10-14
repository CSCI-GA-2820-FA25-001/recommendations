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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from sqlalchemy.exc import SQLAlchemyError
from wsgi import app
from service.models import Recommendation, DataValidationError, db
from .factories import RecommendationFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  RECOMMENDATION   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceModel(TestCase):
    """Test Cases for Recommendation Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_recommendation(self):
        """It should create a Recommendation"""
        # Todo: Remove this test case example
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        found = Recommendation.all()
        self.assertEqual(len(found), 1)
        data = Recommendation.find(recommendation.id)
        self.assertEqual(data.name, recommendation.name)
        self.assertEqual(data.recommendation_type, recommendation.recommendation_type)
        self.assertEqual(data.base_product_id, recommendation.base_product_id)
        self.assertEqual(
            data.recommended_product_id, recommendation.recommended_product_id
        )
        self.assertEqual(data.status, recommendation.status)
        self.assertEqual(data.created_at, recommendation.created_at)
        self.assertEqual(data.updated_at, recommendation.updated_at)

    def test_serialize_recommendation(self):
        """It should serialize a Recommendation into a dictionary"""
        rec = RecommendationFactory()
        rec.create()
        data = rec.serialize()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["id"], rec.id)
        self.assertEqual(data["name"], rec.name)
        self.assertEqual(data["recommendation_type"], rec.recommendation_type.name)
        self.assertEqual(data["base_product_id"], rec.base_product_id)
        self.assertEqual(data["recommended_product_id"], rec.recommended_product_id)
        self.assertEqual(data["status"], rec.status.name)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_deserialize_valid_data(self):
        """It should deserialize a dictionary into a Recommendation object"""
        rec = Recommendation()
        data = {
            "name": "Cross-sell Combo",
            "recommendation_type": "cross_sell",
            "base_product_id": 1,
            "recommended_product_id": 2,
            "status": "active",
        }
        rec.deserialize(data)
        self.assertEqual(rec.name, data["name"])
        self.assertEqual(rec.recommendation_type.value, data["recommendation_type"])
        self.assertEqual(rec.base_product_id, data["base_product_id"])
        self.assertEqual(rec.recommended_product_id, data["recommended_product_id"])
        self.assertEqual(rec.status.value, data["status"])

    def test_deserialize_missing_field_raises(self):
        """It should raise DataValidationError when a required field is missing"""
        rec = Recommendation()
        data = {
            # intentionally missing 'name'
            "recommendation_type": "cross_sell",
            "base_product_id": 1,
            "recommended_product_id": 2,
            "status": "active",
        }
        with self.assertRaises(DataValidationError):
            rec.deserialize(data)

    def test_deserialize_invalid_enum_raises(self):
        """It should raise DataValidationError when enum value is invalid"""
        rec = Recommendation()
        bad = {
            "name": "Invalid Enum",
            "recommendation_type": "not_a_valid_type",
            "base_product_id": 1,
            "recommended_product_id": 2,
            "status": "active",
        }
        with self.assertRaises(DataValidationError):
            rec.deserialize(bad)

    def test_repr_contains_key_info(self):
        """It should return a string representation of the Recommendation"""
        rec = RecommendationFactory()
        rec.create()
        text = repr(rec)
        self.assertIn(str(rec.base_product_id), text)
        self.assertIn(str(rec.recommended_product_id), text)
        self.assertIn(rec.recommendation_type.value, text)
        self.assertTrue(text.startswith("<Recommendation"))

    def test_all_returns_list(self):
        """It should return all recommendations"""
        rec1 = RecommendationFactory()
        rec2 = RecommendationFactory()
        rec1.create()
        rec2.create()
        all_recs = Recommendation.all()
        self.assertIsInstance(all_recs, list)
        self.assertEqual(len(all_recs), 2)

    def test_create_rollback_on_failure(self):
        """It should rollback if create() raises an exception"""
        rec = RecommendationFactory()
        # Monkeypatch db.session.add to raise an exception
        original_add = db.session.add

        def fail_add(_):
            raise SQLAlchemyError("Simulated DB add failure")

        db.session.add = fail_add

        with self.assertRaises(DataValidationError):
            rec.create()

        db.session.add = original_add

    def test_update_rollback_on_failure(self):
        """It should rollback if update() raises an exception"""
        rec = RecommendationFactory()
        rec.create()
        # Monkeypatch db.session.commit to raise an exception
        original_commit = db.session.commit

        def fail_commit():
            raise SQLAlchemyError("Simulated DB commit failure")

        db.session.commit = fail_commit

        rec.name = "New Name"  # make sure the session has something to commit
        with self.assertRaises(DataValidationError):
            rec.update()

        db.session.commit = original_commit

    def test_delete_rollback_on_failure(self):
        """It should rollback if delete() raises an exception"""
        rec = RecommendationFactory()
        rec.create()
        # Monkeypatch db.session.delete to raise an exception
        original_delete = db.session.delete

        def fail_delete(_):
            raise SQLAlchemyError("Simulated DB delete failure")

        db.session.delete = fail_delete

        with self.assertRaises(DataValidationError):
            rec.delete()

        db.session.delete = original_delete

    def test_delete_successful_removes_record(self):
        """It should delete a persisted Recommendation successfully"""
        rec = RecommendationFactory()
        rec.create()  # add to DB
        rec_id = rec.id

        # ensure record exists before deletion
        self.assertIsNotNone(Recommendation.find(rec_id))

        rec.delete()

        self.assertIsNone(Recommendation.find(rec_id))

    def test_find_by_name(self):
        """It should find recommendations by name"""
        rec1 = RecommendationFactory(name="Alpha")
        rec2 = RecommendationFactory(name="Beta")
        rec1.create()
        rec2.create()

        results_query = Recommendation.find_by_name("Alpha")
        results = (
            results_query.all()
            if hasattr(results_query, "all")
            else list(results_query)
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alpha")
