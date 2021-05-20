from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PageVideoViewsPaidDay(PageInsightAbstractModel):
    METRIC = "page_video_views_paid"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_page_video_views_paid"
