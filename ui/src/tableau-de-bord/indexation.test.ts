import { describe, expect, it } from 'vitest';
import { messageResultatIndexation } from './indexation';

describe('message du résultat d’indexation', () => {
  it('distingue une indexation partielle d’un succès', () => {
    expect(
      messageResultatIndexation([], [
        { document: 'guide.pdf', id: '1', pages_non_indexees: [18], erreurs: ['JSON invalide'] },
      ]),
    ).toBe('L’indexation est terminée partiellement.');
  });

  it('priorise les erreurs globales', () => {
    expect(
      messageResultatIndexation([{ document: 'guide.pdf', detail: 'échec' }], []),
    ).toBe('L’indexation est terminée avec des erreurs.');
  });
});
