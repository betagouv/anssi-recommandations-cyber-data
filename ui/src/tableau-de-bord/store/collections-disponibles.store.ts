import { writable } from 'svelte/store';

export type CollectionDisponible = {
  id: string;
  nom: string;
  date_de_creation: Date;
};

const recupereCollectionsDisponibles = async (): Promise<CollectionDisponible[]> => {
  const reponse = await fetch('/api/collections/disponibles', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  const { collections } = await reponse.json();
  return collections;
};

const { subscribe, set } = writable<CollectionDisponible[]>();

export const collectionsDisponiblesStore = {
  subscribe,
  initialise: set,
  recupereCollectionsDisponibles,
};