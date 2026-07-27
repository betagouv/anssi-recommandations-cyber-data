import { writable } from 'svelte/store';

export type Document = {
  id: string;
  nom: string;
  date_de_creation: Date;
  chunks: number;
};

export type Documents = {
  indexee: Document[];
  jeopardy: Document[];
};

const recupereDocuments = async (
  nombreDocumentsIndexes: number,
  nombreDocumentsJeopardy: number,
  idCollectionIndexee?: string,
  idCollectionJeopardy?: string
): Promise<Documents> => {
  const params = new URLSearchParams({
    indexee: String(nombreDocumentsIndexes),
    jeopardy: String(nombreDocumentsJeopardy),
  });
  if (idCollectionIndexee) params.set('id_collection_indexee', idCollectionIndexee);
  if (idCollectionJeopardy) params.set('id_collection_jeopardy', idCollectionJeopardy);

  const reponse = await fetch(`/api/documents/?${params.toString()}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  const documents = await reponse.json();
  documents.indexee.sort((a: Document, b: Document) =>
    b.nom.toLowerCase() > a.nom.toLowerCase() ? -1 : 1
  );
  documents.jeopardy.sort((a: Document, b: Document) =>
    b.nom.toLowerCase() > a.nom.toLowerCase() ? -1 : 1
  );
  return documents;
};

const { subscribe, set } = writable<Documents>();

export const documentsStore = { subscribe, initialise: set, recupereDocuments };
