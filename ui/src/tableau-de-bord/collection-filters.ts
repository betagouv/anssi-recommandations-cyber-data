import type { CollectionDisponible } from './store/collections-disponibles.store';

export type { CollectionDisponible } from './store/collections-disponibles.store';

const estUneCollectionJeopardy = (collection: CollectionDisponible) =>
  collection.nom.toLocaleLowerCase('fr-FR').includes('jeopardy');

export const filtreCollectionsSource = (collections: CollectionDisponible[]) =>
  collections.filter((collection) => !estUneCollectionJeopardy(collection));

export const filtreCollectionsJeopardy = (collections: CollectionDisponible[]) =>
  collections.filter(estUneCollectionJeopardy);
