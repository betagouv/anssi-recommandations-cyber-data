<script lang="ts">

    let nomCollection = $state("");
    let descriptionCollection = $state("");
    let fichiersCollection = $state("");
    let reponseCreationCollection = $state<string | undefined>(undefined);

    const creeCollection = async () => {
        if (nomCollection.trim() === "" || descriptionCollection.trim() === "" || fichiersCollection.trim() === "") return;

        const reponse = await fetch("/api/collections/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({nom: nomCollection, description: descriptionCollection, fichiers: fichiersCollection.split(",").map(f => f.trim())})
        });

        const contenuReponse = await reponse.json();
        reponseCreationCollection = contenuReponse.message;
    }

</script>

<div class="space-y-6">
    <div class="border-b border-gray-100 pb-2">
        <h4 class="text-lg font-medium text-gray-800">Créer une collection</h4>
    </div>
    
    <section class="grid gap-4">
        <div class="flex flex-col gap-1.5">
            <label for="nom-collection" class="text-sm font-medium text-gray-700">Nom de la collection :</label>
            <input type="text" id="nom-collection" name="nom-collection" 
                   bind:value={nomCollection} required
                   class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
        </div>
        
        <div class="flex flex-col gap-1.5">
            <label for="description-collection" class="text-sm font-medium text-gray-700">Description de la collection :</label>
            <input type="text" id="description-collection" name="description-collection" 
                   bind:value={descriptionCollection} required
                   class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
        </div>
        
        <div class="flex flex-col gap-1.5">
            <label for="fichiers-collection" class="text-sm font-medium text-gray-700">Fichiers à ajouter dans la collection :</label>
            <textarea id="fichiers-collection" rows="3" name="fichiers-collection" 
                      bind:value={fichiersCollection} placeholder="Séparer les noms des fichiers par des virgules" required 
                      class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-y"></textarea>
        </div>
        
        <div class="pt-2">
            <button type="button" onclick={creeCollection}
                    class="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
                Créer la collection
            </button>
        </div>
        
        {#if reponseCreationCollection}
            <div class="mt-4 p-4 bg-green-50 text-green-700 rounded-lg border border-green-100 flex items-center animate-in fade-in slide-in-from-top-2">
                <svg class="w-5 h-5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <p class="text-sm">{reponseCreationCollection}</p>
            </div>
        {/if}
    </section>
</div>
