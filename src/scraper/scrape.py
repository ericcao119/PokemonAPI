import multiprocessing
import traceback
from pprint import pprint

from loguru import logger

from src.data.typing import SpeciesId, VariantId
from src.gather_files import request_pokeurl_pokemondb
from src.scraper.ability import scrape_abilities
from src.scraper.pmove import scrape_moves
from src.scraper.pokedex import scrape_pokedex
from src.scraper.pokemon import create_species
from src.utils.general import create_multimap, unique


def _create_species_wrapper(args):
    return create_species(*args)


def generate_all_pokemon():
    """Completey scrape all supported information and compose them together"""
    species, variants, typing, stats, urls = scrape_pokedex()

    try:
        with multiprocessing.Pool(4) as pool:
            entries = pool.map(
                _create_species_wrapper,
                zip(species, variants, typing, stats, urls),
                chunksize=60,
            )

        return create_multimap(species, entries)

    except Exception as e:
        logger.error(e)
        raise e
