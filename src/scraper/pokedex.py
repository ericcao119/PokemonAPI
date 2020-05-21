"""Constructs a pokedex from the pokemon db page"""

# from functools import lru_cache

from functools import lru_cache
from typing import Dict, Iterable, List, Tuple

import bs4

from src.config import POKEDEX
from src.data.poke_enums import PType
from src.data.stats import BaseStats
from src.data.typing import SpeciesId, VariantId


# @profile
def _parse_dex_entry(
    html: bs4.BeautifulSoup,
) -> Tuple[str, str, List[PType], BaseStats, str]:
    """Parses a single dex entry from the pokemon database.
    If the default form of the species has no variant name,
    the species name will be used as the variant name.

    :returns: A tuple of the species name as listed, the variant name as listed,
        the typing of the pokemon, the base stats of the pokemon, and the relative
        of the pokemon
    """

    name_link = html.select_one("a.ent-name")
    small = html.select_one("small")
    species_name = str(name_link.string)
    variant_name = str(small.string) if small else species_name

    url = str(name_link["href"])

    # print(html)
    typing = [PType[t.string] for t in html.find_all("a", attrs={"class": "type-icon"})]

    # This has to explicitly select one class to avoid selecting other html elements

    stat_names = [
        "hp",
        "attack",
        "defense",
        "special_attack",
        "special_defense",
        "speed",
    ]
    stat_vals = [
        int(stat.string)
        for stat in html.find_all("td", attrs={"class": "cell-num"})[-6:]
    ]
    stats = BaseStats(**dict(zip(stat_names, stat_vals)))

    return species_name, variant_name, typing, stats, url


@lru_cache(maxsize=1)
def scrape_pokedex() -> List:
    """Scrapes the pokedex for variants, typing, and base stats

    :returns: A tuple of species, variants, typing, stats, url.

    """

    # Note: We are using lxml to shave off half a second from the execution time.
    # This makes parsing of invalid documents more fragile
    pokedex_html = bs4.BeautifulSoup(POKEDEX.read_text(), "lxml")
    variants_html = pokedex_html.select("#pokedex > tbody > tr")
    pokedex = [_parse_dex_entry(dex_entry) for dex_entry in variants_html]
    return list(zip(*pokedex))
