# HyDE

## But 
Générer une collection de questions à partir des chunks générés à partir des documents d'origine. 
Cela nous permettra de confronter des questions utilisateurs·ices à un ensemble de questions données dans un contexte donné.

La génération de questions est réalisée en deux étapes principales :
1. **Extraction de chunks** : Les documents d'origine sont divisés en segments plus petits, appelés chunks.
2. **Génération de questions** : Les chunks sont ensuite utilisés pour générer des questions pertinentes.

### Description des collections
- **Collection source RAG :** La collection des documents d'origine.
- **Collection miroir HyDE / Jeopardy :** La collection miroir des questions générées.

```mermaid
flowchart LR
    %% =========================
    %% Collection source RAG
    %% =========================
    subgraph SRC["Collection source RAG"]
        C1["CollectionDocuments"]

        D1["Document A"]
        D2["Document B"]

        CH1["Chunk A-001
        paragraphe vectorisé"]
        CH2["Chunk A-…
        paragraphe vectorisé"]
        CH3["Chunk B-001
        paragraphe vectorisé"]

        C1 --> D1
        C1 --> D2

        D1 --> CH1
        D1 --> CH2
        D2 --> CH3
    end

    %% =========================
    %% Collection miroir HyDE / Jeopardy
    %% =========================
    subgraph MIRROR["Collection miroir HyDE / Jeopardy"]
        C2["CollectionQuestionsMiroir"]

        MD1["Document A
        miroir"]
        MD2["Document B
        miroir"]

        Q1["Chunk question A-001-Q1
        question générée"]
        Q2["Chunk question A-…
        question générée"]

        Q5["Chunk question B-001-Q1
        question générée"]
        Q6["Chunk question …
        question générée"]

        C2 --> MD1
        C2 --> MD2

        MD1 --> Q1
        MD1 --> Q2

        MD2 --> Q5
        MD2 --> Q6
    end

    SRC --> MIRROR
```

### Cas d’utilisation
```mermaid
flowchart TD

    A["Question utilisateur"] --> B["Reformulation de la question"]

    B --> C1["Recherche classique
    dans la collection originale"]
    B --> C2["Recherche dans la collection questions miroir"]

    C1 --> D1["Top 10 chunks les plus proches
    de la collection originale"]

    C2 --> D2["Top 10 questions générées
    les plus proches"]

    D2 --> E["Lecture des métadonnées
    de chaque chunk question"]
    E --> F["Récupération des ids des chunks sources
    dans la collection originale"]
    F --> G["Chargement des 10 chunks sources
    correspondants"]

    D1 --> H["Fusion des résultats
    10 chunks classiques + 10 chunks issus du miroir"]
    G --> H

    H --> I["Top 20 chunks candidats"]

    I --> J["Re-ranking"]
    J --> K["Top K chunks finaux"]

    K --> L["Construction du contexte"]
    L --> M["Génération de la réponse"]
```

## Architecture
Pour une collection donnée, on crée une collection de questions miroir.

```mermaid
sequenceDiagram
    participant S as Service de création de questions
    participant C as Collection
    participant CollecteurDeQuestions as Collecteur de questions
    participant Albert as Albert
    
    S -->> C: Demande les documents et chunks d’une collection
    C -->> S: Retourne les documents et chunks
    S -->> CollecteurDeQuestions: Initie une collection de questions
    CollecteurDeQuestions -->> Albert: Crée la collection de questions
    Albert -->> CollecteurDeQuestions: Retourne l’identifiant de la collection de questions
    CollecteurDeQuestions -->> Albert: Demande à Albert de générer N questions pour chaque chunk
    Albert -->> CollecteurDeQuestions: Retourne les questions générées
    CollecteurDeQuestions -->> Albert: Ajoute les questions générées (un chunk par question) à la collection de questions
    CollecteurDeQuestions -->> S: Collection complétée
```

### Pistes de réflexion
- On ne génère pas de question pour des chunks trop petits (e.g : `[TITRE] MESURES CYBER PRÉVENTIVES PRIORITAIRES`)

### Typage d’un chunk de question générée
```json
{'object': 'chunk',
  'id': 312,
  'collection_id': 161145,
  'document_id': 4076447,
  'content': 'Ma question ?',
  'metadata': {
               'source_id_document': '4065642',
               'source_id_chunk': 73,
               'source_numero_page': 17
              },
  'created': 1774968050
}
```