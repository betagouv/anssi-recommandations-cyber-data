<script lang="ts">

  import {startAuthentication, startRegistration} from "@simplewebauthn/browser";

  let identifiantEnrolement = $state("")
  let identifiantAuthentification = $state("")

  type Initialisation = {
    challenge: string;
    id: string;
  }

  const authentifie = async () => {
    if (identifiantAuthentification.trim() === "") return;

    const reponse = await fetch("/auth/initie", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({utilisateur: identifiantAuthentification}),
    });

    const initialisation: Initialisation = await reponse.json();

    const authenticationResponse =
            await startAuthentication({optionsJSON: {challenge: initialisation.challenge, rpId: window.location.hostname, userVerification: "required", allowCredentials: [
                  {id: initialisation.id, type: "public-key"}
                ] }});

    const reponseFinalisation = await fetch("/auth/finalise", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({credential: authenticationResponse, utilisateur: identifiantAuthentification})
    });

    console.log(`CONNECTÉ ? ${reponseFinalisation.status} : ${await reponseFinalisation.text()} - ${await reponseFinalisation.json()}`);
  }

  const enrolement = async () => {
    if (identifiantEnrolement.trim() === "") return;

    const reponse = await fetch("/auth/enrole", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({utilisateur: identifiantEnrolement})
    });

    const enrolement = await reponse.json();
    const credential = await startRegistration(JSON.parse(enrolement.options));

    const reponseVerificationEnrolement = await fetch("/auth/verifie-enrolement", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({credential, utilisateur: enrolement.utilisateur})
    });

    console.log(`ENRÔLÉ ? ${reponseVerificationEnrolement.status}`);
  }
</script>


<main class="main">
  <section>
    <div>
      <input type="text" bind:value={identifiantEnrolement} />
    </div>
    <div>
      <input type="button" value="Enrôlement" onclick={enrolement}>
    </div>
  </section>

  <section>
    <div>
      <input type="text" bind:value={identifiantAuthentification} />
    </div>
    <div>
      <input type="button" value="Login" onclick={authentifie}>
    </div>
  </section>
</main>

<style lang="scss">
  :global(html, body) {
    height: 100%;
  }

  :global(body) {
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

</style>
