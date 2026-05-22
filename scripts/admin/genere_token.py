import argparse
import os
from datetime import datetime, timedelta, timezone

import jwt


def genere_token():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nom", required=True, help="Nom du token")
    parser.add_argument(
        "--duree", required=True, help="Durée de validité du token (par défaut en heures)"
    )
    parser.add_argument(
        "--jours",
        action="store_true",
        help="Pour porter la durée de validité du token en jours",
    )
    args = parser.parse_args()

    clef_jwt = os.getenv("SECRET_JWT", "")

    duree_du_token = _duree_du_token(float(args.duree), args.jours)

    payload = {
        "name": args.nom,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + duree_du_token,
    }

    token = jwt.encode(
        payload,
        clef_jwt,
        algorithm="HS256",
    )

    print(token)


def _duree_du_token(duree: float, est_en_jours: bool) -> timedelta:
    duree_token = timedelta(hours=duree)
    if est_en_jours:
        duree_token = timedelta(days=duree)
    return duree_token


if __name__ == "__main__":
    genere_token()