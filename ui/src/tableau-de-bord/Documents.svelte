<script lang="ts">
    import TableauDeDocuments from './TableauDeDocuments.svelte';


    import {type Documents, documentsStore} from "./store/documents.store";

    interface Props {
        offsetIndexation: number;
        offsetJeopardy: number;
    }

    const {offsetIndexation, offsetJeopardy}: Props = $props()
    let documents: Documents | undefined = $state(undefined)

    $effect(() => {
        documentsStore.recupereDocuments(offsetIndexation, offsetJeopardy).then(data => documents = data)
    })

    $effect(() => {
        if (documents) {
            documentsStore.initialise(documents)
        }
    })

    type Tabulation = "collection-indexee" | "collection-jeopardy";

    let activeTab = $state<Tabulation>("collection-indexee");
</script>


<div class="mb-8 border-b border-gray-200">
    <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
                onclick={() => activeTab = 'collection-indexee'}
                class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm {activeTab === 'collection-indexee' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
        >
            Collection indexée
        </button>
        <button
                onclick={() => activeTab = 'collection-jeopardy'}
                class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm {activeTab === 'collection-jeopardy' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
        >
            Collection Jeopardy
        </button>
    </nav>
</div>
<section class="space-y-8">
    {#if activeTab === 'collection-indexee'}
        <div>
            <div class="bg-white shadow-sm border border-gray-200 overflow-hidden">
                {#if documents}
                    <TableauDeDocuments documents={documents.indexee} />
                {:else}
                    <div class="p-6 text-center text-gray-500 italic">
                        Chargement des documents...
                    </div>
                {/if}
            </div>
        </div>
    {:else if activeTab === 'collection-jeopardy'}
        <div class="bg-white shadow-sm border border-gray-200">
            {#if documents}
                <TableauDeDocuments documents={documents.jeopardy} />
            {:else}
                <div class="p-6 text-center text-gray-500 italic">
                    Chargement des documents...
                </div>
            {/if}
        </div>
    {/if}
</section>