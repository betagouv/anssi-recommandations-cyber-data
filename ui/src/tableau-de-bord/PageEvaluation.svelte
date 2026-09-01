<script lang="ts">

    let elementFichierEvaluation: HTMLInputElement | undefined = $state();
    let fichierEvaluation: FileList | undefined = $state();
    let elementFichierMapping: HTMLInputElement | undefined = $state();
    let fichierMapping: FileList | undefined = $state();
    let erreur: string | undefined = $state();
    let succes: string | undefined = $state();

    const lanceEvaluation = async () => {
        succes = undefined;
        if (fichierEvaluation === undefined || fichierEvaluation.length === 0 || fichierMapping === undefined || fichierMapping.length === 0) {
            erreur = "Veuillez sélectionner un fichier d'évaluation et un fichier de mapping";
            return;
        }
        const donnees = new FormData();
        donnees.append('fichier_evaluation', fichierEvaluation![0]);
        donnees.append('fichier_mapping', fichierMapping![0]);
        const reponse = await fetch(`/api/evaluation/`, {
            method: 'POST',
            body: donnees,
        });
        if (reponse.status !== 200) {
            erreur = "Erreur lors de l'évaluation";
            return;
        }
        succes = "Évaluation en cours";
        erreur = undefined;
    };

</script>

<div class="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
    <h4 class="text-xl font-semibold text-gray-700 mb-4">Évaluation</h4>
    <div class="grid gap-8">
        <div class="flex flex-row gap-1.5">
            <button
                    class="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                    type="button"
                    onclick={() => elementFichierEvaluation?.click()}
            >Ajouter un fichier d’évaluation
            </button>
            <div class="flex flex-col gap-1.5">
                <input
                        type="file"
                        id="fichier-evaluation"
                        name="fichier-evaluation"
                        accept=".csv"
                        bind:files={fichierEvaluation}
                        bind:this={elementFichierEvaluation}
                />
            </div>
        </div>
        <div class="flex flex-col gap-1.5">
            <div class="flex flex-row gap-1.5">
                <button
                        class="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                        type="button"
                        onclick={() => elementFichierMapping?.click()}
                >Ajouter un fichier de mapping
                </button>
                <input
                        type="file"
                        id="fichier-mapping"
                        name="fichier-mapping"
                        accept=".csv"
                        bind:files={fichierMapping}
                        bind:this={elementFichierMapping}
                />
            </div>
        </div>
        <div class="flex flex-wrap items-end gap-4">
            <button
                    type="button"
                    onclick={lanceEvaluation}
                    class="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 active:scale-95"
            >
                Lancer une évaluation
            </button>
        </div>
        {#if erreur}
            <div class="flex flex-wrap items-end gap-4">
                <p class="text-red-500">{erreur}</p>
            </div>
        {/if}
        {#if succes}
            <div class="flex flex-wrap items-end gap-4">
                <p class="text-green-500">{succes}</p>
            </div>
        {/if}
    </div>
</div>