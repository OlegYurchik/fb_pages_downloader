import enum
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, validator


class RetryDelayFunctionEnum(str, enum.Enum):
    """
    Enum for fb_retry_delay_function value in Settings
    """
    EXPO = "expo"
    CONST = "const"


class InsightsForPeriodEnum(str, enum.Enum):
    day = "day"
    week = "week"
    month = "month"
    trimester = "trimester"
    year = "year"


class LogLevelEnum(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITITCAL"


class Settings(BaseSettings):
    load_pages: bool = True
    load_page_posts: bool = True
    load_page_insights: bool = True

    fb_pages_access_tokens: List[str] = []
    fb_pages_insights_for: InsightsForPeriodEnum = InsightsForPeriodEnum.day
    fb_pages_connections_limit: int = 1
    fb_pages_delay_per_request: float = 0
    fb_pages_version: str = "v10.0"
    fb_pages_retry_attempts: int = 3
    fb_pages_retry_delay_function: RetryDelayFunctionEnum = RetryDelayFunctionEnum.EXPO

    db_url: str

    email_to: str
    email_host: str
    email_port: int
    email_username: str
    email_password: str
    email_use_tls: bool = False
    email_use_ssl: bool = False

    log_file: Optional[str] = None
    log_file_level: LogLevelEnum = LogLevelEnum.INFO

    @classmethod
    @validator("email_use_tls", "email_use_ssl")
    def check_email_tls_ssl(cls, value: bool, values: Dict[str, Any]) -> bool:
        email_use_tls = bool(values.get("email_use_tls"))
        email_use_ssl = bool(values.get("email_use_ssl"))
        if email_use_ssl and email_use_tls:
            raise ValueError("Only one of 'email_use_tls' and 'email_use_ssl' can be 'True'")
        return value


    @classmethod
    @validator(
        "fb_pages_connections_limit",
        "fb_pages_delay_per_request",
        "fb_pages_retry_attempts",
        "email_port",
    )
    def check_non_negative(cls, value: float, values: Dict[str, Any]) -> float:
        if value < 0:
            raise ValueError(f"Must be non negative, not {value}")
        return value
