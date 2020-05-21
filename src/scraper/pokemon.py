"""Contains basic code for completely defining a speciess/variant in pokemon"""

import re
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import bs4
from bs4.element import Tag
from loguru import logger

from src.data.poke_enums import EggGroup, LevelingRate, PType
from src.data.species import (
    REGIONAL_TEXT_MAPPING,
    BreedingComponent,
    DexEntryComponent,
    MoveComponent,
    Species,
    TrainingComponent,
)
from src.data.stats import BaseStats, EffortValues
from src.data.typing import SpeciesId, VariantId
from src.gather_files import request_pokeurl_pokemondb
from src.utils.general import normalize_unicode

# TODO: Add LRU caching for soup (Note that this caching is per worker, so chunking is needed)
OMISSION = "—"


def _index_from_tablist(tablist_html: Tag, variant: VariantId) -> int:
    """Determines what index the variant's information is in and returns the id of
    the corresponding internal link

    >>> a = bs4.BeautifulSoup('''<div class="tabs-tab-list">
    ... <a class="tabs-tab active" href="#tab-basic-244">Entei</a>
    ... </div>''', 'lxml')
    >>> _index_from_tablist(a, "Entei")
    '#tab-basic-244'
    >>> a = bs4.BeautifulSoup('''<div class="tabs-tab-list">
    ...   <a class="tabs-tab active" href="#tab-basic-3">
    ...    Venusaur
    ...   </a>
    ...   <a class="tabs-tab" href="#tab-basic-11001">
    ...    Mega Venusaur
    ...   </a>
    ...  </div>''', 'lxml')
    >>> _index_from_tablist(a, "Venusaur")
    '#tab-basic-3'
    >>> _index_from_tablist(a, "Mega Venusaur")
    '#tab-basic-11001'
    """
    tablist = tablist_html.select("a.tabs-tab")
    variants = [normalize_unicode(i.string).strip().upper() for i in tablist]
    index = variants.index(normalize_unicode(variant.strip()).upper())
    return tablist[index]["href"]


def _determine_gender_rate(raw_str: str):
    """Scrapes gender rate from the raw_string

    >>> _determine_gender_rate('Genderless') # Returns None
    >>> _determine_gender_rate('87.5% male, 12.5% female')
    87.5
    >>> _determine_gender_rate('50% male, 50% female')
    50.0
    >>> _determine_gender_rate('—')
    nan
    """
    if raw_str == OMISSION:
        return float("nan")

    cleaned = raw_str.strip()
    if cleaned == "Genderless":
        return float("nan")

    match = re.search(r"[-+]?\d*\.\d+|\d+|$", cleaned)

    if match is None or match == "":
        return float("nan")

    return float(match.group())


def _select_move_tab(moves_html: Tag):
    """Selects the move tab with the most categories"""
    fragments = [i["href"] for i in moves_html.select("div.tabs-tab-list > a")]
    generation_select = [moves_html.select(f"{frag} h3") for frag in fragments]
    return max(zip(generation_select, fragments), key=lambda x: len(x[0]))


