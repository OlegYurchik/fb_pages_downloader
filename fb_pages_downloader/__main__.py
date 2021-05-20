import asyncio
import signal
from argparse import ArgumentParser

from loguru import logger

from .services import EmailService, MainService
from .settings import Settings


async def main(main_service: MainService, email_service: EmailService):
    """
    Main function with running EmailService and MailService
    """
    async with email_service, main_service:
        pass


parser = ArgumentParser(
    description="Facebook Pages API Data Downloader to SQL database",
)
parser.add_argument(
    "-e", "--env",
    type=str,
    dest="env_filepath",
    required=False,
    help="Environment filepath",
)

arguments = parser.parse_args()

if arguments.env_filepath:
    settings = Settings(_env_file=arguments.env_filepath)
    logger.info("Settings loaded from '{}'", arguments.env_filepath)
else:
    settings = Settings()

main_service = MainService(
    settings=settings,
)
email_service = EmailService(
    to=settings.email_to,
    host=settings.email_host,
    port=settings.email_port,
    username=settings.email_username,
    password=settings.email_password,
    use_ssl=settings.email_use_ssl,
    use_tls=settings.email_use_tls,
)

loop = asyncio.get_event_loop()
loop.add_signal_handler(
    signal.SIGTERM,
    lambda: loop.run_until_complete(email_service.logger_sink(message="Send SIGTERM")),
)
coroutine = main(main_service=main_service, email_service=email_service)
loop.run_until_complete(coroutine)
