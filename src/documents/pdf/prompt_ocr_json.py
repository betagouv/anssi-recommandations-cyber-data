PROMPT_OCR_JSON = """Analyse uniquement la page fournie et retourne exclusivement un objet JSON valide.

La propriété blocks contient les blocs dans l'ordre naturel de lecture.
Un bloc possède toujours les propriétés type, code, title, text, level,
continues_previous, items et rows.

Utilise heading pour les titres, recommendation pour une recommandation portant
explicitement un code R suivi de chiffres, paragraph pour un paragraphe, list
pour une liste, table pour un tableau, other pour un contenu informatif qui ne
correspond pas aux autres catégories et footer pour un pied de page ou un
numéro de page décoratif.

Le champ code vaut null pour tous les blocs sauf recommendation. Pour une
recommendation, il vaut un code R suivi de chiffres ou null.

Sépare les titres, les recommandations et les paragraphes. Un titre visuel et sémantique est toujours un bloc heading distinct. Pour un heading, title contient le titre complet, y compris sa numérotation, et text vaut une chaîne vide. Le texte qui suit un titre est un bloc distinct et un paragraphe ne possède jamais de title.
Le champ level est renseigné uniquement pour les headings : 6 vaut 1, 6.1 vaut 2 et 6.1.2 vaut 3. Les paragraphes, recommandations, listes et tableaux ont level à null.

Une liste avec une introduction est un unique bloc list : text contient l'introduction et items contient les puces.
Une recommandation conserve son code, son titre, son contenu et ses puces éventuelles dans items. Lorsqu'un
premier bloc utile commence par une puce qui poursuit une liste de la page
précédente, continues_previous vaut true. N'invente aucun texte, code, titre
ou bloc. N'utilise ni Markdown ni commentaire."""
