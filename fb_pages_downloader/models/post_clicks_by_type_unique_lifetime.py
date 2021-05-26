from typing import Dict

from tortoise import fields

from .base import PagePostInsightAbstractModel
from .utils import PeriodEnum


class PostClicksByTypeUniqueLifetime(PagePostInsightAbstractModel):
    METRIC = "post_clicks_by_type_unique"
    PERIOD = PeriodEnum.life_time

    video_plays = fields.IntField(null=True)
    link_clicks = fields.IntField(null=True)
    other_clicks = fields.IntField(null=True)

    @staticmethod
    def parse_value(value: Dict[str, int]) -> Dict[str, int]:
        return {
            "video_plays": value.get("video play"),
            "link_clicks": value.get("link clicks"),
            "other_clicks": value.get("other clicks"),
        }

    class Meta:
        table = "pages_life_time_unique_post_clicks_by_type"
