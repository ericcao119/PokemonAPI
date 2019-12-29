"""Defines database client to connect to Firestore"""

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from config import ROOT_DIR


def get_client():
    """Gets firestore client"""
    cred = credentials.Certificate(
        str(ROOT_DIR/'secrets/firebase/pokemonscraper-9c2c5-dc3b53ea45be.json'))
    firebase_admin.initialize_app(cred)
    database = firestore.client()
    return database
