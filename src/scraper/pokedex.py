# from functools import lru_cache

import bs4

from config import Pokedex
from src.data.poke_enums import PType
from src.data.stats import BaseStats


def parse_dex_entry(html):
    '''Parses a single dex entry from the pokemon database'''

    # print(html)

    species_name = html.select_one('a.ent-name').string
    variant_name = html.select_one(
        'small').string if html.select_one('small') else species_name

    print(species_name, variant_name)
    typing = [PType[t.string] for t in html.select('td.cell-icon>a')]
    print(typing)

    # This has to explicitly select one class to avoid selecting other html elements

    stat_names = ['HP', 'Attack', 'Defense',
                  'Special_Attack', 'Special_Defense', 'Speed']
    stats = [int(stat.string) for stat in html.select('td[class="cell-num"]')]
    stats = BaseStats(**dict(zip(stat_names, stats)))

    return


def scrape_pokedex():
    """Scrapes the pokedex for variants, typing, and base stats

    :returns: TODO

    """

    html = bs4.BeautifulSoup(Pokedex.read_text(), 'html.parser')
    variants_html = [item for item in html.select('#pokedex > tbody > tr')]
    parse_dex_entry(variants_html[2])
    parse_dex_entry(variants_html[3])
    parse_dex_entry(variants_html[4])
    parse_dex_entry(variants_html[7])
