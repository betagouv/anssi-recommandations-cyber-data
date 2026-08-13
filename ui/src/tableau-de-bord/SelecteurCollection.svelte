<script lang="ts">
  import {
    filtreCollectionsJeopardy,
    filtreCollectionsSource,
  } from './collection-filters';
  import { collectionsDisponiblesStore } from './store/collections-disponibles.store';

  interface Props {
    value: string;
    exclutJeopardy?: boolean;
    uniquementJeopardy?: boolean;
  }

  let {
    value = $bindable(''),
    exclutJeopardy = false,
    uniquementJeopardy = false,
  }: Props = $props();

  $effect(() => {
    collectionsDisponiblesStore
      .recupereCollectionsDisponibles()
      .then((collections) => collectionsDisponiblesStore.initialise(collections));
  });

  const formaterDate = (date: Date | string) =>
    new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });

  let collections = $derived(
    exclutJeopardy
      ? filtreCollectionsSource($collectionsDisponiblesStore ?? [])
      : uniquementJeopardy
        ? filtreCollectionsJeopardy($collectionsDisponiblesStore ?? [])
        : ($collectionsDisponiblesStore ?? []),
  );
</script>

<select
  bind:value
  class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
>
  <option value="" disabled selected>Sélectionner une collection</option>
  {#each collections as collection (collection.id)}
    <option value={String(collection.id)}>
      {collection.nom} (id : {collection.id}) — {formaterDate(collection.date_de_creation)}
    </option>
  {/each}
</select>
