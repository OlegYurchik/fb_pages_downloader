from tortoise import fields

from .base import BaseAbstractModel
from .utils import non_negative_validator, phone_number_validator


class Page(BaseAbstractModel):
    id = fields.CharField(max_length=64, pk=True)
    name = fields.CharField(max_length=64)
    about = fields.TextField(null=True)
    affiliation = fields.TextField(null=True)
    app_id = fields.CharField(max_length=64, null=True)
    artists_we_like = fields.TextField(null=True)
    bio = fields.TextField(null=True)
    birthday = fields.CharField(max_length=28, null=True)
    booking_agent = fields.TextField(null=True)
    built = fields.TextField(null=True)
    can_check_in = fields.BooleanField(null=True)
    can_post = fields.BooleanField(null=True)
    category = fields.CharField(max_length=64, null=True)
    category_list = fields.JSONField(null=True)
    check_ins = fields.IntField(null=True, validators=[non_negative_validator])
    contact_address = fields.JSONField(null=True)
    current_location = fields.TextField(null=True)
    description = fields.TextField(null=True)
    directed_by = fields.CharField(max_length=64, null=True)
    emails = fields.JSONField(null=True)
    hours = fields.JSONField(null=True)
    link = fields.TextField(null=True)
    location = fields.JSONField(null=True)
    mission = fields.TextField(null=True)
    username = fields.CharField(max_length=64, null=True)
    were_here_count = fields.IntField(null=True, validators=[non_negative_validator])
    whatsapp_number = fields.CharField(
        max_length=19,
        null=True,
        validators=[phone_number_validator],
    )

    class Meta:
        table = "pages_page"
