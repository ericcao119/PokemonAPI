import bs4
from typing import List

from pymongo import MongoClient

from config import AbilityList, CODEC_OPTIONS
from src.data.ability import Ability


def parse_ability(html: bs4.BeautifulSoup) -> Ability:
    name = html.select_one('a[class="ent-name"]').text
    descr = html.select_one('td[class="cell-med-text"]').text

    return Ability(name=name, description=descr)


def scrape_abilities() -> List[Ability]:
    with open(AbilityList, 'r') as f:
        html = bs4.BeautifulSoup(f.read(), 'html.parser')

    ability_html = [a for a in html.select(
        'tr:has(> td:has(> a[class="ent-name"]))')]
    abilities = [parse_ability(i) for i in ability_html]
    return abilities


def add_to_database(client: MongoClient = None) -> None:
    if client is None:
        client = MongoClient()

    abilities = scrape_abilities()
    client.get_database('test_database', codec_options=CODEC_OPTIONS).abilities.insert_many(
        [i.asdict() for i in abilities])
