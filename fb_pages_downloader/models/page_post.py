from tortoise import fields

from .base import PageAttributesAbstractModel
from .utils import non_negative_validator


class PagePost(PageAttributesAbstractModel):
    id = fields.CharField(max_length=64, pk=True)
    post_id = fields.CharField(max_length=64, null=False, index=True)
    created_time = fields.DatetimeField(null=False)
    eligible_for_promotion = fields.BooleanField(null=True)
    expired = fields.BooleanField(null=True)
    full_picture = fields.CharField(max_length=64, null=True)
    hidden = fields.BooleanField(null=True)
    message = fields.TextField(null=True)
    popular = fields.BooleanField(null=True)
    published = fields.BooleanField(null=True)
    privacy = fields.JSONField(null=True)
    promotable_id = fields.CharField(max_length=64, null=True)
    shares_count = fields.IntField(null=True, validators=[non_negative_validator])
    status_type = fields.CharField(max_length=64, null=True)
    story = fields.TextField(null=True)
    updated_time = fields.DatetimeField(null=True)

    class Meta:
        table = "pages_post"
