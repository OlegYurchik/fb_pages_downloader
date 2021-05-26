from typing import Dict

from tortoise import fields

from .base import PagePostInsightAbstractModel
from .utils import PeriodEnum


class PostReactionsByTypeTotalUniqueLifetime(PagePostInsightAbstractModel):
    METRIC = "post_reactions_by_type_total"
    PERIOD = PeriodEnum.life_time

    likes = fields.IntField(null=True)
    angers = fields.IntField(null=True)
    loves = fields.IntField(null=True)

    @staticmethod
    def parse_value(value: Dict[str, int]) -> Dict[str, int]:
        return {
            "likes": value.get("like"),
            "angers": value.get("anger"),
            "loves": value.get("love"),
        }

    class Meta:
        table = "pages_life_time_post_reactions_by_type_total"
