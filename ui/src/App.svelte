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
            await startAuthentication({
                optionsJSON: {
                    challenge: initialisation.challenge,
                    rpId: window.location.hostname,
                    userVerification: "required",
                    allowCredentials: [
                        {id: initialisation.id, type: "public-key"}
                    ]
                }
            });

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


<main class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8">
            <h3 class="text-3xl font-bold text-gray-900 border-b pb-4">Authentification</h3>
        </header>
        <section class="space-y-8">
            <div class="grid gap-8">
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div>
                        <section class="grid gap-4">
                            <div class="space-y-6">
                                <input type="text" bind:value={identifiantEnrolement}
                                       class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"/>
                            </div>
                            <div>
                                <input type="button" value="Enrôlement" onclick={enrolement}
                                       class="w-full sm:w-auto px-6 py-2.5 cursor-pointer bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
                            </div>
                        </section>
                    </div>
                </div>


                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div>
                        <section class="grid gap-4">
                            <div class="space-y-6">
                                <input type="text" bind:value={identifiantAuthentification}
                                       class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"/>
                            </div>
                            <div>
                                <input type="button" value="Login" onclick={authentifie}
                                       class="w-full sm:w-auto px-6 py-2.5 cursor-pointer bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </section>
    </div>
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

</style>
