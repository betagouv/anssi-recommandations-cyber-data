import { describe, expect, it } from 'vitest';

import { creeRequeteJeopardyDocument } from './jeopardy-document';

describe('creeRequeteJeopardyDocument', () => {
  it('cible la collection Jeopardy choisie avec le document source sélectionné', () => {
    expect(
      creeRequeteJeopardyDocument('collection-source', 'collection-jeopardy', 'doc-2.pdf'),
    ).toEqual({
      url: '/api/jeopardy/collection-jeopardy/documents',
      body: { documents: ['doc-2.pdf'], identifiant_collection: 'collection-source' },
    });
  });
});
