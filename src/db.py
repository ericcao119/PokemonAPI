"""Basic database setup"""

import os
# import mock
import unittest.mock
from flask import Flask, render_template, request
from google.cloud import firestore
import google.auth.credentials


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