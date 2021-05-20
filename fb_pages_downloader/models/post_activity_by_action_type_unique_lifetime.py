from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PostActivityByActionTypeUniqueLifetime(PageInsightAbstractModel):
    METRIC = "post_activity_by_action_type_unique"
    PERIOD = PeriodEnum.life_time

    class Meta:
        table = "pages_life_time_unique_post_activity_by_action_type"
