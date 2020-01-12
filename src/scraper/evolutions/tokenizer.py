"""Constructs the evolution graph"""

import functools
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional, Tuple

from bs4.element import Tag
from loguru import logger


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


class BaseToken:
    """Base token class"""

    @property
    def token_type(self):
        return "Base"

    @property
    def pokemon(self) -> Optional[List[Tuple[str, str]]]:
        """Extracts the pokemon contained in the token"""
        return None

    @property
    def evolution_method(self) -> Optional[str]:
        """Extracts the evolution method string descriptor"""
        return None

    def __str__(self) -> str:
        return self.token_type


@dataclass
class EvoChainToken(BaseToken):
    chain: Deque
    html_frag: Tag

    @property
    def token_type(self):
        return "Chain"

    def __str__(self):
        return str((self.token_type, self.chain))

    def __repr__(self) -> str:
        return str(self)


@dataclass
class SplitToken(BaseToken):
    """Creates a special split token to represent a split in the evolutionary
    chain. This has to be created to signify the difference between a regular
    chain and a split."""

    children: Deque[EvoChainToken]
    html_frag: Tag

    @property
    def token_type(self):
        return "Split"

    def __str__(self) -> str:
        return str((self.token_type, self.children))

    def __repr__(self) -> str:
        return str(self)


@dataclass
class PokeToken(BaseToken):
    """Represents a single pokemon extracted from the html."""

    html_frag: Tag

    def __post_init__(self):
        self._pokemon = [poke_from_infocard(self.html_frag)]

    @property
    def token_type(self):
        return "Variant"

    @property
    def pokemon(self) -> Optional[List[Tuple[str, str]]]:
        return self._pokemon

    def __str__(self) -> str:
        variants_option = self.pokemon
        variants_name = (
            [i[1] for i in variants_option] if variants_option is not None else None
        )
        return str((self.token_type, variants_name))

    def __repr__(self) -> str:
        return str(self)


@dataclass
class ComboToken(BaseToken):
    """Represents a variety of tokens extracted from the document."""

    html_frag: List[Tag]

    def __post_init__(self):
        self._pokemon = [
            poke_from_infocard(self.html_frag[0]),
            poke_from_infocard(self.html_frag[2]),
        ]

    @property
    def token_type(self):
        return "Combo"

    @property
    def pokemon(self) -> Optional[List[Tuple[str, str]]]:
        return self._pokemon

    def __str__(self) -> str:
        variants_option = self.pokemon
        variants_name = (
            [i[1] for i in variants_option] if variants_option is not None else None
        )
        return str((self.token_type, variants_name))

    def __repr__(self) -> str:
        return str(self)


@dataclass
class EvoToken(BaseToken):
    """Represents a variety of tokens extracted from the document.
    TODO: Split it into many different token classes"""

    html_frag: Tag

    def __post_init__(self):
        self._evolution = self.html_frag.select_one("small").text

    @property
    def token_type(self):
        return "Evolution"

    @property
    def evolution_method(self) -> Optional[str]:
        return self._evolution

    def __str__(self) -> str:
        """Gives a more compact representation that is much nicer for printing.
        TODO: Later move this into a different function"""
        evo_option = self.evolution_method
        return str((self.token_type, evo_option))

    def __repr__(self) -> str:
        return str(self)


class Lexeme(ABC):
    @classmethod
    @abstractmethod
    def matches(cls, html_list: List[Tag]) -> bool:
        """Determines if the first tags match the lexeme"""

    @classmethod
    @abstractmethod
    def create_token(cls, html_list: List[Tag]) -> BaseToken:
        """Create a token from the lexeme"""

    @classmethod
    @abstractmethod
    def consume_lexeme(cls, html_list: List[Tag]) -> List[Tag]:
        """Returns a slice of the html_list without the lexeme.
        This assumes that the lexeme begins at the 0th index and is present"""


