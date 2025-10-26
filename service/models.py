"""
Models for Recommendation

All of the models are stored in this module
"""

import logging
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class RecommendationType(Enum):
    """Enumeration of possible recommendation types"""

    CROSS_SELL = "cross_sell"
    UP_SELL = "up_sell"
    ACCESSORY = "accessory"
    TRENDING = "trending"


class RecommendationStatus(Enum):
    """Enumeration of possible recommendation statuses"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class Recommendation(db.Model):
    """
    Class that represents a YourResourceModel
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)

    base_product_id = db.Column(db.Integer, nullable=False)
    recommended_product_id = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum(RecommendationStatus), default=RecommendationStatus.DRAFT
    )
    recommendation_type = db.Column(db.Enum(RecommendationType), nullable=False)
    likes = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return (
            f"<Recommendation {self.id}: "
            f" {self.base_product_id} -> {self.recommended_product_id}"
            f" ({self.recommendation_type.value})>"
        )

    def create(self):
        """
        Creates a recommendation to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a recommendation to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a recommendation from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "recommendation_type": self.recommendation_type.value,
            "base_product_id": self.base_product_id,
            "recommended_product_id": self.recommended_product_id,
            "status": self.status.value,
            "likes": self.likes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def deserialize(self, data: dict):
        """Deserializes a Recommendation from a dictionary"""
        try:
            self.name = data["name"]
            self.recommendation_type = RecommendationType(data["recommendation_type"])
            self.base_product_id = data["base_product_id"]
            self.recommended_product_id = data["recommended_product_id"]
            self.status = RecommendationStatus(data["status"])
            self.likes = data["likes"]
            self.created_at = data.get("created_at")
            self.updated_at = data.get("updated_at")

        except KeyError as error:
            raise DataValidationError(
                f"Missing required field: {error.args[0]}"
            ) from error
        except (ValueError, TypeError) as error:
            raise DataValidationError(f"Invalid data: {error}") from error

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the recommendation in the database"""
        logger.info("Processing all recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a YourResourceModel by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all YourResourceModels with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
