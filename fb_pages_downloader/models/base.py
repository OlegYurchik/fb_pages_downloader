from tortoise import fields, models

from .utils import PeriodEnum


class BaseAbstractModel(models.Model):
    """
    Base abstract model for all models in Facebook Pages Downloader
    """
    ingested_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True


class PageAttributesAbstractModel(BaseAbstractModel):
    """
    Base abstract model for models which describes any facebook page
    """
    page_id = fields.CharField(max_length=64, null=False, index=True)

    class Meta:
        abstract = True


class PagePostAttributesAbstractModel(PageAttributesAbstractModel):
    """
    Base abstract model for models which describes posts of facebook pages
    """
    post_id = fields.CharField(max_length=64, null=False, index=True)

    class Meta:
        abstract = True


class PageInsightAbstractModel(PageAttributesAbstractModel):
    """
    Base abstract model for models which describes facebook page insights
    """
    @property
    def PERIOD(self):
        raise NotImplementedError

    @property
    def METRIC(self):
        raise NotImplementedError

    m_period = fields.CharEnumField(PeriodEnum, null=False, index=True)
    m_date = fields.CharField(max_length=64, null=False, index=True)
    value = fields.FloatField(null=False)

    class Meta:
        abstract = True
