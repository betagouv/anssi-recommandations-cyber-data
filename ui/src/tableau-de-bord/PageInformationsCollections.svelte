<script lang="ts">
  import Collections from './Collections.svelte';
  import Documents from './Documents.svelte';
  import { collectionStore } from './store/collection.store';
  import SelecteurCollection from "./SelecteurCollection.svelte";

  let offsetIndexation = $state(0);
  let offsetJeopardy = $state(0);
  let idCollectionIndexee = $state('');
  let idCollectionJeopardy = $state('');

  $effect(() => {
    offsetIndexation = $collectionStore.indexee.nombre_documents;
    offsetJeopardy = $collectionStore.jeopardy.nombre_documents;
  });

  const afficheCollections = async () => {
    const collections = await collectionStore
            .recupereCollections(idCollectionIndexee, idCollectionJeopardy);
    collectionStore.initialise(collections);
  };
</script>

<div class="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
  <h4 class="text-xl font-semibold text-gray-700 mb-4">Informations collections</h4>
  <div class="grid gap-8">
    <div class="flex flex-wrap items-end gap-4">
      <div class="flex flex-col gap-1.5">
        <label for="id-collection-indexee" class="text-sm font-medium text-gray-700"
          >Identifiant collection indexation :</label
        >
        <SelecteurCollection bind:value={idCollectionIndexee} />
      </div>

      <div class="flex flex-col gap-1.5">
        <label for="id-collection-jeopardy" class="text-sm font-medium text-gray-700"
          >Identifiant collection Jeopardy :</label
        >
        <SelecteurCollection bind:value={idCollectionJeopardy} />
      </div>

      <button
        type="button"
        onclick={afficheCollections}
        class="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 active:scale-95"
      >
        Afficher
      </button>
    </div>

    <Collections collections={$collectionStore} />

    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <Documents
        {offsetIndexation}
        {offsetJeopardy}
        {idCollectionIndexee}
        {idCollectionJeopardy}
      />
    </div>
  </div>
</div>
