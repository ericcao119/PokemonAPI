"""Contains basic code for completely defining a speciess/variant in pokemon"""

from enum import IntEnum
from typing import Any, Dict, Optional, Tuple

import bs4
from bs4.element import Tag
from loguru import logger

from src.data.poke_enums import PType, Shape
from src.data.species import DexEntryComponent, MoveComponent
from src.gather_files import request_pokeurl_pokemondb


def index_from_tablist(tablist_html: Tag, variant: str) -> int:
    """Determines what index the variant's information is in and returns the id of
    the corresponding internal link"""
    # TODO: Handle None case gracefully
    tablist = tablist_html.select("a.tabs-tab")
    variants = [i.string for i in tablist]
    index = variants.index(variant)
    return tablist[index]["href"]


def get_variant_basics_html(html: Tag, species: str, variant: Optional[str]) -> Tag:
    """Generate dex basics from scraped html"""
    if variant is None:
        variant = species

    tablist_html = html.select_one("div.tabs-tab-list")

    index = index_from_tablist(tablist_html, variant)

    # Select correct tab
    variant_basics = html.select_one(index)
    return variant_basics


# class BasicIndices(IntEnum):
#     national_index = auto()
#     typing_index = auto()
#     kind_index = auto()
#     height_index = auto()
#     weight_index = auto()
#     abilities_index = auto()
#     local_index = auto()


# Note: We ignore the type here because mypy currently
# does not support Enum's funcitonal API
BasicIndices = IntEnum(  # type: ignore # pylint: disable=C0103
    "BasicIndices",
    "national_index typing_index "
    "kind_index height_index weight_index "
    "abilities_index local_index",
    start=0,
)

# Mapping of
BODY_STYLE_MAPPING = {
    Shape.OnlyHead: 0,
    Shape.HeadLegs: 1,
    Shape.Fish: 2,
    Shape.Insectoid: 3,
    Shape.Quadruped: 4,
    Shape.WingedInsectoid: 5,
    Shape.MultipleFusedBodies: 6,
    Shape.Tentacles_MultipleLegs: 7,
    Shape.HeadBase: 8,
    Shape.BipedalTail: 9,
    Shape.Humanoid: 10,
    Shape.TwoWings: 11,
    Shape.Serpent: 12,
    Shape.HeadArms: 13,
}


def parse_basics(db_dex_html: Tag, flavor_html: Tag) -> DexEntryComponent:
    """Creates a basic DexEntry from the given html"""
    initial_filter = "h2:contains('Pokédex data') + table.vitals-table"
    html_subset = db_dex_html.select_one(initial_filter)
    rows = html_subset.select("tr")

    national_row = rows[BasicIndices.national_index]  # type: ignore
    typing_row = rows[BasicIndices.typing_index]  # type: ignore
    kind_row = rows[BasicIndices.kind_index]  # type: ignore
    height_row = rows[BasicIndices.height_index]  # type: ignore
    weight_row = rows[BasicIndices.weight_index]  # type: ignore
    ability_row = rows[BasicIndices.abilities_index]  # type: ignore
    local_row = rows[BasicIndices.local_index]  # type: ignore

    # Dead simple parsing of html
    dex_params: Dict[str, Any] = {}

    dex_params["national_dex_num"] = int(national_row.select_one("td > strong").string)
    dex_params["types"] = [PType[i.string] for i in typing_row.select("td > a")]
    dex_params["kind"] = kind_row.select_one("td").string
    dex_params["height"] = float(height_row.select_one("td").string.split()[0])
    dex_params["weight"] = float(weight_row.select_one("td").string.split()[0])
    dex_params["abilities"] = [i.string for i in ability_row.select("td > span > a")]
    dex_params["hidden_abilities"] = [i.string for i in ability_row.select("small > a")]

    raw_nums = local_row.select_one("td")
    NavigableString = bs4.element.NavigableString
    dex_params["regional_dex_nums"] = [
        i for i in raw_nums if isinstance(i, NavigableString)
    ]
    dex_params["regional_dex_nums"] = [
        int(i.strip()) for i in dex_params["regional_dex_nums"]
    ]

    dex_params["flavor_text"] = flavor_html.select("tr > td")[-1].string

    # TODO: Implement the ones below
    # color: Color = Color.INVALID
    # shape: Shape = Shape.INVALID

    return DexEntryComponent(**dex_params)