class ComboLex(Lexeme):
    """Lexeme to represent a combo of pokemon. This is currently only used
    the Nincada family."""

    @classmethod
    def matches(cls, html_list: List[Tag]) -> bool:
        """Determines if the first three elements form a 'combo'
        where multiple pokemon are grouped together like Shedinja and Ninjask"""
        if len(html_list) < 3:
            return False

        card1, operation, card2, *_ = html_list
        op_valid = operation.name == "span" and (
            operation.select_one("i.icon-arrow").string == "+"
        )
        card1_valid = InfocardLex.matches([card1])
        card2_valid = InfocardLex.matches([card2])

        return op_valid and card1_valid and card2_valid

    @classmethod
    def create_token(cls, html_list: List[Tag]) -> BaseToken:
        """Create a token from the lexeme"""
        return ComboToken(html_list[0:3])

    @classmethod
    def consume_lexeme(cls, html_list: List[Tag]) -> List[Tag]:
        """Returns a slice of the html_list without the lexeme.
        This assumes that the lexeme begins at the 0th index and is present"""
        return html_list[3:]


class InfocardLex(Lexeme):
    """Lexeme representing a infocard element. Note that infocard must be
    the only class of the tag"""

    @classmethod
    def matches(cls, html_list: List[Tag]) -> bool:
        html_frag = html_list[0]
        return html_frag.has_attr("class") and {"infocard"} == set(html_frag["class"])

    @classmethod
    def create_token(cls, html_list: List[Tag]) -> BaseToken:
        return PokeToken(html_list[0])

    @classmethod
    def consume_lexeme(cls, html_list: List[Tag]) -> List[Tag]:
        return html_list[1:]


class ArrowLex(Lexeme):
    """Lexeme representing a infocard-arrow element."""

    @classmethod
    def matches(cls, html_list: List[Tag]) -> bool:
        html_frag = html_list[0]
        return html_frag.has_attr("class") and "infocard-arrow" in html_frag["class"]

    @classmethod
    def create_token(cls, html_list: List[Tag]) -> BaseToken:
        return EvoToken(html_list[0])

    @classmethod
    def consume_lexeme(cls, html_list: List[Tag]) -> List[Tag]:
        return html_list[1:]


class InfocardListLex(Lexeme):
    """Lexeme representing a infocard-list element."""

    @classmethod
    def matches(cls, html_list: List[Tag]) -> bool:
        html_frag = html_list[0]
        return (
            html_frag.has_attr("class")
            and "infocard-list-evo" in html_frag["class"]
            and html_frag.name == "div"
        )

    @classmethod
    def create_token(cls, html_list: List[Tag]) -> BaseToken:
        return EvoChainToken(
            html_list[0], tokenize_list(html_list[0].find_all(recursive=False))
        )

    @classmethod
    def consume_lexeme(cls, html_list: List[Tag]) -> List[Tag]:
        return html_list[1:]


class EvoSplitLex(Lexeme):
    """Lexeme representing a infocard-list element."""

    @classmethod
    def matches(cls, html_list: List[Tag]) -> bool:
        html_frag = html_list[0]
        return (
            html_frag.has_attr("class") and "infocard-evo-split" in html_frag["class"]
        )

    @classmethod
    def create_token(cls, html_list: List[Tag]) -> BaseToken:
        def simplify(html_list: List[Tag]):
            """Sanity check that everything has one child and every child is a chain"""
            if len(html_list) > 1 or not InfocardListLex.matches([html_list[0]]):
                raise NotImplementedError()
            return html_list[0]

        children = html_list[0].find_all(recursive=False)

        first_level = [i for i in children if i.name == "span"]

        if len(children) != len(first_level):
            # Sanity check that every child is a span
            raise NotImplementedError()

        second_level = [simplify(i.find_all(recursive=False)) for i in first_level]

        head_d = [
            EvoChainToken(tokenize_list(child.find_all(recursive=False)), child)
            for child in second_level
        ]

        return SplitToken(deque(head_d), html_list[0])

    @classmethod
    def consume_lexeme(cls, html_list: List[Tag]) -> List[Tag]:
        return html_list[1:]


LEXABLE_HTML_ELEMENTS = [
    ComboLex,
    InfocardLex,
    ArrowLex,
    InfocardListLex,
    EvoSplitLex,
]  # Note: Order matters for lexing reasons


VALID_TOKENS = [
    ComboToken,
    PokeToken,
    EvoToken,
    SplitToken,
]


def subchain_present(evo_token: EvoChainToken) -> bool:
    return functools.reduce(
        lambda accum, elem: accum | isinstance(elem, EvoChainToken),
        evo_token.chain,
        False,
    )