class DexEntrySubpage:
    """Wrapper class for containing dex entry information"""

    def __init__(self, basics_html: Tag, flavor_html: Tag):
        initial_filter = "h2:contains('Pokédex data') + .vitals-table"
        self.table = basics_html.select_one(initial_filter)
        self.flavor_html = flavor_html

    @cached_property
    def national_dex_num(self) -> int:
        return int(
            self.table.select_one("th:contains('National') + td > strong").string
        )

    @cached_property
    def kind(self) -> str:
        return str(self.table.select_one("th:contains('Species') + td").string)

    @cached_property
    def height(self) -> float:
        height_str = str(
            self.table.select_one("th:contains('Height') + td").string
        ).strip()
        if height_str != OMISSION:
            return float(height_str.split()[0])
        else:
            return float("nan")

    @cached_property
    def weight(self) -> float:
        weight_str = str(
            self.table.select_one("th:contains('Weight') + td").string
        ).strip()
        if weight_str != OMISSION:
            return float(weight_str.split()[0])
        else:
            return float("nan")

    @cached_property
    def abilities(self) -> List[str]:
        return [
            str(i.string)
            for i in self.table.select("th:contains('Abilities') + td > span > a")
        ]

    @cached_property
    def hidden_abilities(self) -> List[str]:
        return [
            str(i.string)
            for i in self.table.select("th:contains('Abilities') + td > small > a")
        ]

    @cached_property
    def regional_dex_nums(self) -> Dict[str, int]:
        raw_nums: Tag = self.table.select_one("th:contains('Local') + td")
        NavigableString = bs4.element.NavigableString

        if raw_nums is None or raw_nums.string == OMISSION:
            return {}
        regions = [
            REGIONAL_TEXT_MAPPING[str(small.string)]
            for small in raw_nums
            if not isinstance(small, NavigableString)
        ]
        nums = [int(i.strip()) for i in raw_nums if isinstance(i, NavigableString)]
        return dict(zip(regions, nums))

    @cached_property
    def flavor_text(self) -> str:
        return str(self.flavor_html.find_all("td")[-1].string)

    @cached_property
    def dex_entry_component(self) -> DexEntryComponent:
        """Creates a basic DexEntry from the given html"""

        # Dead simple parsing of html
        dex_params: Dict[str, Any] = {}

        dex_params["national_dex_num"] = self.national_dex_num
        dex_params["kind"] = self.kind
        dex_params["height"] = self.height
        dex_params["weight"] = self.weight

        dex_params["abilities"] = self.abilities
        dex_params["hidden_abilities"] = self.hidden_abilities
        dex_params["regional_dex_nums"] = self.regional_dex_nums

        dex_params["flavor_text"] = self.flavor_text

        # TODO: Implement the ones below
        # color: Color = Color.INVALID
        # shape: Shape = Shape.INVALID

        return DexEntryComponent(**dex_params)


class BreedingSubpage:
    def __init__(self, basics_html):
        initial_filter = "h2:contains('Breeding') + .vitals-table"
        self.table = basics_html.select_one(initial_filter)

    @cached_property
    def egg_groups(self) -> List[EggGroup]:
        egg_group_filter = "tr > th:contains('Egg Groups') + td"
        egg_group_string = str(self.table.select_one(egg_group_filter).text).strip()

        if egg_group_string == OMISSION:
            return []
        else:
            return [
                EggGroup[i.strip().replace(" ", "").replace("-", "").title()]
                for i in egg_group_string.split(",")
            ]

    @cached_property
    def male_rate(self) -> float:
        gender_dist_filter = "tr > th:contains('Gender') + td"
        gender_rate_string = str(self.table.select_one(gender_dist_filter).text)
        return _determine_gender_rate(gender_rate_string)

    @cached_property
    def egg_cycles(self) -> Optional[int]:
        egg_cycles_filter = "tr > th:contains('Egg cycles') + td"
        egg_cycles_string = str(
            list(self.table.select_one(egg_cycles_filter).stripped_strings)[0]
        )
        if egg_cycles_string == OMISSION:
            return None
        return int(egg_cycles_string)

    @cached_property
    def steps_to_hatch_lower(self) -> Optional[int]:
        if self.egg_cycles is None:
            return None
        return (self.egg_cycles - 1) * 257 + 1

    @cached_property
    def steps_to_hatch_upper(self) -> Optional[int]:
        if self.egg_cycles is None:
            return None
        return self.egg_cycles * 257

    @cached_property
    def breeding_component(self) -> BreedingComponent:
        dex_params: Dict[str, Any] = {}
        dex_params["egg_groups"] = self.egg_groups
        dex_params["male_rate"] = self.male_rate

        dex_params["egg_cycles"] = self.egg_cycles
        dex_params["steps_to_hatch_lower"] = self.steps_to_hatch_lower
        dex_params["steps_to_hatch_upper"] = self.steps_to_hatch_upper

        return BreedingComponent(**dex_params)