def __select_move_tab(moves_html: Tag):
    """Selects the move tab with the most categories"""
    fragments = [i["href"] for i in moves_html.select("div.tabs-tab-list > a")]
    generation_select = [moves_html.select(f"{frag} h3") for frag in fragments]
    return max(generation_select, key=lambda x: len(x))


def parse_moves(
    moves_html: Tag, species: str, variant: Optional[str] = None
) -> MoveComponent:
    """Generates a MoveComponent from the given move lists. The generation with more
    move categories will be used."""
    if variant is None:
        variant = species

    key_mapping = {
        "Moves learnt by level up": "learned_moves",
        "Moves learnt by TM": "tm_moves",
        "Egg moves": "egg_moves",
        "Moves learnt by TR": "tr_moves",
        "Move Tutor moves": "tutor_moves",
        "Transfer-only moves": "transfer_moves",
    }

    def sorted_moves(move_list):
        return sorted([i.string for i in move_list.select("a.ent-name")])

    def technical_extract(move_list):
        pairs = zip(move_list.select("td.cell-num > a"), move_list.select("a.ent-name"))
        return sorted([(int(i.string), j.string) for (i, j) in pairs])

    def number_extract(move_list):
        pairs = zip(
            move_list.select("td.cell-num:first-child"), move_list.select("a.ent-name")
        )
        return sorted([(int(i.string), j.string) for (i, j) in pairs])

    transform_mapping = {
        "learned_moves": number_extract,
        "tm_moves": technical_extract,
        "egg_moves": sorted_moves,
        "tr_moves": technical_extract,
        "tutor_moves": sorted_moves,
        "transfer_moves": sorted_moves,
    }

    move_anchors = __select_move_tab(moves_html)
    keys = [
        key_mapping[i.string] for i in move_anchors if i.string in key_mapping.keys()
    ]
    move_tables = [
        i.findNext("div") for i in move_anchors if i.string in key_mapping.keys()
    ]

    moves = {i: transform_mapping[i](j) for (i, j) in zip(keys, move_tables)}

    return MoveComponent(**moves)


def __scrape_flavor_text(html, species: str, variant: Optional[str]) -> Tag:
    """Helper method to extract flavor text"""
    # main is necessary to greatly reduce the number of
    flavor_html = html.select_one(
        f"main h3:contains({variant}) + div.resp-scroll > table > tbody"
    )

    if flavor_html is None:
        logger.info(f"Variant {variant} of Species {species} does not have a dex entry")
        flavor_html = html.select_one(
            f"main h3:contains({species}) + div.resp-scroll > table > tbody"
        )

    if flavor_html is None:
        logger.info(
            "Flavor text is not listed under species name, "
            "so instead the default flavor text is being used."
        )
        flavor_html = html.select_one(
            f"main h2:contains('Pokédex entries') + div.resp-scroll > table > tbody"
        )

    if flavor_html is None:
        logger.error(f"Species does not contain a dex entry")

    return flavor_html


def scrape_pokemon(species: str, variant: str = None) -> Tuple[Tag, Tag, Tag, Tag]:
    """Returns relevant html fragments from pokemon html file"""
    if variant is None:
        variant = species

    db_file = request_pokeurl_pokemondb(species)

    if not db_file.exists():
        raise ValueError(f"File {db_file} does not exist")

    html = bs4.BeautifulSoup(db_file.read_text(), "html.parser")

    dex_basics = html.select_one("#dex-basics ~ div.tabset-basics.tabs-wrapper")
    dex_basics = get_variant_basics_html(dex_basics, species, variant)

    evolution_html = html.select_one("div.infocard-list-evo")
    moves_html = html.select_one("div.tabset-moves-game.tabs-wrapper")
    flavor_html = __scrape_flavor_text(html, species, variant)

    return dex_basics, evolution_html, moves_html, flavor_html


def scrape_body_style():
    """Scrape a list of pokemon classified into body shape"""
    raise NotImplementedError("This is a stretch goal and has not been implemented yet")


def scrape_color():
    """Scrape a list of pokemon classified into color"""
    raise NotImplementedError("This is a stretch goal and has not been implemented yet")
