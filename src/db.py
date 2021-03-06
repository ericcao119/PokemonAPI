"""Basic database setup"""

import os
import sqlite3

# import mock
import unittest.mock

import google.auth.credentials
from flask import Flask, render_template, request
from google.cloud import firestore


def create_sqlite_connection(path):
    connection = None

    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

    return connection


def create_db():
    """"""
    if os.getenv("GAE_ENV", "").startswith("standard"):
        # production
        print("HI")
        db = firestore.Client()
    else:
        # localhost
        os.environ["FIRESTORE_DATASET"] = "test"
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        os.environ["FIRESTORE_EMULATOR_HOST_PATH"] = "localhost:8080/firestore"
        os.environ["FIRESTORE_HOST"] = "http://localhost:8080"
        os.environ["FIRESTORE_PROJECT_ID"] = "test"

        credentials = unittest.mock.Mock(spec=google.auth.credentials.Credentials)
        db = firestore.Client(project="test", credentials=credentials)

    return db
