import { describe, expect, it } from 'vitest';

import {
  filtreCollectionsJeopardy,
  filtreCollectionsSource,
  type CollectionDisponible,
} from './collection-filters';

describe('filtreCollectionsSource', () => {
  it('exclut les collections Jeopardy sans tenir compte de la casse', () => {
    const collections: CollectionDisponible[] = [
      { id: '1', nom: 'Guides ANSSI', date_de_creation: new Date() },
      { id: '2', nom: 'JEOPARDY : Guides ANSSI', date_de_creation: new Date() },
      { id: '3', nom: 'jeopardy secondaire', date_de_creation: new Date() },
    ];

    expect(filtreCollectionsSource(collections)).toEqual([collections[0]]);
  });
});

describe('filtreCollectionsJeopardy', () => {
  it('ne conserve que les collections Jeopardy sans tenir compte de la casse', () => {
    const collections: CollectionDisponible[] = [
      { id: '1', nom: 'Guides ANSSI', date_de_creation: new Date() },
      { id: '2', nom: 'JEOPARDY : Guides ANSSI', date_de_creation: new Date() },
    ];

    expect(filtreCollectionsJeopardy(collections)).toEqual([collections[1]]);
  });
});