class TrainingSubpage:
    def __init__(self, basics_html):
        initial_filter = "h2:contains('Training') + .vitals-table"
        self.table = basics_html.select_one(initial_filter)

    @cached_property
    def effort_points(self) -> Optional[EffortValues]:
        ev_yield_filter = "tr > th:contains('EV') + td"
        return EffortValues.from_string(self.table.select_one(ev_yield_filter).string)

    @cached_property
    def catch_rate(self) -> Optional[int]:
        catch_filter = "tr > th:contains('Catch') + td"
        catch_list = [
            i.strip()
            for i in self.table.select_one(catch_filter).find_all(
                text=True, recursive=False
            )
        ]
        return int(catch_list[0]) if catch_list[0] != OMISSION else None

    @cached_property
    def base_friendship(self) -> Optional[int]:
        friendship_filter = "tr > th:contains('Friendship') + td"
        friendship_list = [
            i.strip()
            for i in self.table.select_one(friendship_filter).find_all(
                text=True, recursive=False
            )
        ]
        return int(friendship_list[0]) if friendship_list[0] != OMISSION else None

    @cached_property
    def base_exp_yield(self) -> Optional[int]:
        base_exp_filter = "tbody > tr > th:contains('Base Exp.') + td"
        base_exp = str(self.table.select_one(base_exp_filter).string)
        return int(base_exp) if base_exp != OMISSION else None

    @cached_property
    def leveling_rate(self) -> LevelingRate:
        level_filter = "tbody > tr > th:contains('Growth Rate') + td"
        level_rate = self.table.select_one(level_filter).string.replace(" ", "").strip()
        return (
            LevelingRate[level_rate] if level_rate != OMISSION else LevelingRate.INVALID
        )

    @cached_property
    def training_component(self) -> TrainingComponent:
        dex_params: Dict[str, Any] = {}
        dex_params["effort_points"] = self.effort_points
        dex_params["catch_rate"] = self.catch_rate
        dex_params["base_friendship"] = self.base_friendship
        dex_params["base_exp_yield"] = self.base_exp_yield
        dex_params["leveling_rate"] = self.leveling_rate
        return TrainingComponent(**dex_params)


class SpeciesPage:
    def __init__(self, species: str, path: Path):
        self.species = species
        self._soup: bs4.BeautifulSoup = bs4.BeautifulSoup(path.read_text(), "lxml")

        for linebreak in self._soup.find_all("br"):
            linebreak.extract()

    @cached_property
    def dex_basics(self) -> Tag:
        return self._soup.select_one(".tabset-basics")

    @cached_property
    def moves_html(self) -> Tag:
        return self._soup.select_one(".tabset-moves-game.tabs-wrapper")

    def flavor_html(self, variant) -> Tag:
        flavor_html = self._soup.select_one(
            f'main h3:contains("{variant}") + div.resp-scroll > table > tbody'
        )

        if flavor_html is None:
            logger.trace(
                f"Variant {variant} of Species {self.species} does not have a dex entry"
            )
            flavor_html = self._soup.select_one(
                f'main h3:contains("{self.species}") + div.resp-scroll > table > tbody'
            )

        if flavor_html is None:
            logger.trace(
                "Flavor text is not listed under species name, "
                "so instead the default flavor text is being used."
            )
            flavor_html = self._soup.select_one(
                f"main h2:contains('Pokédex entries') + div.resp-scroll > table > tbody"
            )

        if flavor_html is None:
            logger.debug(
                f"Species does not contain a dex entry. Using a unlisted form dex entry"
            )

            flavor_html = self._soup.select_one(
                f"main h2:contains('Pokédex entries') + h3 + div.resp-scroll > table > tbody"
            )

        if flavor_html is None:
            logger.error(f"Species does not contain a dex entry.")

        return flavor_html


