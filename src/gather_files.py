"""Collects files from the config and stores them into the cache"""


from pathlib import Path
from time import sleep
from typing import ByteString

import requests
from loguru import logger

from config import URLS


def request_url(file: Path, url: ByteString, refresh_cache=False) -> None:
    """Fetches one url and stores the content in the cache"""
    if not refresh_cache and file.exists():
        logger.info(f"Skipping {url} since {file.absolute()} already exists")
        return

    req = requests.get(url=url)
    sleep(5)  # To be nice

    logger.debug(f"Requesting {file.absolute()} from {url}")
    if not req.ok:
        # TODO: Gracefully handle this case
        logger.error(f"Recieved error {req.status_code} from {req.url}")
        return

    try:
        file.touch()
        with file.open("w") as dest:
            dest.writelines(req.text)
    except NotADirectoryError:
        logger.error(f"{file.absolute()} is not a valid filepath")


def populate_cache():
    """Fills the cache with all the items from the URLS defined in the config file"""
    list(map(lambda kv: request_url(kv[0], kv[1]), URLS.items()))
