import argparse
import json
import os
from dataclasses import asdict
from typing import Any, Dict

from flask import Flask, Response, render_template
from flask.json import dumps

from src.data.species import Species
from src.scraper.pokemon import create_species
from src.scraper.pokedex import scrape_pokedex
from src.utils.general import create_multimap
from src.utils.codec_helpers import JsonEncoderCodec


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path="",
        static_folder="static",
    )

    # app.config.from_mapping(
    # SECRET_KEY='dev',
    # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    species, variants, typing, stats, urls = scrape_pokedex()

    variants_map = create_multimap(species, variants)
    typing_map = create_multimap(species, typing)
    stats_map = create_multimap(species, stats)
    url_map = create_multimap(species, urls)

    # a simple page that says hello
    @app.route("/")
    def root():
        return render_template("index.html")

    @app.route("/api/pokemon/<species>", methods=["GET"])
    def show_base(species: str):
        poke = create_species(
            species,
            variants_map[species][0],
            typing_map[species][0],
            stats_map[species][0],
            url_map[species][0],
        )

        json_str = json.dumps(asdict(poke), cls=JsonEncoderCodec)

        return Response(response=json_str, mimetype="application/json")

    @app.route("/api/pokemon/<species>/<variant>", methods=["GET"])
    def show_variant(species: str, variant: str):
        variant_idx = variants_map[species].index(variant)

        poke = create_species(
            species,
            variant,
            typing_map[species][variant_idx],
            stats_map[species][variant_idx],
            url_map[species][variant_idx],
        )

        json_str = json.dumps(asdict(poke), cls=JsonEncoderCodec)

        return Response(response=json_str, mimetype="application/json")

    return app
