"""
Models for YourResourceModel

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
    DELETED = "deleted"


class Recommendation(db.Model):
    """
    Class that represents a YourResourceModel
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    base_product_id = db.Column(db.Integer, nullable=False)
    recommended_product_id = db.Column(db.Integer, nullable=False)
    weighted_score = db.Column(db.Numeric, default=1.0)
    rationale = db.Column(db.Text)
    status = db.Column(
        db.Enum(RecommendationStatus), default=RecommendationStatus.DRAFT
    )
    recommendation_type = db.Column(db.Enum(RecommendationType), nullable=False)
    recommendation_id = db.Column(db.Integer, nullable=False)
    valid_from = db.Column(db.DateTime, default=datetime.now)
    valid_to = db.Column(db.DateTime)

    # TODO: add created_on and updated_on fields; also add triggers to update them

    name = db.Column(db.String(63))

    def __repr__(self):
        return (
            f"<Recommendation {self.id}: "
            f" {self.base_product_id} -> {self.recommended_product_id}"
            f" ({self.recommendation_type.value})>"
        )

    def create(self):
        """
        Creates a YourResourceModel to the database
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
        Updates a YourResourceModel to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a YourResourceModel from the data store"""
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
            "base_product_id": self.base_product_id,
            "recommended_product_id": self.recommended_product_id,
            "recommendation_type": self.recommendation_type.value if self.recommendation_type else None,
            "weighted_score": float(self.weighted_score) if self.weighted_score else None,
            "rationale": self.rationale,
            "status": self.status.value if self.status else None,
            "recommendation_id": self.recommendation_id,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
        }

    def deserialize(self, data):
        """
        Deserializes a YourResourceModel from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the YourResourceModels in the database"""
        logger.info("Processing all YourResourceModels")
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
