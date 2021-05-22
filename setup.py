from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name="fb-pages-downloader",
    version="1.0.0",
    author="Oleg Yurchik",
    author_email="oleg.yurchik@protonmail.com",
    url="https://github.com/OlegYurchik/fb_pages_downloader",
    description="",
    long_description=open(join(dirname(__file__), "README.md")).read(),
    packages=find_packages(),
    install_requires=[
        "aiohttp==3.7.4",
        "async_sender==1.4.3",
        "facet==0.7.0",
        "loguru==0.5.3",
        "pydantic[dotenv]==1.8.2",
        "tortoise-orm[asyncpg]==0.17.2",
        "yarl==1.6.3",
    ],
    test_suite="fb_pages_downloader.tests",
)