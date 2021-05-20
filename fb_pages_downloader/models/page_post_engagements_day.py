from .base import PageInsightAbstractModel
from .utils import PeriodEnum


class PagePostEngagementsDay(PageInsightAbstractModel):
    METRIC = "page_post_engagements"
    PERIOD = PeriodEnum.day

    class Meta:
        table = "pages_daily_page_post_engagements"
