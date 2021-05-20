from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PageVideoViewsOrganicDay(PageInsightAbstractModel):
    METRIC = "page_video_views_organic"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_page_video_views_organic"
