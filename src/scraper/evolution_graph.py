"""Constructs the evolution graph"""

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

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


# class Edge:
#     def __init__(self, html_frag):
#         self.children = []
#         self._html_frag = html_frag


# class Node:
#     def __init__(self, html_frag):
#         self.type = _representative_class(html_frag["class"])
#         self.species = html_frag.select_one("a.ent-name").string
#         variant_html = html_frag.select_one("br + small:not(:has(a))")
#         self.variant = variant_html.string if variant_html else species
#         self.edges = []
#         self._html_frag = html_frag


def poke_from_infocard(html_frag: Tag) -> Tuple[str, str]:
    """Given that the tag is an div.infocard, this extracts the pokemon from the Tag"""
    if not (html_frag.has_attr("class") and {"infocard"} == set(html_frag["class"])):
        raise ValueError("Tag is not of the form div.infocard")

    species_html = html_frag.select_one("a.ent-name")
    variant_html = html_frag.select_one("br + small:not(:has(a))")

    species = species_html.string
    variant = species

    if variant_html:
        variant = variant_html.string

    return species, variant


@dataclass
class SplitToken:
    """Creates a special split token to represent a split in the evolutionary
    chain. This has to be created to signify the difference between a regular
    chain and a split."""

    children: deque
    html_frag: Tag

    @property
    def token_type(self):
        """Returns the 'token' type"""
        return "Split"

    def __repr__(self) -> str:
        """Gives a more compact representation that is much nicer for printing.
        TODO: Later move this into a different function"""
        return repr((self.token_type[0], self.children))


@dataclass
class EvoToken:
    """Represents a variety of tokens extracted from the document.
    TODO: Split it into many different token classes"""

    token_type: str
    html_frag: List[Tag]

    def __repr__(self) -> str:
        """Gives a more compact representation that is much nicer for printing.
        TODO: Later move this into a different function"""
        if self.token_type == "Variant" or self.token_type == "Combo":
            variants_option = self.pokemon
            variants_name = (
                [i[1] for i in variants_option] if variants_option is not None else None
            )
            return repr((self.token_type[0], variants_name))

        if self.token_type == "Evolution":
            evo_option = self.evolution_method
            return repr((self.token_type[0], evo_option))

        return self.token_type

    @property
    def pokemon(self) -> Optional[List[Tuple[str, str]]]:
        """Extracts the pokemon if the token contains a pokemon"""
        if self.token_type == "Variant":
            return [poke_from_infocard(self.html_frag[0])]

        if self.token_type == "Combo":
            return [
                poke_from_infocard(self.html_frag[0]),
                poke_from_infocard(self.html_frag[2]),
            ]

        return None

    @property
    def evolution_method(self) -> Optional[str]:
        """Extracts the evolution method if the token represents an evolution chain"""
        if self.token_type == "Evolution":
            method = self.html_frag[0].select_one("small").text
            return method

        return None


# def construct_tree(node_list: List):
#     """
#      Possible children
#      - infocard-list-evo (evolution subtree)
#      - infocard-evo-split (Fork in chain)
#      - infocard (Pokemon)
#      - i.icon-arrow.icon-arrow-e (Evolution)
#      - i.icon-arrow:contains("+") (Two or more pokemon generated)
#     """


# def parse_tree_helper(tree_list: List):
#     """Currently not used"""
#     raise NotImplementedError()


def _is_infocard(html_frag: Tag):
    """Determines if a Tag is an infocard and just an infocard"""
    return html_frag.has_attr("class") and {"infocard"} == set(html_frag["class"])


def _is_evo_connect(html_frag: Tag):
    """Determines if a Tag represents an evolution"""
    return html_frag.has_attr("class") and "infocard-arrow" in html_frag["class"]


def _is_infocard_list(html_frag: Tag):
    """Determines if a Tag represents a evolution chain."""
    return (
        html_frag.has_attr("class")
        and "infocard-list-evo" in html_frag["class"]
        and html_frag.name == "div"
    )


def _is_evo_split(html_frag: Tag):
    """Determines if a Tag represents an evolutionary split"""
    return html_frag.has_attr("class") and "infocard-evo-split" in html_frag["class"]


def _matches_combo(html_list: List) -> bool:
    """Determines if the first three elements form a 'combo'
    where multiple pokemon are grouped together like Shedinja and Ninjask"""
    if len(html_list) < 3:
        return False

    card1, operation, card2, *_ = html_list

    # if operation.select_one('i.icon-arrow')
    op_valid = operation.name == "span" and (
        operation.select_one("i.icon-arrow").string == "+"
    )
    card1_valid = _is_infocard(card1)
    card2_valid = _is_infocard(card2)

    return op_valid and card1_valid and card2_valid


def tokenize_list(html_list: List) -> deque:
    """
    Convert this to a fully fledge functional style with pythonic switch-case
    and split everything off into its own function.

     Possible children
     - i.icon-arrow:contains("+") (Two or more pokemon generated) -
     - infocard (Pokemon) -
     - i.icon-arrow.icon-arrow (Evolution) -
     - infocard-evo-split (Fork in chain)
     - infocard-list-evo (evolution subtree) -
    """

    if len(html_list) == 0:
        return deque()

    if _matches_combo(html_list):
        head = EvoToken("Combo", html_list[0:3])
        tail = tokenize_list(html_list[3:])
        tail.appendleft(head)
        return tail

    if _is_infocard(html_list[0]):
        head = EvoToken("Variant", [html_list[0]])
        tail = tokenize_list(html_list[1:])
        tail.appendleft(head)
        return tail

    if _is_evo_connect(html_list[0]):
        head = EvoToken("Evolution", [html_list[0]])
        tail = tokenize_list(html_list[1:])
        tail.appendleft(head)
        return tail

    if _is_infocard_list(html_list[0]):
        head_r = tokenize_list(html_list[0].find_all(recursive=False))
        tail = tokenize_list(html_list[1:])
        tail.appendleft(head_r)
        return tail
        # recurse into to create list and append list

    # print(html_list[0])
    if _is_evo_split(html_list[0]):
        # handle double recursion here
        children = html_list[0].find_all(recursive=False)

        first_level = [i for i in children if i.name == "span"]

        if len(children) != len(first_level):
            raise NotImplementedError()

        second_level = [i.find_all(recursive=False) for i in first_level]

        for i in second_level:
            if len(i) > 1:
                raise NotImplementedError()

            if not _is_infocard_list(i[0]):
                raise NotImplementedError()

        head_d = [
            tokenize_list(child[0].find_all(recursive=False)) for child in second_level
        ]

        head_token = SplitToken(deque(head_d), html_list[0])

        tail = tokenize_list(html_list[1:])
        tail.appendleft(head_token)
        return tail

    raise NotImplementedError()


def scrape_connections(species_list: Dict[SPECIES, VARIANTS]):
    """Scrapes connections from pokemondb's evolution webpage and
    converts them into graphs to be used by networkx."""
    html = bs4.BeautifulSoup(EVOLUTION_GRAPH.read_text(), "lxml")

    chain_selector = "hr ~ div.infocard-list-evo"
    chains = html.select(chain_selector)

    # print(f"Num chains: {len(chains)}")

    # print(tokenize_list(chains[65].find_all(recursive=False)))
    # print(tokenize_list(chains[68].find_all(recursive=False)))
    # print(tokenize_list(chains[119].find_all(recursive=False)))
    # print(tokenize_list(chains[128].find_all(recursive=False)))

    print([tokenize_list(i.find_all(recursive=False)) for i in chains])


# Edge cases:
# Eevee
# Galarian Mr. Mime -
# Wurmple -
# Shedinja -
