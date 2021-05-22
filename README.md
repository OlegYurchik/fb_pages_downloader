# Facebook Pages Downloader

## Prepare for running

You need to install all requirements

```shell script
cd fb_pages_downloader
pip install .
```

After that you should create your `.env` file from template

```shell script
cp .env.template .env
```

And modify it.

If you don't want create `.env` you can define environment variables with name and
values like from `.env.template`.

## Run

```shell script
python -m fb_pages_downloader -e .env
```

If you define environment variables, you can run withou `.env`

```shell script
python -m fb_pages_downloader
```
