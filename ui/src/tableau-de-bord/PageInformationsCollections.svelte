<script lang="ts">
    import Collections from './Collections.svelte';
    import Documents from './Documents.svelte';
    import { collectionStore } from './store/collection.store';


    let offsetIndexation = $state(0);
    let offsetJeopardy = $state(0);

    $effect(() => {
        offsetIndexation = $collectionStore.indexee.nombre_documents;
        offsetJeopardy = $collectionStore.jeopardy.nombre_documents;
    });

</script>
<div class="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
          <h4 class="text-xl font-semibold text-gray-700 mb-4">
            Informations collections
          </h4>
          <div class="grid gap-8">
            <Collections collections={$collectionStore} />

            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <Documents {offsetIndexation} {offsetJeopardy} />
            </div>
          </div>
        </div>