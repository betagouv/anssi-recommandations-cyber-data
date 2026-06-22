<script lang="ts">
    import {collectionStore} from "./store/collection.store";

    const formaterDate = (date: Date | string) => {
        if (!date) return "";
        return new Date(date).toLocaleDateString("fr-FR", {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
</script>


{#if $collectionStore}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        {#each ['indexee', 'jeopardy'] as key (key)}
            {@const collection = $collectionStore[key]}
            {#if collection}
                <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col">
                    <h2 class="text-lg font-bold text-gray-900 mb-2">{collection.nom} <span class="text-sm font-normal text-gray-500">(id : {collection.id})</span></h2>
                    <p class="text-gray-600 mb-4 flex-grow">{collection.description}</p>
                    <p class="text-gray-900 mb-4"><strong class="font-bold">{collection.nombre_documents}</strong> documents</p>
                    <div class="mt-auto pt-4 border-t border-gray-100 text-xs text-gray-500 space-y-1">
                        <p>Créé le : {formaterDate(collection.date_de_creation)}</p>
                        <p>Dernière modification : {formaterDate(collection.date_de_derniere_modification)}</p>
                    </div>
                </section>
            {/if}
        {/each}
    </div>
{:else}
    <p class="text-gray-500 italic">Chargement des collections...</p>
{/if}