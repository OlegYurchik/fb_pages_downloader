import asyncio
import datetime
import math
from copy import deepcopy
from typing import Any, AsyncGenerator, Dict, Iterable, Optional

import yarl
import aiohttp
from facet import ServiceMixin
from loguru import logger


def expo(start_delay: float, attempt: int):
    return start_delay * (math.e ** attempt)


def const(start_delay: float, attempt: int):
    return start_delay


RETRY_DELAY_FUNCTIONS = {
    "expo": expo,
    "const": const,
}


class FacebookPagesService(ServiceMixin):
    BASE_URL = yarl.URL("https://graph.facebook.com")

    def __init__(
            self,
            connections_limit: int = 100,
            delay_per_request: float = 0,
            retry_attempts: int = 0,
            retry_delay_function: str = "expo",
            version: str = "v10.0",
    ):
        self._connections_limit = connections_limit
        self._delay_per_request = delay_per_request
        self._retry_attempts = retry_attempts
        self._retry_delay_function = RETRY_DELAY_FUNCTIONS.get(retry_delay_function)
        self._semaphore = asyncio.Semaphore(connections_limit)
        self._version = version
        self._session = None

    async def start(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.connector.TCPConnector(limit=self._connections_limit),
                raise_for_status=True,
            )
            logger.info("Facebook pages service started.")

    async def stop(self):
        if self._session is not None:
            await self._session.close()
            self._session = None
            logger.info("Facebook pages service stopped.")

    async def request(
            self,
            url: yarl.URL,
            params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        params = {} if params is None else deepcopy(params)
        exception = None
        attempt_number = 0

        async with self._semaphore:
            while attempt_number <= self._retry_attempts:
                try:
                    async with self._session.get(url=url, params=params) as response:
                        payload = await response.json()
                except aiohttp.ClientError as e:

                    logger.warning("Got exception: {}", e)
                    exception = e
                    attempt_number += 1
                    attempt_delay = self._retry_delay_function(
                        self._delay_per_request,
                        attempt_number,
                    )
                    await asyncio.sleep(attempt_delay)
                else:
                    break
            else:
                raise exception

            await asyncio.sleep(self._delay_per_request)

        return payload

    async def request_with_paging(
            self,
            url: yarl.URL,
            params: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Any, None]:
        while url:
            payload = await self.request(
                url=url,
                params=params,
            )
            for result in payload["data"]:
                yield result
            url = yarl.URL(payload.get("paging", {}).get("next", ""))
            params = None

    async def get_accounts(self, access_token: str) -> AsyncGenerator[Dict[str, Any], None]:
        url = self.BASE_URL / self._version / "me" / "accounts"
        params = {"access_token": access_token}
        async for account in self.request_with_paging(url=url, params=params):
            yield account

    async def get_page(self, page_id: str, access_token: str) -> Dict[str, Any]:
        url = self.BASE_URL / self._version / page_id
        params = {"access_token": access_token}
        return await self.request(url=url, params=params)

    async def get_page_published_posts(
            self,
            page_id: str,
            access_token: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        url = self.BASE_URL / self._version / page_id / "published_posts"
        params = {"access_token": access_token}
        async for post in self.request_with_paging(url=url, params=params):
            yield post

    async def get_page_insights(
            self,
            page_id: str,
            access_token: str,
            since: Optional[datetime.date] = None,
            metrics: Optional[Iterable[str]] = None,
            period: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        url = self.BASE_URL / self._version / page_id / "insights"
        params = {"access_token": access_token}
        if metrics is not None:
            params["metric"] = ",".join(metrics)
        if period is not None:
            params["period"] = period
        if since is not None:
            params["since"] = since.strftime("%Y-%m-%d")
        async for insight in self.request_with_paging(url=url, params=params):
            yield insight

    async def get_page_post(self, page_id: str, post_id: str, access_token: str) -> Dict[str, Any]:
        url = self.BASE_URL / self._version / f"{page_id}_{post_id}"
        params = {"access_token": access_token}
        return await self.request(url=url, params=params)

    async def get_page_post_attachments(
            self,
            page_id: str,
            post_id: str,
            access_token: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        url = self.BASE_URL / self._version / f"{page_id}_{post_id}" / "attachments"
        params = {"access_token": access_token}
        async for attachment in self.request_with_paging(url=url, params=params):
            yield attachment
