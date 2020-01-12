# Pokemon API

A webscraping project to provide a simple API for Pokemon information.

## Motivation

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

Python 3.8 was used specifically to take advatange of typing.Final and some features from python 3.7 like dict order preservation.
