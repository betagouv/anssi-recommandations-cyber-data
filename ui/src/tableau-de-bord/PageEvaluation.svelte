<script lang="ts">

    let elementFichier: HTMLInputElement | undefined = $state();
    let fichierEvaluation: FileList | undefined = $state();
    let fichierMapping: FileList | undefined = $state();

    const lanceEvaluation = async () => {
        const donnees = new FormData();
        donnees.append('fichier_evaluation', fichierEvaluation![0]);
        donnees.append('fichier_mapping', fichierMapping![0]);
        const reponse = await fetch(`/api/evaluation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            body: donnees,
        });
        if (reponse.status !== 200) {
            console.error('Erreur lors de l\'évaluation');
        }
    };

</script>

<div class="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
    <h4 class="text-xl font-semibold text-gray-700 mb-4">Évaluation</h4>
    <div class="grid gap-8">
        <div class="flex flex-col gap-1.5">
            <input
                    type="file"
                    id="fichier"
                    name="fichier"
                    accept=".csv"
                    bind:files={fichierEvaluation}
                    bind:this={elementFichier}
            />
        </div>
        <div class="flex flex-col gap-1.5">
            <input
                    type="file"
                    id="fichier"
                    name="fichier"
                    accept=".csv"
                    bind:files={fichierMapping}
                    bind:this={elementFichier}
            />
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
    </div>
</div>