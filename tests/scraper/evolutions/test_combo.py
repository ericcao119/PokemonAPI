from pathlib import Path

import bs4

from src.scraper.evolutions.tokenizer import ComboLex, ComboToken

shedinja_file = Path(__file__).parent / "ShedinjaTest.html"
shedinja = bs4.BeautifulSoup(shedinja_file.read_text(), "lxml")
children = shedinja.select_one("body").find_all(recursive=False)


def test_combo_matches():
    assert not ComboLex.matches([])
    assert not ComboLex.matches(children[0])
    assert not ComboLex.matches(children[:2])
    assert ComboLex.matches(children)


def test_combo_token():
    token = ComboLex.create_token(children)
    assert [("Ninjask", "Ninjask"), ("Shedinja", "Shedinja")] == token.pokemon
    assert token.evolution_method is None
