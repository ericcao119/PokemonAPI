import logging

from pathlib import Path
from typing import Final, Dict

from src.data.codec import TYPE_REGISTRY
from bson.codec_options import CodecOptions

# a = logging.LogRecord()
# a.msecs

ROOT_DIR: Final[Path] = (Path(__file__).parent).absolute()
CACHE_DIR: Final[Path] = (ROOT_DIR / "cache").absolute()

NationalDex: Final[Path] = CACHE_DIR / "NationalDex.html"
FormDifferences: Final[Path] = CACHE_DIR / "FormDifferences.html"
AbilityList: Final[Path] = CACHE_DIR / "AbilityList.html"
Pokedex: Final[Path] = CACHE_DIR / "Pokedex.html"

URLS: Final[Dict[Path, str]] = {
    NationalDex: "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number",
    FormDifferences: "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_form_differences",
    AbilityList: "https://pokemondb.net/ability",
    Pokedex: "https://pokemondb.net/pokedex/all",
}

logging.basicConfig(
    filename="output.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="{process} {processName:<12} {asctime},{msecs:0>3.0f} {name} {levelname} {message}",
    level=logging.DEBUG,
    style="{",
)

CODEC_OPTIONS: Final[CodecOptions] = CodecOptions(type_registry=TYPE_REGISTRY)
