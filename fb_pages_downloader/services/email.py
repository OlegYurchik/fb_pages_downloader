from async_sender import Mail
from facet import ServiceMixin
from loguru import logger


class EmailService(ServiceMixin):
    def __init__(
            self,
            to: str,
            host: str,
            port: int,
            username: str,
            password: str,
            use_tls: bool = False,
            use_ssl: bool = False,
    ):
        self._to = to
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls
        self._use_ssl = use_ssl
        self._sender = None

    async def start(self):
        if self._sender is None:
            self._sender = Mail(
                hostname=self._host,
                port=self._port,
                use_tls=self._use_tls,
                username=self._username,
                password=self._password,
            )
            logger.info("Email service started.")

    async def stop(self):
        if self._sender is not None:
            self._sender = None
            logger.info("Email service stopped.")

    async def logger_sink(self, message: str):
        logger.info("Sending exception message...")
        # await self._sender.send_message(
        #     to=self._to,
        #     body=message,
        # )
        logger.info("Exception message sent.")
