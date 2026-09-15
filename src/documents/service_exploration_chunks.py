from adaptateurs.client_albert_chunks import ClientAlbertChunks, ReponseChunkAlbert
from adaptateurs.client_albert_chunks_reel import ClientAlbertChunksReel
from configuration import recupere_configuration


class ServiceExplorationChunks:
    def __init__(self, client_albert: ClientAlbertChunks):
        self.client_albert = client_albert

    def les_chunks_du_document(self, id_document: str) -> list[ReponseChunkAlbert]:
        return self.client_albert.recupere_les_chunks_du_document(id_document)


def fabrique_service_exploration_chunks() -> ServiceExplorationChunks:
    configuration = recupere_configuration().albert
    return ServiceExplorationChunks(
        ClientAlbertChunksReel(configuration.url, configuration.cle_api)
    )
