from argparse import ArgumentParser


def main() -> None:
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument(
        "--id-experience", required=True, type=str, help="Id de l’expérience en cours"
    )
    args = p.parse_args()
    contenu = args.id_experience

    print(contenu)


if __name__ == "__main__":
    main()
