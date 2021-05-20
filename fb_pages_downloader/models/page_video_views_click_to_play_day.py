from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PageVideoViewsClickToPlayDay(PageInsightAbstractModel):
    METRIC = "page_video_views_click_to_play"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_page_video_views_click_to_play"
