import argparse
import os

import requests


def supprime_collection():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="Identifiant de la collection")
    args = parser.parse_args()

    base_url = "https://albert.api.etalab.gouv.fr/v1"
    api_key = os.getenv("ALBERT_CLE_API")
    session = requests.session()
    session.headers = {"Authorization": f"Bearer {api_key}"}

    reponse = session.delete(f"{base_url}/collections/{args.id}")
    print(f"Réponse de la suppression : {reponse.text}")


if __name__ == "__main__":
    supprime_collection()
