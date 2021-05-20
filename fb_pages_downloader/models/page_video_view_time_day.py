from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PageVideoViewTimeDay(PageInsightAbstractModel):
    METRIC = "page_video_view_time"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_page_video_view_time"
