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
            body: JSON.stringify({nom: nomCollection, description: descriptionCollection, fichiers: fichiersCollection.split(",")})
        });

        const contenuReponse = await reponse.json();
        reponseCreationCollection = contenuReponse.message;
    }

</script>

<div>
    <h4>Créer une collection</h4>
    <section>
        <div>
            <label for="nom-collection">Nom de la collection :</label>
            <input type="text" id="nom-collection" name="nom-collection" bind:value={nomCollection} required>
        </div>
        <div>
            <label for="description-collection">Description de la collection :</label>
            <input type="text" id="description-collection" name="description-collection" bind:value={descriptionCollection} required>
        </div>
        <div>
            <label for="fichiers-collection">Fichiers à ajouter dans la collection :</label>
            <textarea id="fichiers-collection" rows="3" cols="38" name="fichiers-collection" bind:value={fichiersCollection} placeholder="Séparer les noms des fichiers par des virgules" required ></textarea>
        </div>
        <div>
            <button type="button" onclick={creeCollection}>Créer</button>
        </div>
        {#if reponseCreationCollection}
            <p>{reponseCreationCollection}</p>
        {/if}
    </section>
</div>
