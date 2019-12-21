import logging

from pathlib import Path
from collections import namedtuple

from src.data.codec import TYPE_REGISTRY
from bson.codec_options import CodecOptions
# a = logging.LogRecord()
# a.msecs
CACHE_DIR = ((Path(__file__).parent)/'cache').absolute()

NationalDex = CACHE_DIR/'NationalDex.html'
FormDifferences = CACHE_DIR/'FormDifferences.html'
AbilityList = CACHE_DIR/'AbilityList.html'

URLS = {
    NationalDex : 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number',
    FormDifferences : 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_form_differences',
    AbilityList: 'https://pokemondb.net/ability',
}

# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

logging.basicConfig(filename='output.log',
                    filemode='a',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format='{process} {processName:<12} {asctime},{msecs:0>3.0f} {name} {levelname} {message}',
                    level=logging.DEBUG,
                    style='{')

CODEC_OPTIONS = CodecOptions(type_registry=TYPE_REGISTRY)