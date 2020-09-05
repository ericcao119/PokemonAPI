from pathlib import Path

import bs4

from src.scraper.evolutions.tokenizer import InfocardLex, PokeToken

shedinja_file = Path(__file__).parent / "ShedinjaTest.html"
shedinja = bs4.BeautifulSoup(shedinja_file.read_text(), "lxml")
children = shedinja.select_one("body").find_all(recursive=False)


def test_info_matches():
    assert InfocardLex.matches(children)
    assert InfocardLex.matches([children[0]])
    assert not InfocardLex.matches([children[1]])


def test_info_token():
    token = InfocardLex.create_token(children)
    assert [("Ninjask", "Ninjask")] == token.pokemon
    assert token.evolution_method is None
