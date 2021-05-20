from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PageVideoViewsDay(PageInsightAbstractModel):
    METRIC = "page_video_views"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_page_video_views"
