<script lang="ts">

    let fichiersAAjouter = $state<string>("");
    let fichiersAModifier = $state<string>("");
    let fichiersASupprimer = $state<string>("");
    let reponseMiseAJourDocuments = $state<string | undefined>(undefined);


    const metsAJourLaCollection = async () => {

        const recupereLesFichiers = (fichiers: string): string[] => (fichiers.trim().length > 0 ? fichiers.split(",") : []).map(f => f.trim());

        const fichiersAjoutes = recupereLesFichiers(fichiersAAjouter);
        const fichiersModifies = recupereLesFichiers(fichiersAModifier);
        const fichiersSupprimes = recupereLesFichiers(fichiersASupprimer);
        const reponse = await fetch("/api/documents/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                fichiers_ajoutes: fichiersAjoutes,
                fichiers_modifies: fichiersModifies,
                fichiers_supprimes: fichiersSupprimes
            })
        });

        const contenuReponse = await reponse.json();
        reponseMiseAJourDocuments = contenuReponse.message;
    }
</script>

<div class="space-y-6">
    <div class="border-b border-gray-100 pb-2">
        <h4 class="text-lg font-medium text-gray-800">Modifier une collection</h4>
    </div>

    <section class="grid gap-6">
        <div class="flex flex-col gap-1.5">
            <label for="fichiers-a-ajouter" class="text-sm font-medium text-gray-700">Fichiers à ajouter :</label>
            <textarea id="fichiers-a-ajouter" rows="2" name="fichiers-a-ajouter"
                      bind:value={fichiersAAjouter} placeholder="fichiers1.pdf, fichier2.pdf..."
                      class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-y"></textarea>
        </div>

        <div class="flex flex-col gap-1.5">
            <label for="fichiers-a-modifier" class="text-sm font-medium text-gray-700">Fichiers à modifier :</label>
            <textarea id="fichiers-a-modifier" rows="2" name="fichiers-a-modifier"
                      bind:value={fichiersAModifier} placeholder="fichiers1.pdf, fichier2.pdf..."
                      class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-y"></textarea>
        </div>

        <div class="flex flex-col gap-1.5">
            <label for="fichiers-a-supprimer" class="text-sm font-medium text-gray-700 text-red-700">Fichiers à
                supprimer :</label>
            <textarea id="fichiers-a-supprimer" rows="2" name="fichiers-a-supprimer"
                      bind:value={fichiersASupprimer} placeholder="fichiers1.pdf, fichier2.pdf..."
                      class="w-full px-3 py-2 bg-white border border-red-200 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors resize-y"></textarea>
        </div>

        <div class="pt-2">
            <button type="button" onclick={metsAJourLaCollection}
                    class="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-300 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
                Mettre à jour les documents
            </button>
        </div>

        {#if reponseMiseAJourDocuments}
            <div class="mt-4 p-4 bg-blue-50 text-blue-700 rounded-lg border border-blue-100 flex items-center animate-in fade-in slide-in-from-top-2">
                <svg class="w-5 h-5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd"
                          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                          clip-rule="evenodd"/>
                </svg>
                <p class="text-sm">{reponseMiseAJourDocuments}</p>
            </div>
        {/if}
    </section>
</div>