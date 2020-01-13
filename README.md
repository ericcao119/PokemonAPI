# Pokemon API

A webscraping project to provide a simple API for Pokemon information.

## Motivation

### What does the project do?

This project acts as an API endpoint for generic information about pokemon. The existing alternative [PokeAPI](https://pokeapi.co/) does not list some forms like partner Eevee as part of Eevee's API endpoint, so I felt that scraping information created by the Pokemon fan community could be helpful in keeping the API up-to-date upon new releases. This has some obvious drawbacks since not all sources have standardized layouts or layouts that are easily parsed.

### Who is the project for?

This project is mostly for automating the process of gather pokemon information. This can be used for data analysis or as an intermediary step in transforming pokemon data to another form like for use in Pokemon Essentials.

A static version of the website that will exists on this github repo (I will setup Github Pages soon). As well, I will also host a dynamic instance that intermittently updates on Google Cloud.

### How do I use it? (installation instructions)

TBD. For now you can run the functions within src.scraper for gathering information, but I will update this later
to be served through the website and in JSON form. Additionally, once I finish you can also use a JSON database that comes with the repository.

### How does it work?

There are three separate tasks involved in serving data in the API endpoint. Managing ownership of cached information, scraping and parsing the HTML document, and serving the information through Sanic.

This project is meant to be a quick project to experiment with using MongoDB, Sanic, and Celery for SpimArena later. I might also return to this later to create some code generation to see how difficult it would be to make it easier to develop applications in Rust for pokemon.

## Completed features

Scraping all pokemon + variants

Scraping all evolution chains

## Mandatory Features

Support for multiple database types

Resource Manager to keep track of files and ownership

LRU caching to handle evictions

Create API endpoint with flask or sanic

Complete list of items (with descriptions and multiple ones per game)

Complete list of TMs

Complete list of Pokemon with different forms

Complete list of Pokemon with Mega Forms

Complete list of Pokemon with Regional Forms

Complete list of Pokemon with Gigantimax Forms

## Stretch features

Complete list of Pokemon with stats (with forms - beware of darumaka it has both a regional form and a form change)

Complete list of Pokemon API with all details (optional variants or separate)

Complete pokemon colors and shapes (Particularly hard since Variants are the same between websites. Minior really messes this up.)

Scrape based on time periods and handle all errors

## Rationale for using Python 3.8

Python 3.8 was used specifically to take advatange of typing.Final and some features from python 3.7 like dict order preservation. This is not the most accessible version of python, but this was used as a learning experience to get to learn some of the newer features in python like dataclasses and also learn of their shortcomings.