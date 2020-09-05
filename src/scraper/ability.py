"""Fetches the ability list from pokemondb"""

import re
from functools import cached_property
from pathlib import Path
from pprint import pprint
from typing import Final, List

import bs4
from loguru import logger

from src.config import ABILITY_LIST
from src.data.ability import Ability
from src.gather_files import request_abilityurl_pokemondb
from src.utils.general import chunk_list

# RE_MAX_PP = re.compile(r"\(max. (\d+)\)")
# RE_GENERATION = re.compile(r"Generation (\d+)")


class AbilityPage:

    ABILITY_NAME_SELECTOR: Final[str] = "h1"
    EFFECT_SELECTOR: Final[str] = "h2:contains('Effect')"
    ABILITY_DESCR_TABLE: Final[str] = "h2:contains('Game descriptions') + div > table"

    def __init__(self, html: Path):
        self._soup = bs4.BeautifulSoup(html.read_text(), "lxml")

    @cached_property
    def ability_name(self) -> str:
        h1 = self._soup.select_one(AbilityPage.ABILITY_NAME_SELECTOR)
        return str(h1.contents[0]).strip()

    @cached_property
    def effect(self) -> str:
        html: bs4.Tag = self._soup.select_one(AbilityPage.EFFECT_SELECTOR)
        text = []
        for i in html.next_siblings:
            if i.name == "h2":
                break

            if i.name == "p":
                text.append(i.get_text())

        return "\n".join(text)

    @cached_property
    def description(self) -> str:
        html: bs4.Tag = self._soup.select_one(AbilityPage.ABILITY_DESCR_TABLE)
        return str(html("td")[-1].string)

    @property
    def ability(self) -> Ability:
        return Ability(self.ability_name, self.effect, self.description)

    def __str__(self) -> str:
        return self.ability.__str__()

    def __repr__(self) -> str:
        return self.ability.__repr__()


def scrape_ability_urls() -> List[str]:
    html = bs4.BeautifulSoup(ABILITY_LIST.read_text(), "lxml")
    return [i["href"] for i in html.select("#abilities a")]


def scrape_abilities() -> List[Ability]:
    """Scrapes abilities"""
    ability_urls = scrape_ability_urls()

    files = [request_abilityurl_pokemondb(url) for url in ability_urls]

    abilities = [AbilityPage(i).ability for i in files]
    return abilities


# Update database
