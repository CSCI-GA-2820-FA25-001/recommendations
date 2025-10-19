"""
Test Factory to make fake objects for testing
"""

from datetime import datetime
import factory
from service.models import Recommendation, RecommendationType, RecommendationStatus


class RecommendationFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Recommendation

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    recommendation_type = factory.Iterator(list(RecommendationType))
    base_product_id = factory.Sequence(lambda n: n + 100)
    recommended_product_id = factory.Sequence(lambda n: n + 200)
    status = factory.Iterator(list(RecommendationStatus))
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
