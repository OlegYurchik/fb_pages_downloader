from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PostClicksByTypeUniqueLifetime(PageInsightAbstractModel):
    METRIC = "post_clicks_by_type_unique"
    PERIOD = PeriodEnum.life_time

    class Meta:
        table = "pages_life_time_unique_post_clicks_by_type"
