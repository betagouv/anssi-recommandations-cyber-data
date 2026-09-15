import { describe, expect, it } from 'vitest';

import { apercuDuContenu, recupereLesChunks } from './exploration-chunks';

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
