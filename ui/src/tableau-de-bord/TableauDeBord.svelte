<script>
    import CreeCollection from './CreeCollection.svelte';
    import AjouteDocumentCollection from "./AjouteDocumentCollection.svelte";
</script>

<main class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8">
            <h3 class="text-3xl font-bold text-gray-900 border-b pb-4">Tableau de bord</h3>
        </header>

        <section class="space-y-8">
            <div>
                <h4 class="text-xl font-semibold text-gray-700 mb-6 flex items-center">
                    <span class="bg-blue-600 w-2 h-8 rounded mr-3"></span>
                    Gestion des collections
                </h4>
                
                <div class="grid gap-8">
                    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <CreeCollection />
                    </div>
                    
                    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <AjouteDocumentCollection />
                    </div>
                </div>
            </div>
        </section>
    </div>
</main>
