from bs4 import BeautifulSoup
import functools

import src.gather_files
import src.national_dex
from src.utils.utils import separate_conjuctive
from config import FormDifferences


src.gather_files.populate_cache()


def form_differences_list():
    with FormDifferences.open('r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    toc = soup.find('div', attrs={'id': 'toc', 'class': 'toc'})
    l1 = toc.find('ul')
    li = l1('li', recursive=False)[:2]
    pokemon_list = list(map(lambda x: x.find('ul'), li))

    # print(pokemon_list)
    form_diffs = pokemon_list[0]('li', recursive=False)
    print('form_diffs', form_diffs)
    form_likes = pokemon_list[1]('li', recursive=False)

    print('form_likes', form_likes)
    form_diff_raw = list(
        map(lambda x: (x.find('span', attrs={'class': 'toctext'}).string), form_diffs))
    form_like_raw = list(
        map(lambda x: (x.find('span', attrs={'class': 'toctext'}).string), form_likes))

    print('form_diff:', form_diff_raw)
    print('form_like:', form_like_raw)

    def func(acc, e):
        acc.extend(separate_conjuctive(e))
        return acc

    form_diff = sorted(list(functools.reduce(func, form_diff_raw, [])))
    form_like = sorted(list(functools.reduce(func, form_like_raw, [])))

    print('form_diff:', form_diff)
    print('form_like:', form_like)

# Need to extract Regional forms, Gigantimax forms, and Mega evolutions


# form_differences_list()
# src.national_dex.parse_list()
