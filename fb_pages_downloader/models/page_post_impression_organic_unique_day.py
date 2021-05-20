from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PagePostImpressionOrganicUniqueDay(PageInsightAbstractModel):
    METRIC = "page_posts_impressions_organic_unique"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_unique_page_posts_impressions_organic"
