from pathlib import Path

import bs4
import pytest

from src.scraper.evolutions.tokenizer import poke_from_infocard

shedinja_file = Path(__file__).parent / "ShedinjaTest.html"
shedinja = bs4.BeautifulSoup(shedinja_file.read_text(), "lxml")
children = shedinja.select_one("body").find_all(recursive=False)


alolan_rattata_file = Path(__file__).parent / "AlolanRattata.html"
alolan_rattata_raw = bs4.BeautifulSoup(alolan_rattata_file.read_text(), "lxml")
rattata_children = alolan_rattata_raw.select_one("body").find_all(recursive=False)


def test_pokemon_extraction():
    assert poke_from_infocard(children[0]) == ("Ninjask", "Ninjask")
    assert poke_from_infocard(children[2]) == ("Shedinja", "Shedinja")
    body = shedinja.select_one("body")

    with pytest.raises(ValueError):
        poke_from_infocard(body)
