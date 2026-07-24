import { writable } from 'svelte/store';

type Collection = {
  id: string;
  nom: string;
  description: string;
  nombre_documents: number;
  date_de_creation: Date;
  date_de_derniere_modification: Date;
};

export type Collections = {
  indexee: Collection;
  jeopardy: Collection;
};

const recupereCollections = async (idIndexee?: string, idJeopardy?: string) => {
  const params = new URLSearchParams();
  if (idIndexee) params.set('id_collection_indexee', idIndexee);
  if (idJeopardy) params.set('id_collection_jeopardy', idJeopardy);
  const query = params.toString();

  const reponse = await fetch(`/api/collections/${query ? `?${query}` : ''}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  return await reponse.json();
};

const { subscribe, set } = writable<Collections>();

const collections = await recupereCollections();

set(collections);

export const collectionStore = { subscribe, initialise: set, recupereCollections };
