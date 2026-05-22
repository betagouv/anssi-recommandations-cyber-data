import datetime
import os

import requests


def get_collections(session, base_url):
    limit = 100
    offset = 0
    visibilite = "private"
    order_by = "created"
    order_direction = "desc"
    response = session.get(
        f"{base_url}/collections?limit={limit}&offset={offset}&order_by={order_by}&order_direction={order_direction}&visibilite={visibilite}"
    )
    response = response.json()
    return response


def affiche_nos_informations_de_collection():
    base_url = "https://albert.api.etalab.gouv.fr/v1"
    api_key = os.getenv("ALBERT_CLE_API")
    session = requests.session()
    session.headers = {"Authorization": f"Bearer {api_key}"}

    reponse = get_collections(session, base_url)
    for collection in reponse["data"]:
        print(f"Id de la collection : {collection['id']}")
        print(f"    Nom de la collection : {collection['name']}")
        print(
            f"    Date de la collection : {datetime.datetime.fromtimestamp(collection['created'])}"
        )
        print("---")


if __name__ == "__main__":
    affiche_nos_informations_de_collection()
