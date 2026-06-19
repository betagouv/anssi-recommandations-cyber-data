<script lang="ts">

    let fichiersAAjouter = $state<string>("");
    let fichiersAModifier = $state<string>("");
    let fichiersASupprimer = $state<string>("");
    let reponseMiseAJourDocuments = $state<string | undefined>(undefined);


    const metsAJourLaCollection = async () => {
        const fichiersAjoutes = fichiersAAjouter.split(",");
        const fichiersModifies = fichiersAModifier.split(",");
        const fichiersSupprimes = fichiersASupprimer.split(",");
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

<div>
    <h4>Modifier une collection</h4>
    <section>
        <div>
            <label for="fichiers-a-ajouter">Fichiers à ajouter dans la collection :</label>
            <textarea id="fichiers-a-ajouter" rows="3" cols="38" name="fichiers-a-ajouter" bind:value={fichiersAAjouter}
                      placeholder="Séparer les noms des fichiers par des virgules" required></textarea>
        </div>
        <div>
            <label for="fichiers-a-modifier">Fichiers à modifier dans la collection :</label>
            <textarea id="fichiers-a-modifier" rows="3" cols="38" name="fichiers-a-modifier"
                      bind:value={fichiersAModifier} placeholder="Séparer les noms des fichiers par des virgules"
                      required></textarea>
        </div>
        <div>
            <label for="fichiers-a-supprimer">Fichiers à supprimer de la collection :</label>
            <textarea id="fichiers-a-supprimer" rows="3" cols="38" name="fichiers-a-supprimer"
                      bind:value={fichiersASupprimer} placeholder="Séparer les noms des fichiers par des virgules"
                      required></textarea>
        </div>
        <div>
            <button type="button" onclick={metsAJourLaCollection}>Mets à jour les documents</button>
        </div>
        {#if reponseMiseAJourDocuments}
            <p>{reponseMiseAJourDocuments}</p>
        {/if}
    </section>
</div>