<script lang="ts">
    import TableauDeDocuments from './TableauDeDocuments.svelte';


    import {type Documents, type Document, documentsStore} from "./store/documents.store";

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

    import { SvelteMap } from 'svelte/reactivity';

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

        return Array.from(documentsConsolides.values()).sort((a, b) => a.nom.localeCompare(b.nom));
    });
</script>


<section class="space-y-8">
    <div>
        <div class="bg-white shadow-sm border border-gray-200 overflow-hidden">
            {#if documents}
                <TableauDeDocuments documents={documentsConsolides} />
            {:else}
                <div class="p-6 text-center text-gray-500 italic">
                    Chargement des documents...
                </div>
            {/if}
        </div>
    </div>
</section>