import json
import re

from dataclasses import is_dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any


from src.scraper.scrape import generate_all_pokemon, generate_abilities

from jinja2 import Template, FileSystemLoader, Environment


class JsonEncoderCodec(json.JSONEncoder):
    transforms: Dict[Any, Any] = {}

    def default(self, z):
        if issubclass(type(z), Enum):
            return z.name

        if is_dataclass(z):
            return asdict(z)

        if type(z) in JsonEncoderCodec.transforms:
            return JsonEncoderCodec.transforms[type(z)](z)
        else:
            return super().default(z)

current_dir = Path(__file__).parent
template_dir = current_dir/'templates'

template_loader = FileSystemLoader(searchpath=str(template_dir))
template_env = Environment(loader=template_loader, autoescape=True)
template_env.filters['idify'] = lambda name: re.sub(r'[\.:]', '', re.sub(r'\s', '-', name))


pokedex: Dict = generate_all_pokemon()
# pokedex: Dict = {}
json_dex = {k: json.dumps(v, cls=JsonEncoderCodec, indent=2) for k, v in pokedex.items()}


abilities: Dict = generate_abilities()
json_abilities = {k: json.dumps(v, cls=JsonEncoderCodec, indent=2) for k, v in abilities.items()}

def write_pokedex():
    pokemon_folder: Path = current_dir/'api/pokemon'

    for k, v in json_dex.items():
        file = pokemon_folder/f'{k}.json'
        file.touch()
        file.write_text(v)

def write_abilities():
    abilities_folder: Path = current_dir/'api/abilities'

    for k, v in json_abilities.items():
        file = abilities_folder/f'{k}.json'
        file.touch()
        file.write_text(v)


def create_index():
    out = template_env.get_template('index.html').render(pokedex=json_dex, abilities=json_abilities)

    with open(str(current_dir/'index.html'), 'w') as f:
        print(out, file=f)


write_abilities()
write_pokedex()
create_index()