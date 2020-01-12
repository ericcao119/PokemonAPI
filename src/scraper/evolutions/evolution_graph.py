"""Constructs the evolution graph"""

import functools
from collections import deque
from dataclasses import dataclass
from pprint import pprint
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

import bs4
import networkx as nx
from bs4.element import Tag
from loguru import logger

from config import EVOLUTION_GRAPH
from src.scraper.evolutions.tokenizer import (
    ComboToken,
    EvoChainToken,
    PokeToken,
    SplitToken,
    tokenize,
)
from src.utils.general import get_components, grouper_discard_uneven, unique
from src.utils.poke_helpers import add_missing_variants

SPECIES = str
VARIANTS = str

def extract_vertices(token: EvoChainToken) -> Set[Tuple[SPECIES, VARIANTS]]:
    """Extracts vertices from the chain. Currently, pokemon that are combined
    as the result of an evolution are stored separately, but this may need to
    be changed in the future."""
    pokes: Set[Tuple[SPECIES, VARIANTS]] = set()

    for i in token.chain:
        if isinstance(i, EvoChainToken):
            child_poke = extract_vertices(token)
            pokes |= child_poke
            continue

        if isinstance(i, SplitToken):
            child_pokes = [extract_vertices(i) for i in i.children]
            # Combine
            pokes |= functools.reduce(lambda a, b: a | b, child_pokes)
            continue

        poke_option = i.pokemon
        poke_set = set(poke_option) if poke_option else set()
        pokes |= set(poke_set)

    # Clean up
    return pokes


def extract_edges(
    token: EvoChainToken, prev_pokes: List[Tuple[SPECIES, VARIANTS]] = []
):
    """Extracts edges from the chain token, but be warned that there
    is currently no protection from stack overflow. However, the scraped
    information gets stored in a tree structure, so cycles will not cause
    stack overflows."""
    edge_list: List[
        Tuple[List[Tuple[SPECIES, VARIANTS]], List[Tuple[SPECIES, VARIANTS]], Any]
    ] = []
    chain = list(token.chain)

    if len(chain) < 2:
        return edge_list

    if len(prev_pokes) == 0:
        if chain[0].pokemon is None:
            raise ValueError("This first element must be a pokemon")

        prev_pokes = chain[0].pokemon
        chain = chain[1:]

    # Add all edges in chain
    for evo_token, poke_token in grouper_discard_uneven(chain, 2):
        if poke_token.pokemon is None or evo_token.evolution_method is None:
            raise ValueError("Chain is not a valid chain")

        if isinstance(poke_token, PokeToken):
            edge_list.append(
                (prev_pokes, poke_token.pokemon, evo_token.evolution_method)
            )

        if isinstance(poke_token, ComboToken):
            for i in poke_token.pokemon:
                edge_list.append((prev_pokes, [i], evo_token.evolution_method))

        prev_pokes = poke_token.pokemon

    # Handle case where end is a SplitToken
    if isinstance(chain[-1], SplitToken):
        for i in chain[-1].children:
            edge_list.extend(extract_edges(i, prev_pokes))

    return edge_list


def create_graph(chain: EvoChainToken) -> List[nx.MultiDiGraph]:
    """Creates graph from evo-chain"""
    # get vertices (all variants in chain in addition to the)
    # get edge list
    vertices = extract_vertices(chain)
    edges = extract_edges(chain)

    evo_graph = nx.MultiDiGraph()
    evo_graph.add_nodes_from(vertices)

    for prev, curr, evo in edges:
        evo_graph.add_edge(prev[0], curr[0], method=evo)
    return evo_graph


def scrape_connections(
    variants_list: List[Tuple[SPECIES, VARIANTS]],
    geneology: Dict[SPECIES, List[VARIANTS]],
):
    """Scrapes connections from pokemondb's evolution webpage and
    converts them into graphs to be used by networkx. To support
    arbitrary directed multi-graphs, this scraper assumes that each
    'evolution chain' can be cyclic (no evolution has this structure
    as of SwSh). However each chain has an exit point (last pokemon in
    the chain) that can be used to connect further chains."""
    html = bs4.BeautifulSoup(EVOLUTION_GRAPH.read_text(), "lxml")

    chain_selector = "hr ~ div.infocard-list-evo"
    chains = html.select(chain_selector)

    # Note: Due to how this is formatted
    evo_chains = [tokenize(i) for i in chains]

    # Create graph from each chain
    raw_chains = [create_graph(i) for i in evo_chains]

    complete = nx.MultiDiGraph()
    complete.add_nodes_from(variants_list)
    complete = nx.compose(complete, nx.compose_all(raw_chains))

    # Get merged chains
    comps = nx.connected_components(complete.to_undirected())

    # Add implicit edges to group related, but disjoint chains
    new_comps = [add_missing_variants(comp, geneology) for comp in comps]

    # Get vertices of the grouped chains
    grouped_verts = list(get_components(new_comps))

    return [nx.subgraph(complete, comp) for comp in grouped_verts]


# Test Cases:
# print(tokenize_list(chains[65].find_all(recursive=False)))
# print(tokenize_list(chains[68].find_all(recursive=False)))
# print(tokenize_list(chains[119].find_all(recursive=False)))
# print(tokenize_list(chains[128].find_all(recursive=False)))
# Edge cases:
# Eevee
# Galarian Mr. Mime -
# Wurmple -
# Shedinja -
