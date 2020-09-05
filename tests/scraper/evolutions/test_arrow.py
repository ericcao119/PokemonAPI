from pathlib import Path

import bs4

from src.scraper.evolutions.tokenizer import ArrowLex, EvoToken

shedinja_file = Path(__file__).parent / "ShedinjaTest.html"
shedinja = bs4.BeautifulSoup(shedinja_file.read_text(), "lxml")
children = shedinja.select_one("body").find_all(recursive=False)

evolution_file = Path(__file__).parent / "Evolution.html"
evo = bs4.BeautifulSoup(evolution_file.read_text(), "lxml")
evo_span = evo.select("span")


def test_info_matches():
    assert not ArrowLex.matches(children)
    assert not ArrowLex.matches([children[0]])
    assert not ArrowLex.matches(children[1:])
    assert not ArrowLex.matches([children[1]])
    assert ArrowLex.matches(evo_span)


def test_info_token():
    token = ArrowLex.create_token(evo_span)
    assert token.pokemon is None
    assert token.evolution_method == "(Level 20)"
