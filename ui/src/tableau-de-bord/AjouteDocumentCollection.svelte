<script lang="ts">
  import {
    messageResultatIndexation,
    type DocumentPartiel,
  } from './indexation';
  import SelecteurCollection from './SelecteurCollection.svelte';
  import { collectionStore } from './store/collection.store';
  import {
    creeRequeteJeopardyDocument,
    recupereDocumentsDuneCollection,
    type DocumentCollection,
  } from './jeopardy-document';

  let idCollectionIndexee = $state('');
  let idCollectionJeopardy = $state('');
  let documentAJeopardyser = $state('');
  let documentsCollection = $state<DocumentCollection[]>([]);
  let reponseJeopardy = $state<string | undefined>(undefined);
  let fichiersAAjouter = $state<string>('');
  let urlAAjouter = $state<string>('');
  let fichiersAModifier = $state<string>('');
  let fichiersASupprimer = $state<string>('');
  let reponseMiseAJourDocuments = $state<string | undefined>(undefined);
  let indexationEnCours = $state(false);
  let erreursIndexation = $state<{ document: string; detail: string }[]>([]);
  let documentsPartiels = $state<DocumentPartiel[]>([]);

  const detailErreurApi = (detail: unknown, statut: number) => {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((erreur) =>
          typeof erreur === 'object' && erreur !== null && 'msg' in erreur
            ? String(erreur.msg)
            : JSON.stringify(erreur),
        )
        .join('; ');
    }
    return `Erreur HTTP ${statut}`;
  };

  $effect(() => {
    if (!idCollectionIndexee && $collectionStore?.indexee.id) {
      idCollectionIndexee = String($collectionStore.indexee.id);
    }
    if (!idCollectionJeopardy && $collectionStore?.jeopardy.id) {
      idCollectionJeopardy = String($collectionStore.jeopardy.id);
    }
  });

  $effect(() => {
    const idCollection = idCollectionIndexee;
    documentAJeopardyser = '';
    if (!idCollection) {
      documentsCollection = [];
      return;
    }

    recupereDocumentsDuneCollection(idCollection)
      .then((documents) => {
        if (idCollectionIndexee === idCollection) documentsCollection = documents;
      })
      .catch(() => {
        if (idCollectionIndexee === idCollection) documentsCollection = [];
      });
  });

  const attendsTrenteSecondes = () =>
    new Promise((resolve) => {
      setTimeout(resolve, 30_000);
    });

  const suitLIndexation = async (identifiantOperation: string) => {
    let statutIndexation = 'en_cours';

    while (statutIndexation === 'en_cours') {
      await attendsTrenteSecondes();
      const reponseStatut = await fetch(
        `/api/documents/indexation/${identifiantOperation}`,
      );
      const contenuStatut = await reponseStatut.json();

      if (!reponseStatut.ok) {
        indexationEnCours = false;
        erreursIndexation = [
          {
            document: 'suivi de l’indexation',
            detail: detailErreurApi(contenuStatut.detail, reponseStatut.status),
          },
        ];
        reponseMiseAJourDocuments = 'Le suivi de l’indexation a échoué.';
        return;
      }

      statutIndexation = contenuStatut.statut;

      if (statutIndexation !== 'en_cours') {
        erreursIndexation = contenuStatut.erreurs ?? [];
        documentsPartiels = contenuStatut.documents_partiels ?? [];
        indexationEnCours = false;
        reponseMiseAJourDocuments = messageResultatIndexation(
          erreursIndexation,
          documentsPartiels,
        );
      }
    }
  };

  const metsAJourLaCollection = async () => {
    const recupereLesFichiers = (fichiers: string): string[] =>
      (fichiers.trim().length > 0 ? fichiers.split(',') : []).map((f) => f.trim());

    const fichiersAjoutes = recupereLesFichiers(fichiersAAjouter);
    const fichiersModifies = recupereLesFichiers(fichiersAModifier);
    const fichiersSupprimes = recupereLesFichiers(fichiersASupprimer);
    const reponse = await fetch('/api/documents/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        fichiers_ajoutes: fichiersAjoutes,
        fichiers_modifies: fichiersModifies,
        fichiers_supprimes: fichiersSupprimes,
        url_a_ajouter: urlAAjouter.trim() || null,
        id_collection_indexee: idCollectionIndexee
          ? String(idCollectionIndexee)
          : null,
        id_collection_jeopardy: idCollectionJeopardy
          ? String(idCollectionJeopardy)
          : null,
      }),
    });

    const contenuReponse = await reponse.json();

    if (!reponse.ok) {
      const detail = detailErreurApi(contenuReponse.detail, reponse.status);
      reponseMiseAJourDocuments = 'La mise à jour des documents a échoué.';
      erreursIndexation = [{ document: 'requête', detail }];
      indexationEnCours = false;
      return;
    }

    if (typeof contenuReponse.identifiant_operation !== 'string') {
      reponseMiseAJourDocuments =
        'La mise à jour des documents a échoué : identifiant de suivi absent.';
      erreursIndexation = [
        { document: 'requête', detail: 'Réponse API invalide.' },
      ];
      indexationEnCours = false;
      return;
    }

    reponseMiseAJourDocuments = contenuReponse.message;
    erreursIndexation = [];
    documentsPartiels = [];
    indexationEnCours = true;
    await suitLIndexation(contenuReponse.identifiant_operation);
  };

  const jeopardyseLeDocument = async () => {
    if (!idCollectionIndexee || !idCollectionJeopardy || !documentAJeopardyser) return;

    const requete = creeRequeteJeopardyDocument(
      idCollectionIndexee,
      idCollectionJeopardy,
      documentAJeopardyser,
    );
    const reponse = await fetch(requete.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requete.body),
    });
    reponseJeopardy = (await reponse.json()).message;
  };
