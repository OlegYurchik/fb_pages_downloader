from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PageVideoViewsAutoplayedDay(PageInsightAbstractModel):
    METRIC = "page_video_views_autoplayed"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_page_video_views_autoplayed"
