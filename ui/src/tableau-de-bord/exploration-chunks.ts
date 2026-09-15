export type Chunk = {
  id: string;
  contenu: string;
  metadonnees: Record<string, unknown>;
};

type ReponseHTTP = {
  ok: boolean;
  json: () => Promise<{ chunks: Chunk[] }>;
};

type EffectueRequete = (url: string, options: RequestInit) => Promise<ReponseHTTP>;

export const apercuDuContenu = (contenu: string): string =>
  contenu.length <= 200
    ? contenu
    : `${contenu.slice(0, 100)}...${contenu.slice(-100)}`;

export const recupereLesChunks = async (
  idDocument: string,
  effectueRequete: EffectueRequete = fetch
): Promise<Chunk[]> => {
  const reponse = await effectueRequete(`/api/documents/${idDocument}/chunks`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!reponse.ok) {
    throw new Error('Impossible de récupérer les chunks.');
  }
  const contenu = await reponse.json();

  return contenu.chunks;
};
