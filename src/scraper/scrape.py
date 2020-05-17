import multiprocessing
import traceback
from pprint import pprint

from loguru import logger

from src.data.typing import SpeciesId, VariantId
from src.gather_files import request_pokeurl_pokemondb
from src.scraper.abilities_list import scrape_abilities
from src.scraper.pmove import scrape_moves
from src.scraper.pokedex import scrape_pokedex
from src.scraper.pokemon import create_species
from src.utils.general import create_multimap, unique


def _create_species_wrapper(args):
    return create_species(*args)


def generate_all_pokemon():
    """Completey scrape all supported information and compose them together"""
    species, variants, typing, stats = scrape_pokedex()
    geneology = create_multimap(species, variants)
    stat_mapping = create_multimap(species, stats)

    _ = [request_pokeurl_pokemondb(spe) for spe in unique(species)]

    try:
        pool = multiprocessing.Pool(4)
        entries = pool.map(
            _create_species_wrapper, zip(species, variants, typing, stats), chunksize=60
        )
        # entries = [_create_species_wrapper(i) for i in list(zip(species, variants, stats))[:4]]
        # print(species)
        # pprint(species)
        return create_multimap(species, entries)
        # pprint(create_multimap(species, entries), indent=1, sort_dicts=False, width=120)

    except Exception as e:
        logger.error(e)
        raise


def generate_abilities():
    abilities = scrape_abilities()
    return {ability.name: ability for ability in abilities}
