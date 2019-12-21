
import bs4

from bs4 import BeautifulSoup
from config import NationalDex
from collections import namedtuple

from src.data.ptype import PType


"""TODO Add information about forms since some pokemon like Raticate are missing regional dex numbers,
but are still listed due to different typing"""


DexEntry = namedtuple(
    'DexEntry', ['variant', 'ndex', 'image_url', 'name', 'type1', 'type2'])


def parse_list():
    # assert(type(NationalDex) == Path)
    with NationalDex.open('r') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    regional_dexes = soup.find_all('table', attrs={'align': 'center'})

    lines = [tag('tr') for tag in regional_dexes]

    pokemon = {}
    for i in range(len(regional_dexes)):
        for j in range(1, len(lines[i])):
            entry = pokemon_from_line(lines[i][j])

            if entry.name not in pokemon:
                pokemon[entry.name] = entry
    print(list(pokemon.values()))


def pokemon_from_line(tr: bs4.Tag) -> DexEntry:
    RDEX_IDX = 0
    KDEX_IDX = 1
    IMG_URL_IDX = 2
    POKEMON_IDX = 3
    TYPE_1 = 4
    TYPE_2 = 5

    entry = tr('td')

    poke = DexEntry(
        variant='',
        ndex=int(str(entry[KDEX_IDX].string).strip()[1:]),
        image_url=entry[IMG_URL_IDX].find('a').find('img').attrs['src'],
        name=entry[POKEMON_IDX].find('a').string,
        type1=PType[entry[TYPE_1].find('a').find('span').string],
        type2=(PType[entry[TYPE_2].find('a').find('span').string]
               if len(entry) > TYPE_2 else PType.INVALID)
    )

    return poke
