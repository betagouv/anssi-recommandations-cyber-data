<script lang="ts">
    import TableauDeDocuments from './TableauDeDocuments.svelte';
    import { SvelteMap } from 'svelte/reactivity';
    import {type Documents, type Document, documentsStore} from "./store/documents.store";

    interface Props {
        offsetIndexation: number;
        offsetJeopardy: number;
    }

    const {offsetIndexation, offsetJeopardy}: Props = $props()

    let documents: Documents | undefined = $state(undefined)
    let filtreNom = $state("");

    $effect(() => {
        documentsStore.recupereDocuments(offsetIndexation, offsetJeopardy).then(data => documents = data)

    })

    $effect(() => {
        if (documents) {
            documentsStore.initialise(documents)
        }

    })

    type DocumentConsolide = {
        nom: string;
        indexee?: Document;
        jeopardy?: Document;
    }

    let documentsConsolides = $derived.by(() => {
        if (!documents) return [];

        const documentsConsolides = new SvelteMap<string, DocumentConsolide>();

        documents.indexee.forEach(doc => {
            documentsConsolides.set(doc.nom, { nom: doc.nom, indexee: doc });
        });

        documents.jeopardy.forEach(doc => {
            const existant = documentsConsolides.get(doc.nom);
            if (existant) {
                existant.jeopardy = doc;
            } else {
                documentsConsolides.set(doc.nom, { nom: doc.nom, jeopardy: doc });
            }
        });

        let result = Array.from(documentsConsolides.values());

        if (filtreNom.trim() !== "") {
            const search = filtreNom.toLowerCase();
            result = result.filter(doc => doc.nom.toLowerCase().includes(search));
        }

        return result.sort((a, b) => a.nom.localeCompare(b.nom));
    });
</script>


<section class="space-y-6">
    <div class="flex items-center space-x-4">
        <div class="relative flex-1 max-w-md">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
            </div>
            <input
                type="text"
                bind:value={filtreNom}
                placeholder="Filtrer par nom de document..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors"
            />
        </div>
        {#if filtreNom}
            <button
                onclick={() => filtreNom = ""}
                class="text-sm text-gray-500 hover:text-gray-700 font-medium"
            >
                Effacer
            </button>
        {/if}
    </div>

    <div>
        <div class="bg-white shadow-sm border border-gray-200 overflow-hidden rounded-lg">
            {#if documents}
                {#if documentsConsolides.length > 0}
                    <TableauDeDocuments documents={documentsConsolides} />
                {:else}
                    <div class="p-12 text-center">
                        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <h3 class="mt-2 text-sm font-medium text-gray-900">Aucun document trouvé</h3>
                        <p class="mt-1 text-sm text-gray-500">Aucun document ne correspond à votre recherche "{filtreNom}".</p>
                        <div class="mt-6">
                            <button
                                type="button"
                                onclick={() => filtreNom = ""}
                                class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Effacer la recherche
                            </button>
                        </div>
                    </div>
                {/if}
            {:else}
                <div class="p-6 text-center text-gray-500 italic">
                    Chargement des documents...
                </div>
            {/if}
        </div>
    </div>
</section>