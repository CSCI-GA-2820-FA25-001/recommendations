"""
Test Factory to make fake objects for testing
"""

from datetime import datetime, timedelta
import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyDecimal
from service.models import Recommendation, RecommendationType, RecommendationStatus


class RecommendationFactory(factory.Factory):
    """Creates fake Recommendation objects for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""
        model = Recommendation

    id = factory.Sequence(lambda n: n)
    base_product_id = FuzzyInteger(1, 1000)
    recommended_product_id = FuzzyInteger(1, 1000)
    recommendation_type = FuzzyChoice(choices=[t for t in RecommendationType])
    weighted_score = FuzzyDecimal(0.0, 10.0, precision=2)
    rationale = factory.Faker("sentence", nb_words=10)
    status = FuzzyChoice(choices=[s for s in RecommendationStatus])
    recommendation_id = factory.Sequence(lambda n: n + 1000)
    valid_from = factory.LazyFunction(datetime.now)
    valid_to = factory.LazyFunction(lambda: datetime.now() + timedelta(days=30))
