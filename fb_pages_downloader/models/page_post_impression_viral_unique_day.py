from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PagePostImpressionViralUniqueDay(PageInsightAbstractModel):
    METRIC = "page_posts_impressions_viral_unique"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_unique_page_posts_impressions_viral"
