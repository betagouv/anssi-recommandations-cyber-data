PROMPT_OCR_JSON = """Analyse uniquement la page fournie et retourne exclusivement un objet JSON valide.

La propriété blocs contient les blocs dans l'ordre naturel de lecture.
Un bloc possède toujours les propriétés type_de_bloc, code_recommandation, titre,
texte, niveau, est_une_continuation, elements_de_liste et lignes_de_tableau.

Utilise titre uniquement pour un titre de la hiérarchie documentaire. Utilise
recommandation uniquement pour une recommandation portant explicitement un code
R suivi de chiffres. Le type recommandation est réservé à une recommandation
dont le code Rxx est visible. Représente les recommandations sans code visible,
notamment sous une rubrique RECOMMANDATIONS, comme des blocs liste. Utilise
paragraphe pour un paragraphe, liste pour une liste, tableau pour un tableau,
table_des_matieres pour un sommaire, autre pour un contenu informatif ou un
encadré qui ne correspond pas aux autres catégories et pied_de_page pour un pied
de page ou un numéro de page décoratif.

Le champ code_recommandation vaut null pour tous les blocs sauf recommandation,
pour laquelle il contient obligatoirement un code R suivi de chiffres. N'invente
jamais la lettre R devant un numéro.

Sépare les titres, les recommandations et les paragraphes. Ne saute jamais un
titre de chapitre visible. Lorsqu'un titre de chapitre précède un encadré comme
Objectif, retourne d'abord le titre dans un bloc titre distinct, puis l'encadré
dans un bloc autre distinct. Un titre visuel et sémantique est toujours un bloc
titre distinct. Pour un titre, titre contient le titre complet, y compris sa
numérotation, et texte vaut une chaîne vide. Le bloc reste unique lorsque son
numéro et son libellé sont placés sur deux lignes.

Le texte qui suit un titre est un bloc distinct et un paragraphe ne possède jamais
de titre. Un encadré comme Attention, Objectif ou un libellé équivalent est un
bloc autre, même si son titre ressemble à une section : conserve son titre et
son texte, sans en faire une section. Un encadré coloré avec une icône ou une
ligne verticale est également un bloc autre lorsqu'il ne porte pas de code de
recommandation. Une table des matières est un unique bloc table_des_matieres qui
conserve son titre et toutes ses entrées, avec une entrée par élément dans
elements_de_liste.

Le champ niveau est renseigné uniquement pour les titres : 6 vaut 1, 6.1 vaut 2
et 6.1.2 vaut 3. Les paragraphes, recommandations, listes et tableaux ont niveau
à null. Déduis le niveau de la numérotation et de la hiérarchie visuelle. Une
annexe ouvre une nouvelle racine documentaire et les rubriques de l'annexe,
comme les références, restent sous cette racine.

Une liste avec une introduction est un unique bloc liste : texte contient
l'introduction et elements_de_liste contient les puces. Une recommandation
conserve son code, son titre, son contenu et ses puces éventuelles dans
elements_de_liste. Lorsqu'un premier bloc utile poursuit une liste de la page
précédente, est_une_continuation vaut true, même si son marqueur graphique n'est
plus visible. Lorsqu'une liste en début de page poursuit les puces d'une
recommandation de la page précédente, retourne uniquement la liste, marque-la
comme continuation et ne répète pas le code ni le titre de la recommandation.
Si le haut d'une page contient du texte sans puce qui termine un élément de liste
précédent, conserve ce texte dans le même bloc liste et marque la continuation.
Si une nouvelle puce apparaît ensuite, conserve-la dans elements_de_liste du même
bloc liste. Tout texte qui commence visuellement par ■, •, ▪, ◦, ‣ ou par un tiret
suivi d'un espace est obligatoirement un élément de liste : ne le retourne jamais
comme paragraphe. Regroupe dans un même bloc les fragments qui appartiennent au
même paragraphe, à la même liste ou à la même recommandation.

Inspecte systématiquement les cartouches visuels colorés contenant un code de
recommandation. Lorsqu'un cartouche R suivi de chiffres est placé à gauche d'un
titre et d'un texte, il appartient au même bloc. Un cartouche R20 associé à un
titre et à un texte doit produire un seul bloc recommandation avec
code_recommandation égal à R20, le titre complet et le texte associé. Ce
cartouche ne doit pas être classé comme un titre documentaire. Avant de terminer,
vérifie que chaque cartouche R suivi de chiffres visible sur la page est présent
dans la sortie JSON. N'invente jamais de code si aucun cartouche n'est visible.

Transcris sans omission tous les textes informatifs, notamment les partenaires,
les noms, les chiffres et les libellés des infographies. Transcris exactement
les numéros, codes, libellés et termes visibles, sans les reformuler, les
compléter ni en inventer. Exclus uniquement les vrais en-têtes répétés, pieds de
page, numéros de page et logos sans contenu informatif, tout en conservant les
légendes de figures.

Pour un tableau, restitue l'intégralité du tableau dans texte sous la forme d'un
tableau HTML bien formé, avec les balises table, thead, tbody, tr, th et td
uniquement. Place la ligne d'en-tête dans thead avec des cellules th lorsqu'une
ligne d'en-tête est visible. Renseigne aussi lignes_de_tableau avec les cellules
du tableau, chaque ligne étant une liste de chaînes. N'utilise cette balise HTML
que pour un tableau : pour tous les autres blocs, n'utilise ni Markdown ni HTML
ni commentaire.

Renseigne toujours les huit propriétés attendues, avec null pour
code_recommandation, titre, elements_de_liste ou lignes_de_tableau lorsqu'ils
ne s'appliquent pas. N'utilise ni Markdown ni commentaire."""
