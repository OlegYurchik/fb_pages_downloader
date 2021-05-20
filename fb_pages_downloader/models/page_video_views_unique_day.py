from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PageVideoViewsUniqueDay(PageInsightAbstractModel):
    METRIC = "page_video_views_unique"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_unique_page_video_views"
