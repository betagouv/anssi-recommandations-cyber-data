<script lang="ts">
  import {
    apercuDuContenu,
    informationsDeSource,
    recupereLesChunks,
    separeLesMetadonneesDeSource,
    type Chunk,
  } from './exploration-chunks';

  let idDocument = $state('');
  let chunks = $state<Chunk[] | undefined>(undefined);
  let chargement = $state(false);
  let erreur = $state('');

  const afficheLesChunks = async () => {
    const identifiantDocument = idDocument.trim();
    chunks = undefined;
    erreur = '';

    if (!identifiantDocument) {
      erreur = 'Saisissez un identifiant de document.';
      return;
    }

    chargement = true;
    try {
      chunks = await recupereLesChunks(identifiantDocument);
    } catch (erreurDeRecuperation) {
      chunks = [];
      erreur =
        erreurDeRecuperation instanceof Error
          ? erreurDeRecuperation.message
          : 'Impossible de récupérer les chunks.';
    } finally {
      chargement = false;
    }
  };

  const afficheLesMetadonnees = (metadonnees: Record<string, unknown>) =>
    JSON.stringify(metadonnees) ?? '';
</script>

<div class="bg-white p-8 rounded-xl shadow-sm border border-gray-200 space-y-6">
  <div>
    <h4 class="text-xl font-semibold text-gray-700">Exploration de chunks</h4>
    <p class="mt-1 text-sm text-gray-500">
      Consultez les chunks et leurs métadonnées à partir de l’identifiant d’un
      document.
    </p>
  </div>

  <div class="flex flex-wrap items-end gap-4">
    <div class="flex flex-col gap-1.5 min-w-72">
      <label for="id-document-exploration" class="text-sm font-medium text-gray-700">
        Identifiant du document :
      </label>
      <input
        id="id-document-exploration"
        type="text"
        bind:value={idDocument}
        class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
    </div>
    <button
      type="button"
      onclick={afficheLesChunks}
      disabled={chargement}
      class="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
    >
      {chargement ? 'Chargement...' : 'Afficher les chunks'}
    </button>
  </div>

  {#if erreur}
    <p role="alert" class="text-sm text-red-700">{erreur}</p>
  {:else if chargement}
    <p class="text-sm text-gray-500 italic">Chargement des chunks...</p>
  {:else if chunks === undefined}
    <p class="text-sm text-gray-500 italic">
      Saisissez un identifiant de document pour explorer ses chunks.
    </p>
  {:else if chunks.length === 0}
    <p class="text-sm text-gray-500 italic">Aucun chunk trouvé pour ce document.</p>
  {:else}
    <div class="overflow-x-auto border border-gray-200 rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              ID du chunk
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Aperçu
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Source
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Métadonnées
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          {#each chunks as chunk (chunk.id)}
            {@const metadonneesDeSource = separeLesMetadonneesDeSource(
              chunk.metadonnees
            )}
            {@const source = informationsDeSource(
              metadonneesDeSource.sourceUrl,
              metadonneesDeSource.page
            )}
            <tr class="hover:bg-gray-50">
              <td
                class="px-6 py-4 align-top text-sm font-mono text-gray-700 break-all"
              >
                {chunk.id}
              </td>
              <td
                class="px-6 py-4 align-top text-sm text-gray-700 whitespace-pre-wrap break-words min-w-96"
              >
                {apercuDuContenu(chunk.contenu)}
              </td>
              <td
                class="px-6 py-4 align-top text-sm text-gray-700 whitespace-pre-wrap break-all min-w-96"
              >
                {#if source.url}
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    class="text-blue-700 underline hover:text-blue-900"
                    >{source.libelle}</a
                  >
                {:else}
                  {source.libelle}
                {/if}
              </td>
              <td
                class="px-6 py-4 align-top text-sm font-mono text-gray-700 whitespace-pre-wrap break-words min-w-96"
              >
                {afficheLesMetadonnees(metadonneesDeSource.metadonnees)}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
