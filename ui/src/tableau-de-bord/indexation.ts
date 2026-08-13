export type DocumentPartiel = {
  document: string;
  id: string;
  pages_non_indexees: number[];
  erreurs: string[];
};

export const messageResultatIndexation = (
  erreurs: { document: string; detail: string }[],
  documentsPartiels: DocumentPartiel[],
): string => {
  if (erreurs.length > 0) return 'L’indexation est terminée avec des erreurs.';
  if (documentsPartiels.length > 0) return 'L’indexation est terminée partiellement.';
  return 'Tous les documents ont été indexés avec succès.';
};
