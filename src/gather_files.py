"""Collects files from the config and stores them into the cache"""


from pathlib import Path
from time import sleep
from typing import Union

import requests
from loguru import logger

from src.config import (
    BULBADEX_STUB,
    DBDEX_STUB,
    MOVE_POKEDB_DIR,
    POKEMONDB_STUB,
    SPECIES_POKEDB_DIR,
    URLS,
)
from src.data.typing import SpeciesId
from src.utils.general import normalize_unicode, rate_limited


def request_pokeurl_pokemondb(species: SpeciesId) -> Path:
    """Request a pokemon entry from PokemonDB"""
    # TODO: Restructure to request by url
    species_file: Path = (SPECIES_POKEDB_DIR / (species + ".html")).absolute()
    species = (
        species.replace("♂", "-m")
        .replace("♀", "-f")
        .replace(" ", "-")
        .replace(".", "")
        .replace(":", "")
        .replace("'", "")
    )
    url = DBDEX_STUB + normalize_unicode(species).lower()
    request_url(species_file, url)
    return species_file


def request_moveurl_pokemondb(relative_url: str) -> Path:
    """Request a pokemon entry from PokemonDB.
    Move URL should be of the form /move/{move_name}"""

    if not relative_url.startswith("/move/"):
        raise ValueError("Move url not of the correct form")

    move = relative_url[6:]

    move_file: Path = (MOVE_POKEDB_DIR / (move + ".html")).absolute()

    request_url(move_file, POKEMONDB_STUB + relative_url)
    return move_file


@rate_limited(0.333)
def _request_url(file: Path, url: Union[str, bytes]) -> None:
    logger.debug(f"Requesting {file.absolute()} from {str(url)}")
    req = requests.get(url=url)

    if not req.ok:
        # TODO: Gracefully handle this case
        logger.error(f"Recieved error {req.status_code} from {req.url}")
        req.raise_for_status()

    try:
        file.touch()
        with file.open("w") as dest:
            dest.writelines(req.text)
    except NotADirectoryError:
        logger.error(f"{file.absolute()} is not a valid filepath")


def request_url(file: Path, url: Union[str, bytes], refresh_cache=False) -> None:
    """Fetches one url and stores the content in the cache"""
    if not refresh_cache and file.exists():
        logger.debug(f"Skipping {str(url)} since {file.absolute()} already exists")
        return

    _request_url(file, url)


def populate_cache():
    """Fills the cache with all the items from the URLS defined in the config file"""
    list(map(lambda kv: request_url(kv[0], kv[1]), URLS.items()))
