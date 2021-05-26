from typing import Any, Dict

from tortoise import fields, models

from .utils import PeriodEnum


class BaseAbstractModel(models.Model):
    """
    Base abstract model for all models in Facebook Pages Downloader
    """
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

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


class InsightMixinModel:
    """
    Mixin model for models which describes facebook page insights
    """

    @property
    def PERIOD(self) -> PeriodEnum:
        raise NotImplementedError

    @property
    def METRIC(self) -> str:
        raise NotImplementedError

    @staticmethod
    def parse_value(value: Any) -> Dict[str, Any]:
        raise NotImplementedError

    m_period = fields.CharEnumField(PeriodEnum, null=False, index=True)


class PageInsightAbstractModel(InsightMixinModel, PageAttributesAbstractModel):
    m_date = fields.CharField(max_length=64, null=True, index=True)
    value = fields.FloatField(null=False)

    @staticmethod
    def parse_value(value: int) -> Dict[str, int]:
        return {"value": value}


class PagePostInsightAbstractModel(InsightMixinModel, PagePostAttributesAbstractModel):
    pass
