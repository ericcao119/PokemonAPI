"""Fetches the ability list from pokemondb"""

from typing import List

import bs4
import google.cloud.firestore_v1.client

from src.config import ABILITY_LIST
from src.data.ability import Ability
from src.utils.general import chunk_list


# Scraping
def _parse_ability(html: bs4.BeautifulSoup) -> Ability:
    """Takes a single list item and turns it into an ability
    """
    name = html.select_one('a[class="ent-name"]').text
    descr = html.select_one('td[class="cell-med-text"]').text

    return Ability(name=name, description=descr)


def scrape_abilities() -> List[Ability]:
    """Scrapes abilities"""
    html = bs4.BeautifulSoup(ABILITY_LIST.read_text(), "html.parser")

    ability_html = html.select('tr:has(> td:has(> a[class="ent-name"]))')
    abilities = [_parse_ability(i) for i in ability_html]
    return abilities


# Update database


def chunk_write(
    database: google.cloud.firestore_v1.client.Client,
    collection: str,
    iterable: List[Ability],
) -> None:
    """Executes a single batch write over an iterable
    TODO: Parameterize the function
    TODO: Assert on size of iterable
    """
    batch = database.batch()

    for ability in iterable:
        ref = database.collection(collection).document(ability.name)
        batch.set(ref, ability._asdict())

    batch.commit()


def write_abilties_to_firebase(database: google.cloud.firestore_v1.client.Client):
    """Specific function for writing to firebase. Will batch writes."""
    abilities = scrape_abilities()

    chunked_abilities = chunk_list(abilities, 500)

    for chunk in chunked_abilities:
        chunk_write(database, u"abilities", chunk)


def write_abilties(database) -> None:
    """Write abilities to the database of choice"""
    if isinstance(database, google.cloud.firestore_v1.client.Client):
        # dispatch
        write_abilties_to_firebase(database)
    else:
        raise ValueError("Unkown database type")
