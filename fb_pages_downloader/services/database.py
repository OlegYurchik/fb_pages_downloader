import re
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Type

from facet import ServiceMixin
from loguru import logger
from tortoise import Tortoise, models

from .. import models
from ..models import (
    Page,
    PagePost,
    PagePostAttachment,
)
from ..models.base import BaseAbstractModel


@lru_cache()
def generate_get_function(model: Type[BaseAbstractModel]) -> Callable:
    async def get(**kwargs) -> Optional[model]:
        return await model.get_or_none(**kwargs)

    return get


@lru_cache()
def generate_update_function(model: Type[BaseAbstractModel]) -> Callable:
    async def update(record: model, fields: Dict[str, Any]):
        await record.save(update_fields=fields)

    return update


@lru_cache()
def generate_create_function(model: Type[BaseAbstractModel]) -> Callable:
    async def create(fields: Dict[str, Any]) -> model:
        return await model.create(**fields)

    return create


def camel_to_snake(string: str) -> str:
    return re.sub(r"\B([A-Z]+)", r"_\1", string).lower()


class DatabaseServiceMeta(type):
    MODELS = (
        Page,
        PagePost,
        PagePostAttachment,
    )

    def __new__(mcs, class_name, parents, attributes) -> type:
        for model in mcs.MODELS:
            model_name = camel_to_snake(model.__name__)
            attributes[f"get_{model_name}"] = staticmethod(generate_get_function(model))
            attributes[f"update_{model_name}"] = staticmethod(generate_update_function(model))
            attributes[f"create_{model_name}"] = staticmethod(generate_create_function(model))
            attributes["generate_get_function"] = staticmethod(generate_get_function)
            attributes["generate_update_function"] = staticmethod(generate_update_function)
            attributes["generate_create_function"] = staticmethod(generate_create_function)

        return super().__new__(mcs, class_name, parents, attributes)


class DatabaseService(ServiceMixin, metaclass=DatabaseServiceMeta):
    def __init__(self, db_url: str):
        self._db_url = db_url

    async def start(self):
        await Tortoise.init(
            db_url=self._db_url,
            modules={"models": [models]},
        )
        logger.info("Connected to database")
        await Tortoise.generate_schemas()
        logger.info("Generate schemas in database")
        logger.info("Database service started.")

    @staticmethod
    async def stop():
        await Tortoise.close_connections()
        logger.info("Close connections with database")
        logger.info("Database service stopped.")
