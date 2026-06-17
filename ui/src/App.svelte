<script lang="ts">

  import {startAuthentication} from "@simplewebauthn/browser";

  type Initialisation = {
    challenge: string;
    id: string;
  }

  const authentifie = async () => {
    console.log("authentifie");

    const reponse = await fetch("/auth/initie", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({utilisateur: "bertrand.bougon"}),
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
      body: JSON.stringify({credential: authenticationResponse, challenge: initialisation.challenge})
    });

    console.log(`CONNECTÉ ? ${reponseFinalisation.status} : ${await reponseFinalisation.text()} - ${await reponseFinalisation.json()}`);
  }
</script>


<main class="main">
  <input type="button" value="bertrand.bougon" onclick={authentifie}>
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
