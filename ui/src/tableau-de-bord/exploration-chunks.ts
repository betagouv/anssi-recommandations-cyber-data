export type Chunk = {
  id: string;
  contenu: string;
  metadonnees: Record<string, unknown>;
};

type MetadonneesDeSource = {
  sourceUrl: string | undefined;
  page: string | number | undefined;
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

export const separeLesMetadonneesDeSource = (
  metadonnees: Record<string, unknown>
): MetadonneesDeSource => {
  const { source_url: sourceUrl, page, ...autresMetadonnees } = metadonnees;

  return {
    sourceUrl: typeof sourceUrl === 'string' ? sourceUrl : undefined,
    page: typeof page === 'string' || typeof page === 'number' ? page : undefined,
    metadonnees: autresMetadonnees,
  };
};

export const construitUrlDeSource = (
  sourceUrl: string,
  page: string | number
): string => {
  const url = new URL(sourceUrl);
  url.hash = `page=${page}`;

  return url.toString();
};

export const informationsDeSource = (
  sourceUrl: string | undefined,
  page: string | number | undefined
): { libelle: string; url?: string } => {
  if (sourceUrl && page !== undefined) {
    const url = construitUrlDeSource(sourceUrl, page);
    return { libelle: url, url };
  }
  if (sourceUrl) {
    return { libelle: sourceUrl, url: sourceUrl };
  }
  if (page !== undefined) {
    return { libelle: `Page ${page}` };
  }

  return { libelle: '—' };
};

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
