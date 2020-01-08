"""Constructs the evolution graph"""

from typing import List, Dict

import bs4
import networkx as nx
from bs4.element import Tag

from config import EVOLUTION_GRAPH

# TotalEV_Graph = nx.DiGraph()
# TotalEV_Graph.add_nodes_from(
#     {}
# )

SPECIES = str
VARIANTS = str

# def extract_vertices()

# Algebraic Datatype
# Node =
#  | Evo
#  | (Arrow Evo) Node
#  | SplitList([Arrow Evo]) Node


def _representative_class(class_list):
    return max(class_list, key=lambda x: len(x))


class Edge:
    def __init__(self, html_frag):
        self.children = []
        self._html_frag = html_frag


class Node:
    def __init__(self, html_frag):
        self.type = _representative_class(html_frag["class"])
        self.species = html_frag.select_one("a.ent-name").string
        variant_html = html_frag.select_one("br + small:not(:has(a))")
        self.variant = variant_html.string if variant_html else species
        self.edges = []
        self._html_frag = html_frag


def construct_tree(node_list: List):

    """
     Possible children
     - infocard-list-evo (evolution subtree)
     - infocard-evo-split (Fork in chain)
     - infocard (Pokemon)
     - i.icon-arrow.icon-arrow-e (Evolution)
     - i.icon-arrow:contains("+") (Two or more pokemon generated) 
    """
    pass


def parse_tree_helper(tree_list: List):

    # Functions of the form
    parsing_table = {
        # "infocard": parse_info_only,
        "infocard-evo-split": lambda x: x,
        "infocard-arrow": lambda x: x,
    }

    root = tree_list[0]
    root_type = _representative_class(tree_list[0]["class"])
    # print(tree_list)
    return parsing_table[root_type](root)


def _is_infocard(html_frag):
    """Determines if a Tag is an infocard and just an infocard"""
    return {"infocard"} == set(html_frag["class"])


def _matches_combo(html_list: List) -> bool:
    """Determines if the first three elements form a 'combo'
    where multiple pokemon are grouped together like Shedinja and Ninjask"""
    if len(html_list) < 3:
        return False

    card1, operation, card2, *rem_list = html_list

    # if operation.select_one('i.icon-arrow')
    op_valid = {"span"} == set(operation["class"]) and (
        operation.select_one("i.icon-arrow").string == "+"
    )
    card1_valid = _is_infocard(card1)
    card2_valid = _is_infocard(card2)

    return op_valid and card1_valid and card2_valid


def tokenize_list(html_list: List):
    """
     Possible children
     - i.icon-arrow:contains("+") (Two or more pokemon generated) -
     - infocard (Pokemon)
     - i.icon-arrow.icon-arrow-e (Evolution)
     - infocard-evo-split (Fork in chain)
     - infocard-list-evo (evolution subtree)
    """
    print([i["class"] for i in html_list])
    print([i.text for i in html_list])

    if _matches_combo(html_list):
        pass

    if _is_infocard(html_list[0]):
        pass


def scrape_connections(species_list: Dict[SPECIES, VARIANTS]):
    html = bs4.BeautifulSoup(EVOLUTION_GRAPH.read_text(), "lxml")

    # parse_tree_helper(
    #     [i for i in html.select("div.infocard-list-evo")[86].find_all(recursive=False)]
    # )

    chain_selector = "hr ~ div.infocard-list-evo"

    print(f"Num chains: {len(html.select(chain_selector))}")
    tokenize_list(html.select(chain_selector)[65].find_all(recursive=False))
    tokenize_list(html.select(chain_selector)[119].find_all(recursive=False))
    tokenize_list(html.select(chain_selector)[128].find_all(recursive=False))
    # tree = construct_tree([i for i in html.select("div.infocard-list-evo")[80].find_all(recursive=False)])

    for i in (
        html.select(chain_selector)[128]
        .find_all(recursive=False)[1]
        .select("div.infocard-list-evo")[1]
        .find_all(recursive=False)
    ):
        print(i)
        print()

    print()
    # s, v = parse_tree_helper(
    #     None
    # )


# Edge cases:
# Eevee
# Galarian Mr. Mime -
# Wurmple -
# Shedinja -
