import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('secrets/firebase/pokemonscraper-9c2c5-dc3b53ea45be.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

