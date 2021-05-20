from tortoise import fields

from .base import PagePostAttributesAbstractModel


class PagePostAttachment(PagePostAttributesAbstractModel):
    type = fields.CharField(max_length=64, null=False)
    title = fields.CharField(max_length=256, null=True)
    url = fields.TextField(null=True)
    description = fields.TextField(null=True)
    target = fields.JSONField(null=True)

    class Meta:
        table = "pages_post_attachment"
