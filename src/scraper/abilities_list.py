import bs4

import google.cloud.firestore_v1.client

from typing import List
from config import AbilityList
from src.utils.general import chunk_list
from src.data.ability import Ability
from src.databases.firestore import get_client


# Scraping
def parse_ability(html: bs4.BeautifulSoup) -> Ability:
    name = html.select_one('a[class="ent-name"]').text
    descr = html.select_one('td[class="cell-med-text"]').text

    return Ability(name=name, description=descr)


def scrape_abilities() -> List[Ability]:
    html = bs4.BeautifulSoup(AbilityList.read_text(), 'html.parser')

    ability_html = [a for a in html.select(
        'tr:has(> td:has(> a[class="ent-name"]))')]
    abilities = [parse_ability(i) for i in ability_html]
    return abilities

# Update database


def chunk_write(db: google.cloud.firestore_v1.client.Client,
                collection: str, iterable: List[Ability]) -> None:
    batch = db.batch()

    for ability in iterable:
        ref = db.collection(collection).document(ability.name)
        batch.set(ref, ability.asdict())

    batch.commit()


def write_abilties_to_firebase(db: google.cloud.firestore_v1.client.Client):
    abilities = scrape_abilities()

    chunked_abilities = chunk_list(abilities, 500)

    for chunk in chunked_abilities:
        chunk_write(db, u'abilities', chunk)


def write_abilties(db) -> None:
    """"""
    if isinstance(db, google.cloud.firestore_v1.client.Client):
        # dispatch
        write_abilties_to_firebase(db)
        pass
    else:
        raise ValueError('Unkown database type')
