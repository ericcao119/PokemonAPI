"""Contains basic code for completely defining a speciess/variant in pokemon"""

import re
from typing import Any, Dict, Optional, Tuple

import bs4
from bs4.element import Tag
from loguru import logger

from src.data.poke_enums import EggGroup, LevelingRate, PType
from src.data.species import (
    BreedingComponent,
    DexEntryComponent,
    MoveComponent,
    TrainingComponent,
)
from src.data.stats import EffortValues
from src.gather_files import request_pokeurl_pokemondb
from src.utils.general import normalize_unicode


def index_from_tablist(tablist_html: Tag, variant: str) -> int:
    """Determines what index the variant's information is in and returns the id of
    the corresponding internal link

    >>> a = bs4.BeautifulSoup('''<div class="tabs-tab-list">
    ... <a class="tabs-tab active" href="#tab-basic-244">Entei</a>
    ... </div>''', 'lxml')
    >>> index_from_tablist(a, "Entei")
    '#tab-basic-244'
    >>> a = bs4.BeautifulSoup('''<div class="tabs-tab-list">
    ...   <a class="tabs-tab active" href="#tab-basic-3">
    ...    Venusaur
    ...   </a>
    ...   <a class="tabs-tab" href="#tab-basic-11001">
    ...    Mega Venusaur
    ...   </a>
    ...  </div>''', 'lxml')
    >>> index_from_tablist(a, "Venusaur")
    '#tab-basic-3'
    >>> index_from_tablist(a, "Mega Venusaur")
    '#tab-basic-11001'
    """
    tablist = tablist_html.select("a.tabs-tab")
    variants = [normalize_unicode(i.string).strip().upper() for i in tablist]
    index = variants.index(normalize_unicode(variant.strip()).upper())
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


def parse_basics(db_dex_html: Tag, flavor_html: Tag) -> DexEntryComponent:
    """Creates a basic DexEntry from the given html"""
    initial_filter = "h2:contains('Pokédex data') + table.vitals-table"
    html_subset = db_dex_html.select_one(initial_filter)

    # Dead simple parsing of html
    dex_params: Dict[str, Any] = {}

    dex_params["national_dex_num"] = int(
        html_subset.select_one("th:contains('National') + td > strong").string
    )
    dex_params["types"] = [
        PType[i.string] for i in html_subset.select("th:contains('Type') + td > a")
    ]
    dex_params["kind"] = str(
        html_subset.select_one("th:contains('Species') + td").string
    )
    dex_params["height"] = float(
        html_subset.select_one("th:contains('Height') + td").string.split()[0]
    )
    dex_params["weight"] = float(
        html_subset.select_one("th:contains('Weight') +td").string.split()[0]
    )
    dex_params["abilities"] = [
        str(i.string)
        for i in html_subset.select("th:contains('Abilities') + td > span > a")
    ]
    dex_params["hidden_abilities"] = [
        str(i.string)
        for i in html_subset.select("th:contains('Abilities') + td > small > a")
    ]

    raw_nums = html_subset.select_one("th:contains('Local') + td")
    NavigableString = bs4.element.NavigableString
    dex_params["regional_dex_nums"] = [
        int(i.strip()) for i in raw_nums if isinstance(i, NavigableString)
    ]

    dex_params["flavor_text"] = str(flavor_html.select("tr > td")[-1].string)

    # TODO: Implement the ones below
    # color: Color = Color.INVALID
    # shape: Shape = Shape.INVALID

    return DexEntryComponent(**dex_params)


def _determine_gender_rate(raw_str: str):
    """Scrapes gender rate from the raw_string

    >>> _determine_gender_rate('Genderless') # Returns None
    >>> _determine_gender_rate('87.5% male, 12.5% female')
    87.5
    >>> _determine_gender_rate('50% male, 50% female')
    50.0
    """
    cleaned = raw_str.strip()
    if cleaned == "Genderless":
        return None

    match = re.search(r"[-+]?\d*\.\d+|\d+|$", cleaned)

    if match is None or match == "":
        return None

    return float(match.group())