class VariantSubpage:
    def __init__(self, variant: str, parent: SpeciesPage):
        self.variant = variant if variant is not None else parent.species
        self.parent = parent

    @cached_property
    def flavor_text_html(self) -> Tag:
        return self.parent.flavor_html(self.variant)

    @cached_property
    def _dex_basics_tablist(self) -> Tag:
        return self.parent.dex_basics.select_one("div.tabs-tab-list")

    @cached_property
    def variant_basics_html(self) -> Tag:
        """Generate dex basics from scraped html"""
        index = _index_from_tablist(self._dex_basics_tablist, self.variant)
        # Select correct tab
        variant_basics = self.parent.dex_basics.select_one(index)
        return variant_basics

    @cached_property
    def dex_entry(self) -> DexEntryComponent:
        return DexEntrySubpage(
            self.variant_basics_html, self.flavor_text_html
        ).dex_entry_component

    @cached_property
    def breeding(self) -> BreedingComponent:
        return BreedingSubpage(self.variant_basics_html).breeding_component

    @cached_property
    def training(self) -> TrainingComponent:
        return TrainingSubpage(self.variant_basics_html).training_component

    @cached_property
    def moves(self) -> MoveComponent:
        key_mapping = {
            "Moves learnt by level up": "learned_moves",
            "Moves learnt by TM": "tm_moves",
            "Egg moves": "egg_moves",
            "Moves learnt by TR": "tr_moves",
            "Move Tutor moves": "tutor_moves",
            "Transfer-only moves": "transfer_moves",
            "Moves learnt on evolution": "evolution_moves",
        }

        def sorted_moves(move_list):
            if move_list is None:
                return []
            return sorted([str(i.string) for i in move_list.select("a.ent-name")])

        def technical_extract(move_list):
            if move_list is None:
                return []
            pairs = zip(
                move_list.select("td.cell-num > a"), move_list.select("a.ent-name")
            )
            return sorted([(int(i.string), str(j.string)) for (i, j) in pairs])

        def number_extract(move_list):
            if move_list is None:
                return []
            pairs = zip(
                move_list.select("td.cell-num:first-child"),
                move_list.select("a.ent-name"),
            )
            return sorted([(int(i.string), str(j.string)) for (i, j) in pairs])

        TRANSFORM_MAPPING = {
            "learned_moves": number_extract,
            "tm_moves": technical_extract,
            "egg_moves": sorted_moves,
            "tr_moves": technical_extract,
            "tutor_moves": sorted_moves,
            "transfer_moves": sorted_moves,
            "evolution_moves": sorted_moves,
        }

        move_anchors, href = _select_move_tab(self.parent.moves_html)
        keys = [
            key_mapping[str(i.string)]
            for i in move_anchors
            if i.string in key_mapping.keys()
        ]
        move_tables = [
            self.parent.moves_html.select_one(
                href + f" h3:contains('{str(i.string)}') + p + div.resp-scroll"
            )
            for i in move_anchors
            if i.string in key_mapping.keys()
            # i.findNext("div") for i in move_anchors if i.string in key_mapping.keys()
        ]

        moves = {i: TRANSFORM_MAPPING[i](j) for (i, j) in zip(keys, move_tables)}

        return MoveComponent(**moves)


@lru_cache
def get_species_page(species: str, url: str):
    path = request_pokeurl_pokemondb(url)
    return SpeciesPage(species, path)


def create_species(
    species: SpeciesId,
    variant: VariantId,
    typing: List[PType],
    stats: BaseStats,
    url: str,
) -> Species:
    """Create full species information"""
    species_page = get_species_page(species, url)
    variant_page = VariantSubpage(variant, species_page)

    species_info: Dict[str, Any] = {"species_name": species, "variant_name": species}

    species_info["species_name"] = species
    species_info["variant_name"] = variant
    species_info["base_stats"] = stats
    species_info["types"] = typing

    species_info["dex_entry"] = variant_page.dex_entry
    species_info["move_info"] = variant_page.moves
    species_info["training_info"] = variant_page.training
    species_info["breeding_info"] = variant_page.breeding

    return Species(**species_info)


def scrape_body_style():
    """Scrape a list of pokemon classified into body shape"""
    raise NotImplementedError("This is a stretch goal and has not been implemented yet")


def scrape_color():
    """Scrape a list of pokemon classified into color"""
    raise NotImplementedError("This is a stretch goal and has not been implemented yet")
