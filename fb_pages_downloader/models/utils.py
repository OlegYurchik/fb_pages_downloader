import enum

from tortoise.exceptions import ValidationError


class PeriodEnum(enum.Enum):
    day = "day"
    life_time = "lifetime"


def non_negative_validator(value: int):
    if value < 0:
        raise ValidationError(f"Value is negative: {value}")


def phone_number_validator(value: str):
    pass
