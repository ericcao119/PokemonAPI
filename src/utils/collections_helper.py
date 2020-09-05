from typing import List

import google.cloud.firestore_v1.client

from src.data.ability import Ability


def chunk_write(
    database: google.cloud.firestore_v1.client.Client,
    collection: str,
    iterable: List[Ability],
) -> None:
    """Executes a single batch write over an iterable
    TODO: Parameterize the function
    TODO: Assert on size of iterable
    """
    batch = database.batch()

    for ability in iterable:
        ref = database.collection(collection).document(ability.name)
        batch.set(ref, ability._asdict())

    batch.commit()