def split_valid(evo_token: EvoChainToken) -> bool:
    """Does a simple validation of the split"""
    splits = [i for i in evo_token.chain if isinstance(i, SplitToken)]

    if len(splits) == 0:
        return True

    if len(splits) > 1:
        logger.error(f"Multiple splits found in token chain: {evo_token}")
        return False

    # Only one split
    split = splits[0]

    if not isinstance(evo_token.chain[-1], SplitToken):
        logger.error(
            f"Unsupported feature: A split exists before the last token in the chain: {evo_token}"
        )
        return False

    # Verify all children of Split are valid
    split = splits[0]

    all_chains = all(isinstance(i, EvoChainToken) for i in split.children)
    if not all_chains:
        logger.error(f"Not all children of the Split Token are chains: {evo_token}")
        return False

    subchildren_valid = all(is_valid_token(i, False) for i in split.children)
    if not subchildren_valid:
        logger.error(f"Not all subchildren of the Split Token are valid: {evo_token}")
    return subchildren_valid


def valid_chain_ends(evo_token: EvoChainToken, start_with_poke: bool) -> bool:
    chain = evo_token.chain

    if len(chain) == 0:
        logger.error(f"Chain of length 0 found!")
        return False

    if start_with_poke == (chain[0].pokemon is None):
        logger.error(f"Starting element is not of expected type")
        return False

    if len(chain) > 1:
        # Can end pokemon or pokemon-split
        end_poke = chain[-1].pokemon is not None
        end_poke_split = (chain[-2].pokemon is not None) and (
            isinstance(chain[-1], SplitToken)
        )

        if not (end_poke or end_poke_split):
            logger.error(f"Chain does not end correctly: {evo_token.chain}")
            return False

    return True


def is_valid_token(evo_token: EvoChainToken, start_with_poke: bool = True) -> bool:
    """The only types of chains supported are of the form
    Language restrictions:
    - No chains of length 1
    - Chains should not regroup after a split -
    - Chain must end in a pokemon or pokemon then split
    - The only direct children of splits are chains -
    - Chains can only be direct children of splits -
    - Chain must alternate between evolution and pokemon every time
    """

    if subchain_present(evo_token):
        logger.error(f"Subchain present in the current chain: {evo_token}")
        return False

    if not split_valid(evo_token):
        return False

    if not valid_chain_ends(evo_token, start_with_poke):
        return False

    # verify alternating pattern
    is_poke = start_with_poke

    for i in evo_token.chain:
        if isinstance(i, SplitToken):
            continue

        if is_poke == (i.pokemon is None):
            logger.error(f"Chain does not alternate as expected: {evo_token}")
            return False

        is_poke = not is_poke

    return True


def tokenize_list(html_list: List) -> Deque:
    """
    Tokenizes a list of html fragments into a full tree describing the evolution chain

     Possible children
     - i.icon-arrow:contains("+") (Two or more pokemon generated) -
     - infocard (Pokemon) -
     - i.icon-arrow.icon-arrow (Evolution) -
     - infocard-evo-split (Fork in chain)
     - infocard-list-evo (evolution subtree) -
    """

    if len(html_list) == 0:
        return deque()

    for lexeme in LEXABLE_HTML_ELEMENTS:
        if lexeme.matches(html_list):
            head = lexeme.create_token(html_list)
            tail = tokenize_list(lexeme.consume_lexeme(html_list))
            tail.appendleft(head)
            return tail

    # Does not match one of the given cases
    raise NotImplementedError()


def tokenize(html: Tag) -> EvoChainToken:
    """
    Convert this to a fully fledge functional style with pythonic switch-case
    and split everything off into its own function and verifies that the list
    is well formed. Note the graph returned is necessarily a tree

     Possible children
     - i.icon-arrow:contains("+") (Two or more pokemon generated) -
     - infocard (Pokemon) -
     - i.icon-arrow.icon-arrow (Evolution) -
     - infocard-evo-split (Fork in chain)
     - infocard-list-evo (evolution subtree) -
    """
    html_list = html.find_all(recursive=False)

    tree = tokenize_list(html_list)

    token = EvoChainToken(tree, html_list)

    if not is_valid_token(token):
        raise ValueError(f"Invalid token generated: {token}")

    return token
