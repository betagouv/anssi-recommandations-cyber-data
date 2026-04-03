import uvicorn

from configuration import recupere_configuration
from serveur import fabrique_serveur

configuration = recupere_configuration()
serveur = fabrique_serveur(configuration.mqc_data.max_requetes_par_minute)

if __name__ == "__main__":
    HOST = configuration.mqc_data.hote
    PORT = configuration.mqc_data.port
    uvicorn.run(
        "main:serveur",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info",
    )
