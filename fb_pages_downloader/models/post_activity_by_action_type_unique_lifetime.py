from typing import Dict

from tortoise import fields

from .base import PagePostInsightAbstractModel
from .utils import PeriodEnum


class PostActivityByActionTypeUniqueLifetime(PagePostInsightAbstractModel):
    METRIC = "post_activity_by_action_type_unique"
    PERIOD = PeriodEnum.life_time

    shares = fields.IntField(null=True)
    likes = fields.IntField(null=True)
    comments = fields.IntField(null=True)

    @staticmethod
    def parse_value(value: Dict[str, int]) -> Dict[str, int]:
        return {
            "shares": value.get("share"),
            "likes": value.get("like"),
            "comments": value.get("comment"),
        }

    class Meta:
        table = "pages_life_time_unique_post_activity_by_action_type"
