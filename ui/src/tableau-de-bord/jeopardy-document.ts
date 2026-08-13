export type RequeteJeopardyDocument = {
  url: string;
  body: {
    documents: string[];
    identifiant_collection: string;
  };
};

export const creeRequeteJeopardyDocument = (
  idCollectionSource: string,
  idCollectionJeopardy: string,
  nomDocument: string,
): RequeteJeopardyDocument => ({
  url: `/api/jeopardy/${idCollectionJeopardy}/documents`,
  body: {
    documents: [nomDocument],
    identifiant_collection: idCollectionSource,
  },
});

export type DocumentCollection = { id: string; nom: string };

export const recupereDocumentsDuneCollection = async (
  idCollection: string,
): Promise<DocumentCollection[]> => {
  const reponse = await fetch(`/api/collections/${idCollection}/documents`);
  const { documents } = await reponse.json();
  return documents;
};
