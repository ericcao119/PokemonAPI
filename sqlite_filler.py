import json
import sqlite3
from pprint import pprint

from loguru import logger
from networkx.readwrite.json_graph import adjacency_data, tree_data

from src.data.species import *
from src.gather_files import populate_cache
from src.scraper.ability import scrape_abilities
from src.scraper.evolutions.evolution_graph import scrape_evolution_trees
from src.scraper.pmove import *
from src.scraper.scrape import create_species, generate_all_pokemon, scrape_pokedex


def fill_ability_sql(conn: sqlite3.Connection):
    logger.info("Starting to scrape abilities")
    abilities = scrape_abilities()

    for idx, ability in enumerate(abilities):
        try:
            ability.write_to_sql(conn.cursor())
        except Exception as e:
            logger.error(f"Failed to write the ability: {ability.ability_name}")

    conn.commit()


def fill_moves_sql(conn: sqlite3.Connection):
    logger.info("Starting to scrape moves")
    moves = scrape_moves()

    for idx, move in enumerate(moves):
        try:
            move.write_to_sql(conn.cursor())
        except Exception as e:
            logger.error(f"Failed to write the ability: {move.name}")
    conn.commit()


def fill_pokemon_sql(conn: sqlite3.Connection):
    logger.info("Starting to scrape pokemon")
    species, variants, typing, stats, urls = scrape_pokedex()

    for idx, i in enumerate(zip(species, variants, typing, stats, urls)):
        poke = create_species(*i)
        try:
            poke.write_to_sql(conn.cursor())
        except Exception as e:
            logger.error(f"Failed to write pokemon: {poke.variant_name}")

    conn.commit()


def write_evolution_trees():
    logger.info("Starting to scrape evolution chains")
    species, variants, typing, stats, urls = scrape_pokedex()
    graphs = scrape_evolution_trees(list(zip(species, variants)))
    trees = []
    for tree in graphs:
        sources = [n for n, d in tree.in_degree() if d == 0]
        trees.append(tree_data(tree, sources[0]))

    with open("evolutions.json", "w") as f:
        f.write(str.encode(json.dumps(trees)).decode("unicode-escape"))


if __name__ == "__main__":
    conn = sqlite3.connect("./pokemon.db")

    with open("sql/pokemon_tables.sql", "r") as f:
        conn.cursor().executescript(f.read())

    fill_ability_sql(conn)
    fill_moves_sql(conn)
    fill_pokemon_sql(conn)
    write_evolution_trees()
