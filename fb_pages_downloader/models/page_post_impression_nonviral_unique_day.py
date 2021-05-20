from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PagePostImpressionNonviralUniqueDay(PageInsightAbstractModel):
    METRIC = "page_posts_impressions_nonviral_unique"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_unique_page_posts_impressions_nonviral"
