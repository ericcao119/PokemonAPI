import argparse
import json
import os
from dataclasses import asdict
from typing import Any, Dict

from flask import Flask, Response, render_template
from flask.json import dumps

from src.data.species import Species
from src.scraper.pokemon import (
    parse_basics,
    parse_moves,
    parse_training,
    scrape_pokemon,
)
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

    # a simple page that says hello
    @app.route("/")
    def root():
        return render_template("index.html")

    @app.route("/api/pokemon/<species>", methods=["GET"])
    def show_base(species: str):
        dex_basics, evolution_html, moves_html, flavor_html = scrape_pokemon(species)

        species_info: Dict[str, Any] = {
            "species_name": species,
            "variant_name": species,
        }

        species_info["dex_entry"] = parse_basics(dex_basics, flavor_html)
        species_info["move_info"] = parse_moves(moves_html, species)
        species_info["training_info"] = parse_training(dex_basics)

        json_str = json.dumps(asdict(Species(**species_info)), cls=JsonEncoderCodec)

        return Response(response=json_str, mimetype="application/json")

    @app.route("/api/pokemon/<species>/<variant>", methods=["GET"])
    def show_variant(species: str, variant: str):
        return scrape_pokemon(species, variant)

    return app
