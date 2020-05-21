"""Basic configuration information abour various resources"""

from pathlib import Path
from typing import Dict, Final

from bson.codec_options import CodecOptions

from src.data.codec import TYPE_REGISTRY

ROOT_DIR: Final[Path] = (Path(__file__).parent).absolute()
CACHE_DIR: Final[Path] = (ROOT_DIR / "cache").absolute()
POKEMONDB_DIR: Final[Path] = (CACHE_DIR / "pokemondb").absolute()
SPECIES_POKEDB_DIR: Final[Path] = (POKEMONDB_DIR / "pokedex").absolute()
MOVE_POKEDB_DIR: Final[Path] = (POKEMONDB_DIR / "move").absolute()
ABILITY_POKEDB_DIR: Final[Path] = (POKEMONDB_DIR / "ability").absolute()

# NationalDex: Final[Path] = CACHE_DIR / "NationalDex.html"
# FormDifferences: Final[Path] = CACHE_DIR / "FormDifferences.html"
ABILITY_LIST: Final[Path] = CACHE_DIR / "AbilityList.html"
POKEDEX: Final[Path] = CACHE_DIR / "Pokedex.html"
BODY_STYLE: Final[Path] = CACHE_DIR / "BodyStyle.html"
COLOR_LIST: Final[Path] = CACHE_DIR / "ColorList.html"
EVOLUTION_GRAPH: Final[Path] = CACHE_DIR / "EvolutionGraph.html"
ITEMS_LIST: Final[Path] = CACHE_DIR / "Items.html"
MOVES_LIST: Final[Path] = CACHE_DIR / "Moves.html"


POKEMONDB_STUB: Final[str] = "https://pokemondb.net"
DBDEX_STUB: Final[str] = "https://pokemondb.net/pokedex/"
BULBADEX_STUB: Final[str] = "https://bulbapedia.bulbagarden.net/wiki/"

URLS: Final[Dict[Path, str]] = {
    ABILITY_LIST: "https://pokemondb.net/ability",
    POKEDEX: "https://pokemondb.net/pokedex/all",
    BODY_STYLE: "https://bulbapedia.bulbagarden.net/wiki/List_of_Pokémon_by_body_style",
    COLOR_LIST: "https://bulbapedia.bulbagarden.net/wiki/List_of_Pokémon_by_color",
    EVOLUTION_GRAPH: "https://pokemondb.net/evolution",
    ITEMS_LIST: "https://pokemondb.net/item/all",
    MOVES_LIST: "https://pokemondb.net/move/all",
}

CODEC_OPTIONS: Final[CodecOptions] = CodecOptions(type_registry=TYPE_REGISTRY)
