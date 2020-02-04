"""Constructs a pokedex from the pokemon db page"""

# from functools import lru_cache

from typing import Dict, List

import bs4

from src.config import POKEDEX
from src.data.poke_enums import PType
from src.data.stats import BaseStats
from src.data.typing import SpeciesId, VariantId


# @profile
def _parse_dex_entry(html):
    """Parses a single dex entry from the pokemon database.
    If the default form of the species has no variant name,
    the species name will be used as the variant name.
    """

    species_name = html.select_one("a.ent-name").string
    variant_name = (
        html.select_one("small").string if html.select_one("small") else species_name
    )

    typing = [PType[t.string] for t in html.select("td.cell-icon>a")]

    # This has to explicitly select one class to avoid selecting other html elements

    stat_names = [
        "hp",
        "attack",
        "defense",
        "special_attack",
        "special_defense",
        "speed",
    ]
    stats = [int(stat.string) for stat in html.select('td[class="cell-num"]')]
    stats = BaseStats(**dict(zip(stat_names, stats)))

    return str(species_name), str(variant_name), typing, stats


def scrape_pokedex():
    """Scrapes the pokedex for variants, typing, and base stats

    :returns: A tuple of species, variants, typing, stats.

    """

    # Note: We are using lxml to shave off half a second from the execution time.
    # This makes parsing of invalid documents more fragile
    pokedex_html = bs4.BeautifulSoup(POKEDEX.read_text(), "lxml")

    variants_html = pokedex_html.select("#pokedex > tbody > tr")
    # pokedex_html.find_all('tbody')

    pokedex = [_parse_dex_entry(dex_entry) for dex_entry in variants_html]
    return zip(*pokedex)
