import './app.css';
import './fonts.css';
import { mount } from 'svelte';
import TableauDeBord from './tableau-de-bord/TableauDeBord.svelte';

const tableauDeBord = mount(TableauDeBord, {
  target: document.getElementById('tableau-de-bord')!,
});

export default tableauDeBord;
