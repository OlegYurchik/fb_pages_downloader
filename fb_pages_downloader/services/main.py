import asyncio
import datetime
from typing import Any, Dict, List, Type

from facet import ServiceMixin
from loguru import logger

from .database import DatabaseService
from .email import EmailService
from .fb_pages import FacebookPagesService
from ..models import (
    PagePostEngagementsDay,
    PagePostImpressionNonviralUniqueDay,
    PagePostImpressionOrganicUniqueDay,
    PagePostImpressionPaidUniqueDay,
    PagePostImpressionUniqueDay,
    PagePostImpressionViralUniqueDay,
    PageVideoViewsAutoplayedDay,
    PageVideoViewsClickToPlayDay,
    PageVideoViewsDay,
    PageVideoViewsOrganicDay,
    PageVideoViewsPaidDay,
    PageVideoViewsUniqueDay,
    PageVideoViewTimeDay,
    PostActivityByActionTypeUniqueLifetime,
    PostClicksByTypeUniqueLifetime,
    PostReactionsByTypeTotalUniqueLifetime,
)
from ..models.base import PageInsightAbstractModel, PagePostInsightAbstractModel
from ..settings import InsightsForPeriodEnum, Settings


class MainService(ServiceMixin):
    """
    Service for loading data from Facebook Pages API and saving to database

    All methods in service run concurrently, tasks can run another tasks.
    Next scheme describes tasks relations:

                       ______
                      |start|
                      |_____|
                   ______|_____
           _______|______     |
           |load_account|    ...
           |____________|
         ________|____________________________________________________________________
    _____|_____   |   ________|________   |                                 _________|_________
    |load_page|  ...  |load_page_posts|  ...                                |load_page_insights|
    |_________|       |_______________|                                     |__________________|
                  ____________|__________________________________________________________      |
    ______________|_____________   |              |   |  ______________|_____________   |      |
    |load_page_post_attachments|  ...             |   |  |update_or_create_page_post|  ...     |
    |__________________________|                  |   |  |__________________________|          |
                  |____________________________   |   |                     ___________________|
    ______________|________________________   |   |   |     ________________|______________    |
    |update_or_create_page_post_attachment|  ...  |   |     |update_or_create_page_insight|   ...
    |_____________________________________|       |   |     |_____________________________|
                          ________________________|   |
                          |load_page_post_insights|  ...
                          |_______________________|
                                      |_____________________
                     _________________|_________________   |
                    |update_or_create_page_post_insight|  ...
                    |__________________________________|
    """

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S+0000"
    PAGE_INSIGHT_MODELS = (
        PagePostEngagementsDay,
        PagePostImpressionNonviralUniqueDay,
        PagePostImpressionOrganicUniqueDay,
        PagePostImpressionPaidUniqueDay,
        PagePostImpressionUniqueDay,
        PagePostImpressionViralUniqueDay,
        PageVideoViewsAutoplayedDay,
        PageVideoViewsClickToPlayDay,
        PageVideoViewsDay,
        PageVideoViewsOrganicDay,
        PageVideoViewsPaidDay,
        PageVideoViewsUniqueDay,
        PageVideoViewTimeDay,
    )
    PAGE_POST_INSIGHT_MODELS = (
        PostActivityByActionTypeUniqueLifetime,
        PostClicksByTypeUniqueLifetime,
        PostReactionsByTypeTotalUniqueLifetime,
    )
    TIMEDELTA_MAPPING = {
        InsightsForPeriodEnum.day.value: datetime.timedelta(days=1),
        InsightsForPeriodEnum.week.value: datetime.timedelta(weeks=1),
        InsightsForPeriodEnum.month.value: datetime.timedelta(days=30),
        InsightsForPeriodEnum.trimester: datetime.timedelta(days=90),
        InsightsForPeriodEnum.year.value: datetime.timedelta(days=365),
    }

    def __init__(self, settings: Settings):
        self.settings = settings
        self.facebook_pages_service = FacebookPagesService(
            connections_limit=settings.fb_pages_connections_limit,
            delay_per_request=settings.fb_pages_delay_per_request,
            retry_attempts=settings.fb_pages_retry_attempts,
            retry_delay_function=settings.fb_pages_retry_delay_function.value,
            version=settings.fb_pages_version,
        )
        self.database_service = DatabaseService(
            db_url=settings.db_url,
        )
        self.email_service = EmailService(
            to=settings.email_to,
            host=settings.email_host,
            port=settings.email_port,
            username=settings.email_username,
            password=settings.email_password,
            use_tls=settings.email_use_tls,
            use_ssl=settings.email_use_ssl,
        )
        self._logger_email_sink_id = None
        self._logger_file_sink_ids = []

    @property
    def dependencies(self) -> List[ServiceMixin]:
        return [
            self.facebook_pages_service,
            self.database_service,
            self.email_service,
        ]

    @classmethod
    def to_datetime(cls, date_string: str) -> datetime.datetime:
        return datetime.datetime.strptime(date_string, cls.DATE_FORMAT)

    async def start(self):
        logger.info("Main service started.")
        self._logger_email_sink_id = logger.add(self.email_service.logger_sink, level="ERROR")
        for filename, level in self.settings.log_files.items():
            self._logger_file_sink_ids.append(logger.add(filename, level=level.value))

        await asyncio.gather(*(
            self.load_account(access_token)
            for access_token in self.settings.fb_pages_access_tokens
        ))

    async def stop(self):
        logger.remove(self._logger_email_sink_id)
        for sink_id in self._logger_file_sink_ids:
            logger.remove(sink_id)
        self._logger_file_sink_ids.clear()
        logger.info("Main service stopped.")

    @logger.catch()
    async def load_account(self, access_token: str):
        accounts_generator = self.facebook_pages_service.get_accounts(
            access_token=access_token,
        )

        tasks = []
        async for account in accounts_generator:
            logger.info("Downloaded account: account_id={}", account["id"])
            logger.debug("Account payload: {}", account)

            page_id = account["id"]
            access_token = account["access_token"]

            if self.settings.load_pages:
                task = asyncio.create_task(self.load_page(
                    page_id=page_id,
                    access_token=access_token,
                ))
                tasks.append(task)

            if self.settings.load_page_posts:
                task = asyncio.create_task(self.load_page_posts(
                    page_id=page_id,
                    access_token=access_token,
                ))
                tasks.append(task)

            if self.settings.load_page_insights:
                for view_model in self.PAGE_INSIGHT_MODELS:
                    task = asyncio.create_task(self.load_page_insights(
                        view_model=view_model,
                        page_id=page_id,
                        access_token=access_token,
                    ))
                    tasks.append(task)

        if tasks:
            await asyncio.wait(tasks)

    @logger.catch()
    async def load_page(self, page_id: str, access_token: str):
        data = await self.facebook_pages_service.get_page(
            page_id=page_id,
            access_token=access_token,
        )
        logger.info("Downloaded page: page_id={}", page_id)
        logger.debug("Page payload: {}", data)
        fields = {
            "id": data["id"],
            "name": data["name"],
            "about": data.get("about"),
            "affiliation": data.get("affiliation"),
            "app_id": data.get("app_id"),
            "artists_we_like": data.get("artists_we_like"),
            "bio": data.get("bio"),
            "birthday": data.get("birthday"),
            "booking_agent": data.get("booking_agent"),
            "built": data.get("built"),
            "can_check_in": data.get("can_checkin"),
            "can_post": data.get("can_post"),
            "category": data.get("category"),
            "category_list": data.get("category_list"),
            "check_ins": data.get("checkins"),
            "contact_address": data.get("contact_address"),
            "current_location": data.get("current_location"),
            "description": data.get("description"),
            "directed_by": data.get("directed_by"),
            "emails": data.get("emails"),
            "hours": data.get("hours"),
            "link": data.get("link"),
            "location": data.get("location"),
            "mission": data.get("mission"),
            "username": data.get("username"),
            "were_here_count": data.get("were_here_count"),
            "whatsapp_number": data.get("whatsapp_number"),
        }

        page = await self.database_service.get_page(id=page_id)
        if page:
            await self.database_service.update_page(record=page, fields=fields)
            logger.info("Updated page: page_id={}", page_id)
        else:
            await self.database_service.create_page(fields=fields)
            logger.info("Created page: page_id={}", page_id)
        logger.debug("Page fields: {}", fields)

    @logger.catch()
    async def load_page_posts(self, page_id: str, access_token: str):
        generator = self.facebook_pages_service.get_page_published_posts(
            page_id=page_id,
            access_token=access_token,
        )

        tasks = []
        async for page_post in generator:
            logger.info("Downloaded page post: page_post_id={}", page_post["id"])
            logger.debug("Page post payload: {}", page_post)

            _, post_id = page_post["id"].split("_")

            task = asyncio.create_task(self.update_or_create_page_post(data=page_post))
            tasks.append(task)

            if self.settings.load_page_post_attachments:
                task = asyncio.create_task(self.load_page_post_attachments(
                    page_id=page_id,
                    post_id=post_id,
                    access_token=access_token,
                ))
                tasks.append(task)

            if self.settings.load_page_post_insights:
                for view_model in self.PAGE_POST_INSIGHT_MODELS:
                    task = asyncio.create_task(self.load_page_post_insights(
                        view_model=view_model,
                        page_id=page_id,
                        post_id=post_id,
                        access_token=access_token,
                    ))
                    tasks.append(task)

        if tasks:
            await asyncio.wait(tasks)

    @logger.catch()
    async def update_or_create_page_post(self, data: Dict[str, Any]):
        id_ = data["id"]
        page_id, post_id = id_.split("_")
        fields = {
            "id": id_,
            "page_id": page_id,
            "post_id": post_id,
            "created_time": self.to_datetime(data["created_time"]),
            "eligible_for_promotion": data.get("is_eligible_for_promotion"),
            "expired": data.get("is_expired"),
            "full_picture": data.get("full_picture"),
            "hidden": data.get("is_hidden"),
            "message": data.get("message"),
            "popular": data.get("is_popular"),
            "published": data.get("is_published"),
            "privacy": data.get("privacy"),
            "promotable_id": data.get("promotable_id"),
            "shares_count": data.get("shares"),
            "status_type": data.get("status_type"),
            "story": data.get("story"),
            "updated_time": data.get("updated_time"),
        }

        page_post = await self.database_service.get_page_post(id=id_)
        if page_post:
            await self.database_service.update_page_post(record=page_post, fields=fields)
            logger.info("Updated page post: page_post_id={}", id_)
        else:
            await self.database_service.create_page_post(fields=fields)
            logger.info("Created page post: page_post_id={}", id_)
        logger.debug("Page post fields: {}", fields)

    @logger.catch()
    async def load_page_post_attachments(self, page_id: str, post_id: str, access_token: str):
        generator = self.facebook_pages_service.get_page_post_attachments(
            page_id=page_id,
            post_id=post_id,
            access_token=access_token,
        )

        tasks = []
        async for page_post_attachment in generator:
            logger.info("Downloaded page post attachment: page_id={}; post_id={}", page_id, post_id)
            logger.debug("Page post attachment payload: {}", page_post_attachment)

            task = asyncio.create_task(self.update_or_create_page_post_attachment(
                page_id=page_id,
                post_id=post_id,
                data=page_post_attachment,
            ))
            tasks.append(task)

        if tasks:
            await asyncio.wait(tasks)

    @logger.catch()
    async def update_or_create_page_post_attachment(
            self,
            page_id: str,
            post_id: str,
            data: Dict[str, Any],
    ):
        fields = {
            "page_id": page_id,
            "post_id": post_id,
            "type": data["type"],
            "url": data.get("url"),
            "description": data.get("description"),
            "title": data.get("title"),
            "target": data.get("target"),
        }
        page_post_attachment = await self.database_service.get_page_post_attachment(**fields)
        if page_post_attachment:
            await self.database_service.update_page_post_attachment(
                record=page_post_attachment,
                fields=fields,
            )
            logger.info("Updated page post attachment: page_id={}; post_id={}", page_id, post_id)
            logger.debug("Page post attachment fields: {}", fields)

    @logger.catch()
    async def load_page_post_insights(
            self,
            view_model: Type[PagePostInsightAbstractModel],
            page_id: str,
            post_id: str,
            access_token: str,
    ):
        since = datetime.datetime.now()
        since -= self.TIMEDELTA_MAPPING[self.settings.fb_pages_insights_for.value]
        generator = self.facebook_pages_service.get_insights(
            object_id=f"{page_id}_{post_id}",
            access_token=access_token,
            since=since,
            metrics=[view_model.METRIC],
            period=view_model.PERIOD.value,
        )

        tasks = []
        async for page_post_insight in generator:
            logger.info(
                "Downloaded page post insight: page_id={}; post_id={}; metric={}; "
                "page_insight_id={}",
                page_id,
                post_id,
                view_model.METRIC,
                page_post_insight["id"],
            )
            logger.debug("Page post insight payload: {}", page_post_insight)

            task = asyncio.create_task(self.update_or_create_page_post_insight(
                view_model=view_model,
                page_id=page_id,
                post_id=post_id,
                data=page_post_insight,
            ))
            tasks.append(task)

        if tasks:
            await asyncio.wait(tasks)

    @logger.catch()
    async def update_or_create_page_post_insight(
            self,
            view_model: Type[PagePostInsightAbstractModel],
            page_id: str,
            post_id: str,
            data: Dict[str, Any],
    ):
        get_function = self.database_service.generate_get_function(view_model)
        create_function = self.database_service.generate_create_function(view_model)
        update_function = self.database_service.generate_update_function(view_model)

        for value in data["values"]:
            fields = {
                "m_period": data["period"],
                "page_id": page_id,
                "post_id": post_id,
                **view_model.parse_value(value["value"]),
            }
            record = await get_function(page_id=page_id, post_id=post_id)
            if record is None:
                await create_function(fields=fields)
                logger.info(
                    "Created page post insight: page_id={}; post_id={}; metric={}",
                    page_id,
                    post_id,
                    view_model.METRIC,
                )
            else:
                await update_function(record=record, fields=fields)
                logger.info(
                    "Updated page post insight: page_id={}; post_id={}; metric={}",
                    page_id,
                    post_id,
                    view_model.METRIC,
                )
            logger.debug("Page post insight fields: {}", fields)

    @logger.catch()
    async def load_page_insights(
            self,
            view_model: Type[PageInsightAbstractModel],
            page_id: str,
            access_token: str,
    ):
        since = datetime.datetime.now()
        since -= self.TIMEDELTA_MAPPING[self.settings.fb_pages_insights_for.value]
        generator = self.facebook_pages_service.get_insights(
            object_id=page_id,
            access_token=access_token,
            since=since,
            metrics=[view_model.METRIC],
            period=view_model.PERIOD.value,
        )

        tasks = []
        async for page_insight in generator:
            logger.info(
                "Downloaded page insight: page_id={}; metric={}; page_insight_id={}",
                page_id,
                view_model.METRIC,
                page_insight["id"],
            )
            logger.debug("Page insight payload: {}", page_insight)

            task = asyncio.create_task(self.update_or_create_page_insight(
                view_model=view_model,
                page_id=page_id,
                data=page_insight,
            ))
            tasks.append(task)

        if tasks:
            await asyncio.wait(tasks)

    @logger.catch()
    async def update_or_create_page_insight(
            self,
            view_model: Type[PageInsightAbstractModel],
            page_id: str,
            data: Dict[str, Any],
    ):
        get_function = self.database_service.generate_get_function(view_model)
        create_function = self.database_service.generate_create_function(view_model)
        update_function = self.database_service.generate_update_function(view_model)

        for value in data["values"]:
            fields = {
                "m_period": data["period"],
                "m_date": value["end_time"],
                "page_id": page_id,
                **view_model.parse_value(value["value"]),
            }
            record = await get_function(m_date=fields["m_date"], page_id=page_id)
            if record is None:
                await create_function(fields=fields)
                logger.info(
                    "Created page insight: page_id={}; metric={}; date={}",
                    page_id,
                    view_model.METRIC,
                    value["end_time"],
                )
            else:
                await update_function(record=record, fields=fields)
                logger.info(
                    "Updated page insight: page_id={}; metric={}; date={}",
                    page_id,
                    view_model.METRIC,
                    value["end_time"],
                )
            logger.debug("Page insight fields: {}", fields)
