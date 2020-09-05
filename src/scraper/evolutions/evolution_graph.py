"""Constructs the evolution graph"""

from functools import singledispatch
from typing import Any, Dict, List, Optional, Set, Tuple

import bs4
import networkx as nx

from src.config import EVOLUTION_GRAPH
from src.data.typing import PokeId, SpeciesId, VariantId
from src.scraper.evolutions.tokenizer import (
    ComboToken,
    EvoChainToken,
    EvoToken,
    PokeToken,
    SplitToken,
    tokenize,
)
from src.utils.general import create_multimap, get_components, grouper_discard
from src.utils.poke_helpers import add_missing_variants


@singledispatch
def extract_vertices(token: EvoChainToken) -> Set[PokeId]:
    """Extracts vertices from the chain. Currently, pokemon that are combined
    as the result of an evolution are stored separately, but this may need to
    be changed in the future."""
    pokes: Set[PokeId] = set()

    for token in token.chain:
        pokes |= set(extract_vertices(token))

    return pokes


@extract_vertices.register
def extract_from_split(token: SplitToken) -> Set[PokeId]:
    """Extracts vertices from the chain. Currently, pokemon that are combined
    as the result of an evolution are stored separately, but this may need to
    be changed in the future."""
    pokes: Set[PokeId] = set()
    child_pokes = [extract_vertices(branch) for branch in token.children]
    pokes = pokes.union(*child_pokes)
    return pokes


@extract_vertices.register(EvoToken)
@extract_vertices.register(PokeToken)
@extract_vertices.register(ComboToken)
def extract_from_base(token: PokeToken) -> Set[PokeId]:
    """Extracts vertices from the chain. Currently, pokemon that are combined
    as the result of an evolution are stored separately, but this may need to
    be changed in the future."""
    pokes: Set[PokeId] = set()
    poke_option = token.pokemon
    pokes = set(poke_option) if poke_option else set()
    return pokes


def extract_edges(token: EvoChainToken, prev_pokes: Optional[List[PokeId]] = None):
    """Extracts edges from the chain token, but be warned that there
    is currently no protection from stack overflow. However, the scraped
    information gets stored in a tree structure, so cycles will not cause
    stack overflows."""
    # TODO: Refactor this method
    if prev_pokes is None:
        prev_pokes = []

    edge_list: List[Tuple[List[PokeId], List[PokeId], Any]] = []
    chain = list(token.chain)

    if len(chain) < 2:
        return edge_list

    if len(prev_pokes) == 0:
        if chain[0].pokemon is None:
            raise ValueError("This first element must be a pokemon")

        prev_pokes = chain[0].pokemon
        chain = chain[1:]

    # Add all edges in chain
    for evo_token, poke_token in grouper_discard(chain, 2):
        if poke_token.pokemon is None or evo_token.evolution_method is None:
            raise ValueError("Chain is not a valid chain")

        if isinstance(poke_token, PokeToken):
            edge_list.append(
                (prev_pokes, poke_token.pokemon, evo_token.evolution_method)  # type: ignore
            )

        if isinstance(poke_token, ComboToken):
            for i in poke_token.pokemon:
                edge_list.append((prev_pokes, [i], evo_token.evolution_method))  # type: ignore

        prev_pokes = poke_token.pokemon

    # Handle case where end is a SplitToken
    if isinstance(chain[-1], SplitToken):
        for i in chain[-1].children:
            edge_list.extend(extract_edges(i, prev_pokes))

    return edge_list


def create_graph_from_chain(chain: EvoChainToken) -> nx.MultiDiGraph:
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
    variants_list: List[PokeId],
    with_missing_variants: bool = False,
) -> List[nx.MultiDiGraph]:
    """Scrapes connections from pokemondb's evolution webpage and
    converts them into graphs to be used by networkx. To support
    arbitrary directed multi-graphs, this scraper assumes that each
    'evolution chain' can be cyclic (no evolution has this structure
    as of SwSh). However each chain has an exit point (last pokemon in
    the chain) that can be used to connect further chains.

    ## Params

    - variants_list: A list of (species, variant) pairs used to uniquely identify pokemon
    - with_missing_variants: Includes variants that are not in any evolutionary chain into
        the graph. A good example is Mega Venusaur, which is not an evolution of Ivysaur, but
        would now be included in the graph.
    - treeify: A post processing argument to convert the return evolutionary chains into a tree.
        Note that this assumes that the input graphs are all (directed with parallel edges) trees,
        which may not be true in the future.
    """
    species, variants = zip(*variants_list)
    geneology = create_multimap(species, variants)

    # Get evolutionary chains
    html = bs4.BeautifulSoup(EVOLUTION_GRAPH.read_text(), "lxml")
    chain_selector = "hr ~ div.infocard-list-evo"
    chains = html.select(chain_selector)

    # Create a graph from each chain. Due to how this is formatted, pokemon like Eevee
    # will appear in many chains, so these will later have to be unioned.
    evo_chains = [tokenize(i) for i in chains]
    raw_chains = [create_graph_from_chain(i) for i in evo_chains]

    # Union graphs together (should be a forest)
    complete = nx.MultiDiGraph()
    complete.add_nodes_from(variants_list)  # This enforces an ordering on the nodes
    complete = nx.compose(complete, nx.compose_all(raw_chains))  # Union all graphs

    if not with_missing_variants:
        complete.remove_nodes_from(list(nx.isolates(complete)))

    # Isolate the nodes into their trees
    comps = nx.connected_components(complete.to_undirected())

    if with_missing_variants:
        # Add implicit edges to group related, but disjoint chains
        comps = [add_missing_variants(comp, geneology) for comp in comps]

    # Get vertices of the grouped chains
    grouped_verts = list(get_components(comps))

    subgraphs = [nx.subgraph(complete, comp) for comp in grouped_verts]

    return subgraphs


def treeify(g: nx.MultiDiGraph) -> nx.DiGraph:
    """Converts MultiDigraph (that is already a tree!) into a Tree Digraph.
    This function does not check for the tree like structure. For compatability
    with tree_data, we push the data to the nodes."""
    tree = nx.DiGraph()

    for u, v, data in g.edges.data("method"):
        if not tree.has_edge(u, v):
            tree.add_edge(u, v)
            tree.nodes[v]["methods"] = []
        tree.nodes[v]["methods"].append(data)

    return tree


def scrape_evolution_trees(variants_list: List[PokeId]) -> List[nx.DiGraph]:
    subgraphs = scrape_connections(variants_list, with_missing_variants=False)
    return [treeify(g) for g in subgraphs]


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
