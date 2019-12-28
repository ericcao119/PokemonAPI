from pathlib import Path

from time import sleep
import requests
from loguru import logger

from config import URLS

from typing import ByteString


def request_url(file: Path, url: ByteString, refresh_cache=False):
    if not refresh_cache and file.exists():
        logger.info(f'Skipping {url} since {file.absolute()} already exists')

    req = requests.get(url=url)
    sleep(10)  # To be nice

    logger.debug(f'Requesting {file.absolute()} from {url}')
    if not req.ok:
        # TODO:
        logger.error(f'Recieved error {req.status_code} from {req.url}')
        return

    try:
        file.touch()
        with file.open('w') as dest:
            dest.writelines(req.text)
    except NotADirectoryError:
        logger.error(f'{file.absolute()} is not a valid filepath')


def populate_cache():
    list(map(lambda kv: request_url(kv[0], kv[1]), URLS.items()))
