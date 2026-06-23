<script lang="ts">

    import type {Document} from "./store/documents.store";

    type DocumentConsolide = {
        nom: string;
        indexee?: Document;
        jeopardy?: Document;
    }

    interface Props {
        documents: DocumentConsolide[];
    }

    const {documents}: Props = $props()

    const documentManquantDansUneCollection = (doc: DocumentConsolide) => !doc.indexee || !doc.jeopardy
</script>
<div class="min-w-full">
                        <div class="bg-gray-50 border-b border-gray-200 grid grid-cols-[80px_80px_1fr_80px_80px_140px_140px] gap-4 px-6 py-3">
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID J</div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Chunks</div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Chunks J</div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date création</div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date création J</div>
                        </div>

                        <div class="divide-y divide-gray-200">
                            {#each documents as doc (doc.nom)}
                                <div class="grid grid-cols-[80px_80px_1fr_80px_80px_140px_140px] gap-4 px-6 py-4 hover:bg-gray-50 transition-colors items-center">
                                    <div class="text-sm font-mono truncate {documentManquantDansUneCollection(doc) ? 'text-red-400 italic' : 'text-gray-500'}" title={doc.indexee?.id ?? 'Manquant'}>
                                        {documentManquantDansUneCollection(doc) ? '❌ ' : '' }{doc.indexee?.id ?? '-'}
                                    </div>
                                    <div class="text-sm font-mono truncate {documentManquantDansUneCollection(doc) ? 'text-red-400 italic' : 'text-gray-500'}" title={doc.jeopardy?.id ?? 'Manquant'}>
                                        {doc.jeopardy?.id ?? '-'}
                                    </div>
                                    <div class="text-sm font-medium {documentManquantDansUneCollection(doc) ? 'text-red-800 italic' : 'text-gray-900'} truncate" title={doc.nom}>
                                        {doc.nom}
                                    </div>
                                    <div class="text-sm {documentManquantDansUneCollection(doc) ? 'text-red-400 italic' : 'text-gray-500'}">
                                        {doc.indexee?.chunks ?? '-'}
                                    </div>
                                    <div class="text-sm {documentManquantDansUneCollection(doc) ? 'text-red-400 italic' : 'text-gray-500'}">
                                        {doc.jeopardy?.chunks ?? '-'}
                                    </div>
                                    <div class="text-sm {documentManquantDansUneCollection(doc) ? 'text-red-400 italic' : 'text-gray-500'}">
                                        {#if doc.indexee}
                                            {new Date(doc.indexee.date_de_creation).toLocaleDateString('fr-FR', {
                                                year: 'numeric', month: 'numeric', day: 'numeric'
                                            })}
                                        {:else}
                                            -
                                        {/if}
                                    </div>
                                    <div class="text-sm {documentManquantDansUneCollection(doc) ? 'text-red-400 italic' : 'text-gray-500'}">
                                        {#if doc.jeopardy}
                                            {new Date(doc.jeopardy.date_de_creation).toLocaleDateString('fr-FR', {
                                                year: 'numeric', month: 'numeric', day: 'numeric'
                                            })}
                                        {:else}
                                            -
                                        {/if}
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>