</script>

<div class="space-y-6">
  <div class="border-b border-gray-100 pb-2">
    <h4 class="text-lg font-medium text-gray-800">Modifier une collection</h4>
  </div>

  <section class="grid gap-6">
    <div class="flex flex-wrap gap-4">
      <div class="flex min-w-72 flex-1 flex-col gap-1.5">
        <label for="id-collection-indexee" class="text-sm font-medium text-gray-700"
          >Collection à modifier :</label
        >
        <SelecteurCollection bind:value={idCollectionIndexee} exclutJeopardy />
      </div>

      <div class="flex min-w-72 flex-1 flex-col gap-1.5">
        <label for="id-collection-jeopardy" class="text-sm font-medium text-gray-700"
          >Collection Jeopardy :</label
        >
        <SelecteurCollection bind:value={idCollectionJeopardy} uniquementJeopardy />
        {#if !idCollectionJeopardy}
          <p class="text-sm text-red-700">Sélectionnez une collection Jeopardy cible.</p>
        {/if}
      </div>
    </div>

    <div class="flex flex-col gap-1.5">
      <label for="fichiers-a-ajouter" class="text-sm font-medium text-gray-700"
        >Fichiers à ajouter :</label
      >
      <textarea
        id="fichiers-a-ajouter"
        rows="2"
        name="fichiers-a-ajouter"
        bind:value={fichiersAAjouter}
        placeholder="fichiers1.pdf, fichier2.pdf..."
        class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-y"
      ></textarea>
    </div>

    <div class="flex flex-col gap-1.5">
      <label for="url-a-ajouter" class="text-sm font-medium text-gray-700"
        >URL du document à ajouter :</label
      >
      <input
        type="url"
        id="url-a-ajouter"
        name="url-a-ajouter"
        bind:value={urlAAjouter}
        placeholder="https://cyber.gouv.fr/cyberdico/"
        class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
      />
    </div>

    <div class="flex flex-col gap-1.5">
      <label for="fichiers-a-modifier" class="text-sm font-medium text-gray-700"
        >Fichiers à modifier :</label
      >
      <textarea
        id="fichiers-a-modifier"
        rows="2"
        name="fichiers-a-modifier"
        bind:value={fichiersAModifier}
        placeholder="fichiers1.pdf, fichier2.pdf..."
        class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-y"
      ></textarea>
    </div>

    <div class="flex flex-col gap-1.5">
      <label
        for="fichiers-a-supprimer"
        class="text-sm font-medium text-gray-700 text-red-700"
        >Fichiers à supprimer :</label
      >
      <textarea
        id="fichiers-a-supprimer"
        rows="2"
        name="fichiers-a-supprimer"
        bind:value={fichiersASupprimer}
        placeholder="fichiers1.pdf, fichier2.pdf..."
        class="w-full px-3 py-2 bg-white border border-red-200 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors resize-y"
      ></textarea>
    </div>

    <div class="pt-2">
      <button
        type="button"
        onclick={metsAJourLaCollection}
        disabled={!idCollectionIndexee || !idCollectionJeopardy || indexationEnCours}
        class="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-300 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Mettre à jour les documents
      </button>
    </div>

    <div class="rounded-lg border border-violet-200 bg-violet-50 p-4">
      <h5 class="mb-3 text-base font-medium text-violet-900">Jeopardyser un document</h5>
      <div class="flex flex-wrap items-end gap-4">
        <div class="flex min-w-72 flex-1 flex-col gap-1.5">
          <label for="document-a-jeopardyser" class="text-sm font-medium text-gray-700"
            >Document de la collection source :</label
          >
          <select
            id="document-a-jeopardyser"
            bind:value={documentAJeopardyser}
            disabled={!idCollectionIndexee || !idCollectionJeopardy}
            class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 shadow-sm transition-colors focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <option value="" disabled selected>Sélectionner un document</option>
            {#each documentsCollection as document (document.id)}
              <option value={document.nom}>{document.nom}</option>
            {/each}
          </select>
        </div>

        <button
          type="button"
          onclick={jeopardyseLeDocument}
          disabled={!idCollectionIndexee || !idCollectionJeopardy || !documentAJeopardyser}
          class="px-6 py-2.5 font-semibold text-white transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50 bg-violet-600 rounded-lg shadow-md hover:bg-violet-700 focus:ring-4 focus:ring-violet-300 active:scale-95"
        >
          Jeopardyser le document
        </button>
      </div>

      {#if reponseJeopardy}
        <p class="mt-3 text-sm text-violet-800">{reponseJeopardy}</p>
      {/if}
    </div>

    {#if reponseMiseAJourDocuments && indexationEnCours}
      <div
        class="mt-4 p-4 bg-blue-50 text-blue-700 rounded-lg border border-blue-100 flex items-center animate-in fade-in slide-in-from-top-2"
      >
        <svg
          class="w-5 h-5 mr-3 flex-shrink-0"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
            clip-rule="evenodd"
          />
        </svg>
        <p class="text-sm">{reponseMiseAJourDocuments}</p>
      </div>
    {/if}

    {#if
      reponseMiseAJourDocuments &&
      !indexationEnCours &&
      erreursIndexation.length === 0 &&
      documentsPartiels.length === 0
    }
      <div
        class="mt-4 p-4 bg-blue-50 text-blue-700 rounded-lg border border-blue-100 flex items-center animate-in fade-in slide-in-from-top-2"
      >
        <p class="text-sm">{reponseMiseAJourDocuments}</p>
      </div>
    {/if}

    {#if !indexationEnCours && documentsPartiels.length > 0}
      <div
        class="mt-4 p-4 bg-amber-50 text-amber-800 rounded-lg border border-amber-200 animate-in fade-in slide-in-from-top-2"
      >
        <p class="text-sm font-medium">{reponseMiseAJourDocuments}</p>
        <ul class="mt-2 list-disc list-inside text-sm">
          {#each documentsPartiels as documentPartiel (documentPartiel.id)}
            <li>
              <strong>{documentPartiel.document}</strong> — pages non indexées :
              {documentPartiel.pages_non_indexees.join(', ')}
              {#if documentPartiel.erreurs.length > 0}
                <ul class="ml-5 list-disc">
                  {#each documentPartiel.erreurs as erreur}
                    <li>{erreur}</li>
                  {/each}
                </ul>
              {/if}
            </li>
          {/each}
        </ul>
      </div>
    {/if}

    {#if !indexationEnCours && erreursIndexation.length > 0}
      <div
        class="mt-4 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 animate-in fade-in slide-in-from-top-2"
      >
        <p class="text-sm font-medium">{reponseMiseAJourDocuments}</p>
        <ul class="mt-2 list-disc list-inside text-sm">
          {#each erreursIndexation as erreur (erreur.document)}
            <li><strong>{erreur.document}</strong> : {erreur.detail}</li>
          {/each}
        </ul>
      </div>
    {/if}
  </section>
</div>
