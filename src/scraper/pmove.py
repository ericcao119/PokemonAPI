"""Scrape Moves"""

from pathlib import Path
from pprint import pprint
from typing import Final, Optional

import bs4
from loguru import logger

from src.config import MOVES_LIST
from src.data.pmove import PMove
from src.data.poke_enums import MoveCategory, PType


def parse_accuracy_string(string: str) -> Optional[int]:
    if string is None or string == "None":
        return None
    if string == "—":
        return None
    if string == "∞":
        return -1
    return int(string)


def parse_move(move_html):
    fields = move_html.select("td")

    title = str(fields[2]["data-filter-val"]).title()
    if title is None or title == "":
        title = "INVALID"

    mapping = {
        "name": str(fields[0].find("a").string),
        "ptype": PType[fields[1].find("a").string],
        "category": MoveCategory[title],
        "power": parse_accuracy_string(str(fields[3].string)),
        "accuracy": parse_accuracy_string(str(fields[4].string)),
        "pp": parse_accuracy_string(str(fields[5].string)),
        "tm": str(fields[6].string if fields[6].string is not None else ""),
        "effect": str(fields[7].string),
        "prob": parse_accuracy_string(str(fields[8].string)),
    }

    return PMove(**mapping)


def scrape_moves():
    from src.gather_files import populate_cache

    populate_cache()

    strainer = bs4.SoupStrainer(id="moves")
    moves_html = bs4.BeautifulSoup(MOVES_LIST.read_text(), "lxml", parse_only=strainer)

    moves = moves_html.select("tbody tr")

    return [parse_move(move) for move in moves]
