from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PostReactionsByTypeTotalUniqueLifetime(PageInsightAbstractModel):
    METRIC = "post_reactions_by_type_total"
    PERIOD = PeriodEnum.life_time

    class Meta:
        table = "pages_life_time_post_reactions_by_type_total"