def parse_breeding(db_dex_html: Tag) -> BreedingComponent:
    """Creates a basic DexEntry from the given html"""
    initial_filter = "h2:contains('Breeding') + table.vitals-table"
    html_subset = db_dex_html.select_one(initial_filter)

    # Dead simple parsing of html
    dex_params: Dict[str, Any] = {}

    egg_group_filter = r"tr > th:contains('Egg Groups') + td"
    gender_dist_filter = r"tr > th:contains('Gender') + td"
    egg_cycles_filter = r"tr > th:contains('Egg cycles') + td"
    # Need to test Ungendered
    egg_group_string = str(html_subset.select_one(egg_group_filter).text).strip()
    gender_rate_string = str(html_subset.select_one(gender_dist_filter).text)
    egg_cycles_string = str(
        list(html_subset.select_one(egg_cycles_filter).stripped_strings)[0]
    )

    dex_params["egg_groups"] = [
        EggGroup[i.strip().replace(" ", "")] for i in egg_group_string.split(",")
    ]
    dex_params["male_rate"] = _determine_gender_rate(gender_rate_string)
    dex_params["egg_cycles"] = int(egg_cycles_string)

    dex_params["steps_to_hatch_lower"] = (dex_params["egg_cycles"] - 1) * 257 + 1
    dex_params["steps_to_hatch_upper"] = dex_params["egg_cycles"] * 257

    return BreedingComponent(**dex_params)


def parse_training(db_dex_html: Tag) -> TrainingComponent:
    """Creates a basic TrainingComponent from the given html"""
    initial_filter = "h2:contains('Training') + table.vitals-table"
    html_subset = db_dex_html.select_one(initial_filter)

    # Dead simple parsing of html
    dex_params: Dict[str, Any] = {}

    # html_subset.select_one("tbody > tr > th:contains('EV yield') + td")

    ev_yield_filter = "tr > th:contains('EV') + td"
    catch_filter = "tr > th:contains('Catch') + td"
    friendship_filter = "tr > th:contains('Friendship') + td"
    base_exp_filter = "tbody > tr > th:contains('Base Exp.') + td"
    level_filter = "tbody > tr > th:contains('Growth Rate') + td"

    catch_list = [
        i.strip()
        for i in html_subset.select_one(catch_filter).find_all(
            text=True, recursive=False
        )
    ]

    friendship_list = [
        i.strip()
        for i in html_subset.select_one(friendship_filter).find_all(
            text=True, recursive=False
        )
    ]

    dex_params["effort_points"] = EffortValues.from_string(
        html_subset.select_one(ev_yield_filter).string
    )
    dex_params["catch_rate"] = int(catch_list[0])
    dex_params["base_friendship"] = int(friendship_list[0])
    dex_params["base_exp_yield"] = int(html_subset.select_one(base_exp_filter).string)
    dex_params["leveling_rate"] = LevelingRate[
        html_subset.select_one(level_filter).string.replace(" ", "")
    ]

    return TrainingComponent(**dex_params)


def _select_move_tab(moves_html: Tag):
    """Selects the move tab with the most categories"""
    fragments = [i["href"] for i in moves_html.select("div.tabs-tab-list > a")]
    generation_select = [moves_html.select(f"{frag} h3") for frag in fragments]
    return max(zip(generation_select, fragments), key=lambda x: len(x[0]))


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
        if move_list is None:
            return []
        return sorted([str(i.string) for i in move_list.select("a.ent-name")])

    def technical_extract(move_list):
        if move_list is None:
            return []
        pairs = zip(move_list.select("td.cell-num > a"), move_list.select("a.ent-name"))
        return sorted([(int(i.string), str(j.string)) for (i, j) in pairs])

    def number_extract(move_list):
        if move_list is None:
            return []
        pairs = zip(
            move_list.select("td.cell-num:first-child"), move_list.select("a.ent-name")
        )
        return sorted([(int(i.string), str(j.string)) for (i, j) in pairs])

    transform_mapping = {
        "learned_moves": number_extract,
        "tm_moves": technical_extract,
        "egg_moves": sorted_moves,
        "tr_moves": technical_extract,
        "tutor_moves": sorted_moves,
        "transfer_moves": sorted_moves,
    }

    move_anchors, href = _select_move_tab(moves_html)
    keys = [
        key_mapping[str(i.string)]
        for i in move_anchors
        if i.string in key_mapping.keys()
    ]
    move_tables = [
        moves_html.select_one(
            href + f" h3:contains('{str(i.string)}') + p + div.resp-scroll"
        )
        for i in move_anchors
        if i.string in key_mapping.keys()
        # i.findNext("div") for i in move_anchors if i.string in key_mapping.keys()
    ]

    moves = {i: transform_mapping[i](j) for (i, j) in zip(keys, move_tables)}

    return MoveComponent(**moves)


def _scrape_flavor_text(html, species: str, variant: Optional[str]) -> Tag:
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
    flavor_html = _scrape_flavor_text(html, species, variant)

    return dex_basics, evolution_html, moves_html, flavor_html


def scrape_body_style():
    """Scrape a list of pokemon classified into body shape"""
    raise NotImplementedError("This is a stretch goal and has not been implemented yet")


def scrape_color():
    """Scrape a list of pokemon classified into color"""
    raise NotImplementedError("This is a stretch goal and has not been implemented yet")