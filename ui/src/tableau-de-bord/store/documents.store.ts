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
  nombreDocumentsJeopardy: number
): Promise<Documents> => {
  const reponse = await fetch(
    `/api/documents/?indexee=${nombreDocumentsIndexes}&jeopardy=${nombreDocumentsJeopardy}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  const documents = await reponse.json();
  documents.indexee.sort((a: Document, b: Document) => b.nom.toLowerCase() > a.nom.toLowerCase() ? -1 : 1);
  documents.jeopardy.sort((a: Document, b: Document) => b.nom.toLowerCase() > a.nom.toLowerCase() ? -1 : 1);
  return documents;
};

const { subscribe, set } = writable<Documents>();

export const documentsStore = { subscribe, initialise: set, recupereDocuments };
