"""Scrape Moves"""

import re
from functools import cached_property
from pathlib import Path
from pprint import pprint
from typing import Final, List, Optional

import bs4
from loguru import logger

from src.config import MOVES_LIST
from src.data.pmove import PMove
from src.data.poke_enums import MoveCategory, PType
from src.gather_files import request_moveurl_pokemondb
from src.utils.general import normalize_unicode

RE_MAX_PP = re.compile(r"\(max. (\d+)\)")
RE_GENERATION = re.compile(r"Generation (\d+)")


class MovePage:

    MOVE_NAME_SELECTOR: Final[str] = "h1"
    MOVE_DATA_SELECTOR: Final[str] = "h2 + table.vitals-table > tbody"
    TM_SELECTOR: Final[str] = "h3 + table.vitals-table > tbody"
    EFFECT_SELECTOR: Final[str] = "#move-effects"
    ZMOVE_EFFECT_SELECTOR: Final[str] = "h3:contains('Z-Move effects')"
    TARGET_DESCR_SELECTOR: Final[str] = "p.mt-descr"
    MOVE_DESCR_TABLE: Final[str] = "#move-descr + div > table.vitals-table > tbody"

    def __init__(self, path: Path):
        self._soup = bs4.BeautifulSoup(path.read_text(), "lxml")
        self._move_data = self._soup.select_one(MovePage.MOVE_DATA_SELECTOR)

    @cached_property
    def name(self) -> str:
        h1 = self._soup.select_one("h1")
        return str(h1.contents[0]).strip()

    @cached_property
    def ptype(self) -> PType:
        return PType[self._move_data.select_one("a.type-icon").string]

    @cached_property
    def category(self) -> MoveCategory:
        html = self._move_data.select_one("th:contains('Category') + td")
        string = html.get_text().strip()

        if string == "—":
            return MoveCategory.NoCategory
        return MoveCategory[string]

    @cached_property
    def power(self) -> float:
        html = self._move_data.select_one("th:contains('Power') + td")
        string = html.string.strip()
        if string == "—":
            return float("nan")
        if string == "∞":
            return float("inf")
        return float(html.string.strip())

    @cached_property
    def accuracy(self) -> float:
        html = self._move_data.select_one("th:contains('Accuracy') + td")
        string = html.string.strip()
        if string == "—":
            return float("nan")
        if string == "∞":
            return float("inf")
        return float(html.string.strip())

    @cached_property
    def pp(self) -> Optional[int]:
        html = self._move_data.select_one("th:contains('PP') + td")
        string = html.contents[0].strip()
        if string == "—":
            return None
        return int(string)

    @cached_property
    def max_pp(self) -> Optional[int]:
        html = self._move_data.select_one("th:contains('PP') + td")

        if html.string is not None and html.string.strip() == "—":
            return None

        string = html.contents[1].string.strip()
        match = RE_MAX_PP.search(string)

        if match:
            string = match.group(1)
        else:
            logger.error("Could not find / parse max PP. Using default PP value")
            return self.pp

        if string == "—":
            raise ValueError("Should not be NULL")
            return None
        return int(string)

    @cached_property
    def generation_introduced(self) -> Optional[int]:
        html = self._move_data.select_one("th:contains('Introduced') + td")
        string = html.string.strip()
        match = RE_GENERATION.search(string)

        if match:
            string = match.group(1)
        else:
            logger.error("Did not generation")
            raise ValueError("Did not find generation")

        if string == "—":
            return None
        return int(string)

    @cached_property
    def tm(self) -> Optional[int]:
        html: bs4.Tag = self._soup.select_one(MovePage.TM_SELECTOR)
        if html is None:
            return None

        if normalize_unicode(html("th")[-1].get_text().strip()) != "Sword/Shield":
            return None

        return int(html("td")[-1].string[2:])

    @cached_property
    def effect(self) -> str:
        html: bs4.Tag = self._soup.select_one(MovePage.EFFECT_SELECTOR)
        text = []
        for i in html.next_siblings:
            if i.name == "h3":
                break

            if i.name == "p":
                text.append(i.get_text())

        return "\n".join(text)

    @cached_property
    def zmove_effect(self) -> Optional[str]:
        html: bs4.Tag = self._soup.select_one(MovePage.ZMOVE_EFFECT_SELECTOR)

        if html is None:
            return None

        text = []
        for i in html.next_siblings:
            if i.name == "h3":
                break

            if i.name == "p":
                text.append(i.get_text())

        return "\n".join(text)

    @cached_property
    def target_description(self) -> str:
        html: bs4.Tag = self._soup.select_one(MovePage.TARGET_DESCR_SELECTOR)

        return str(html.string).strip()

    @cached_property
    def description(self) -> str:
        html: bs4.Tag = self._soup.select_one(MovePage.MOVE_DESCR_TABLE)
        return str(html("td")[-1].string)

    @cached_property
    def tr(self) -> Optional[int]:
        # TODO: PokemonDb does not list this yet
        return None

    @property
    def move(self) -> PMove:
        return PMove(
            self.name,
            self.ptype,
            self.category,
            self.power,
            self.accuracy,
            self.pp,
            self.max_pp,
            self.generation_introduced,
            self.tm,
            self.tr,
            self.effect,
            self.zmove_effect,
            self.description,
            self.target_description,
        )

    def __str__(self) -> str:
        return self.move.__str__()

    def __repr__(self) -> str:
        return self.move.__repr__()


def get_move_url(move_html: bs4.BeautifulSoup) -> str:
    fields = move_html.select("td")
    return fields[0].find("a")["href"]


def scrape_moves() -> List[PMove]:
    from src.gather_files import populate_cache

    populate_cache()

    strainer = bs4.SoupStrainer(id="moves")
    moves_html = bs4.BeautifulSoup(MOVES_LIST.read_text(), "lxml", parse_only=strainer)

    moves = moves_html.select("tbody tr")

    urls = [get_move_url(move) for move in moves]
    files = [request_moveurl_pokemondb(url) for url in urls]

    # 0 - 10,000 Volt thunderbolt, 1 - Absorb, 7 - Acrobatics
    moves = [MovePage(i).move for i in files]

    return moves
