<script lang="ts">

    import type {Document} from "./store/documents.store";

    interface Props {
        documents: Document[];
    }

    const {documents}: Props = $props()
</script>
<div class="min-w-full">
                        <div class="bg-gray-50 border-b border-gray-200 grid grid-cols-[100px_1fr_100px_200px] gap-4 px-6 py-3">
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Chunks
                            </div>
                            <div class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date de
                                création
                            </div>
                        </div>

                        <div class="divide-y divide-gray-200">
                            {#each documents as document (document.id)}
                                <div class="grid grid-cols-[100px_1fr_100px_200px] gap-4 px-6 py-4 hover:bg-gray-50 transition-colors items-center">
                                    <div class="text-sm font-mono text-gray-500 truncate"
                                         title={document.id}>{document.id}</div>
                                    <div class="text-sm font-medium text-gray-900 truncate"
                                         title={document.nom}>{document.nom}</div>
                                    <div class="text-sm text-gray-500">{document.chunks}</div>
                                    <div class="text-sm text-gray-500">
                                        {new Date(document.date_de_creation).toLocaleDateString('fr-FR', {
                                            year: 'numeric',
                                            month: 'numeric',
                                            day: 'numeric',
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>