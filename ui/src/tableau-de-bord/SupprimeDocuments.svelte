<script lang="ts">
    let documentsASupprimer = $state<string>("");
    let reponseSuppressionDocuments = $state<string | undefined>(undefined);

    const supprimeLesDocuments = async () => {
        const reponse = await fetch(`/api/documents/supprimer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                documents: documentsASupprimer.split(",").map(document => document.trim())
            })
        });


        const contenuReponse = await reponse.json();
        reponseSuppressionDocuments = contenuReponse.message;
    }
</script>

<div class="space-y-6">
    <div class="border-b border-gray-100 pb-2">
        <h4 class="text-lg font-medium text-gray-800">Supprime les documents indexés</h4>
    </div>

    <section class="grid gap-4">
        <div class="flex flex-col gap-1.5">
            <label for="id-collection" class="text-sm font-medium text-gray-700">Identifiant des documents à supprimer :</label>
            <textarea id="documents-a-supprimer" rows="2" name="documents-a-supprimer"
                      bind:value={documentsASupprimer} placeholder="ID1, ID2..."
                      class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-y"></textarea>
        </div>

        <div class="pt-2">
            <button type="button" onclick={supprimeLesDocuments}
                    class="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-300 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
                Supprime les documents
            </button>
        </div>

        {#if reponseSuppressionDocuments}
            <div class="mt-4 p-4 bg-blue-50 text-blue-700 rounded-lg border border-blue-100 flex items-center animate-in fade-in slide-in-from-top-2">
                <svg class="w-5 h-5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd"
                          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                          clip-rule="evenodd"/>
                </svg>
                <p class="text-sm">{reponseSuppressionDocuments}</p>
            </div>
        {/if}

    </section>
</div>