import requests
from openai import OpenAI
from configuration import recupere_configuration


class ClientAlbert:
    def __init__(self, url: str, cle_api: str):
        self.client_openai = OpenAI(base_url=url, api_key=cle_api)
        self.session = requests.session()
        self.session.headers = {"Authorization": f"Bearer {cle_api}"}


def fabrique_client_albert() -> ClientAlbert:
    config = recupere_configuration().albert
    return ClientAlbert(config.url, config.cle_api)


if __name__ == "__main__":
    client = fabrique_client_albert()
    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")
