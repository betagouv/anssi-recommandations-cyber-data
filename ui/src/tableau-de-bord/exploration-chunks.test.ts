import { describe, expect, it } from 'vitest';

import {
  apercuDuContenu,
  construitUrlDeSource,
  informationsDeSource,
  recupereLesChunks,
  separeLesMetadonneesDeSource,
} from './exploration-chunks';

describe('aperçu du contenu d’un chunk', () => {
  it('conserve le contenu qui ne dépasse pas deux cents caractères', () => {
    const contenu = 'Contenu court';

    expect(apercuDuContenu(contenu)).toBe(contenu);
  });

  it('montre le début et la fin du contenu trop long', () => {
    const contenu = `${'a'.repeat(100)}milieu${'z'.repeat(100)}`;

    expect(apercuDuContenu(contenu)).toBe(`${'a'.repeat(100)}...${'z'.repeat(100)}`);
  });

  it('récupère les chunks du document demandé', async () => {
    const effectueRequete = async () => ({
      ok: true,
      json: async () => ({
        chunks: [
          {
            id: 'chunk-1',
            contenu: 'Un contenu',
            contexte_documentaire: 'Document : guide test\nSections : Introduction',
            metadonnees: { page: 3 },
          },
        ],
      }),
    });

    const resultat = await recupereLesChunks('document-42', effectueRequete);

    expect(resultat).toEqual([
      {
        id: 'chunk-1',
        contenu: 'Un contenu',
        contexte_documentaire: 'Document : guide test\nSections : Introduction',
        metadonnees: { page: 3 },
      },
    ]);
  });

  it('signale une erreur lorsque la récupération échoue', async () => {
    const effectueRequete = async () => ({
      ok: false,
      json: async () => ({ chunks: [] }),
    });

    await expect(recupereLesChunks('document-42', effectueRequete)).rejects.toThrow(
      'Impossible de récupérer les chunks.'
    );
  });
});

describe('métadonnées de source', () => {
  it('sépare la source et la page des autres métadonnées', () => {
    const metadonnees = {
      source_url: 'https://example.test/guide.pdf',
      page: 7,
      nom_document: 'guide.pdf',
      position_page: 3,
    };

    expect(separeLesMetadonneesDeSource(metadonnees)).toEqual({
      sourceUrl: 'https://example.test/guide.pdf',
      page: 7,
      metadonnees: {
        nom_document: 'guide.pdf',
        position_page: 3,
      },
    });
  });

  it('construit une URL qui ouvre la page demandée', () => {
    expect(construitUrlDeSource('https://example.test/guide.pdf#sommaire', 7)).toBe(
      'https://example.test/guide.pdf#page=7'
    );
  });

  it.each([
    [
      'https://example.test/guide.pdf',
      undefined,
      {
        libelle: 'https://example.test/guide.pdf',
        url: 'https://example.test/guide.pdf',
      },
    ],
    [undefined, 7, { libelle: 'Page 7' }],
    [undefined, undefined, { libelle: '—' }],
  ])('affiche l’information de source disponible', (sourceUrl, page, attendu) => {
    expect(informationsDeSource(sourceUrl, page)).toEqual(attendu);
  });
});
