"""Scrape items"""

from pathlib import Path
from pprint import pprint
from typing import Final

import bs4
from loguru import logger

from src.config import ITEMS_LIST
from src.data.item import Item
from src.data.poke_enums import ItemCategory


def parse_item(item_html):
    fields = item_html.select("td")

    mapping = {
        "name": str(fields[0].find("a").string),
        "category": ItemCategory[str(fields[1].string).title().replace(" ", "")],
        "description": str(fields[2].string if fields[2].string is not None else ""),
    }

    return Item(**mapping)


def scrape_items():
    from src.gather_files import populate_cache

    populate_cache()
    strainer = bs4.SoupStrainer("table")
    items_html = bs4.BeautifulSoup(ITEMS_LIST.read_text(), "lxml", parse_only=strainer)

    items = items_html.select("tbody tr")

    return [parse_item(item) for item in items]
