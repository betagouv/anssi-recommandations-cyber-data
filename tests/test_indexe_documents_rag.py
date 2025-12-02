from indexe_documents_rag import ClientAlbert


def test_client_albert_initialise_correctement():
    client = ClientAlbert("https://test.api", "test-key")

    assert isinstance(client, ClientAlbert)
    assert str(client.client_openai.base_url) == "https://test.api"
    assert client.session.headers["Authorization"] == "Bearer test-key"
