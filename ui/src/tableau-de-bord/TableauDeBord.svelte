<script>
    import CreeCollection from './CreeCollection.svelte';
    import AjouteDocumentCollection from "./AjouteDocumentCollection.svelte";
    import Collections from "./Collections.svelte";
    import Documents from "./Documents.svelte";

    let activeTab = 'collections';
</script>

<main class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8">
            <h3 class="text-3xl font-bold text-gray-900 border-b pb-4">Tableau de bord</h3>
        </header>

        <!-- Système d'onglets -->
        <div class="mb-8 border-b border-gray-200">
            <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                <button
                    on:click={() => activeTab = 'collections'}
                    class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm {activeTab === 'collections' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                >
                    Gestion des collections
                </button>
                <button
                    on:click={() => activeTab = 'autre'}
                    class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm {activeTab === 'autre' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                >
                    Informations collections
                </button>
            </nav>
        </div>

        <section class="space-y-8">
            {#if activeTab === 'collections'}
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
            {:else if activeTab === 'autre'}
                <div class="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
                    <h4 class="text-xl font-semibold text-gray-700 mb-4">Informations collections</h4>
                    <div class="grid gap-8">
                        <Collections />

                        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                            <Documents />
                        </div>
                    </div>
                </div>
            {/if}
        </section>
    </div>
</main>
