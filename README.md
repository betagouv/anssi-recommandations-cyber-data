# anssi-recommandations-cyber-data

Une interface permettant d'évaluer le bot de l'ANSSI, basé sur Albert [Albert](https://github.com/betagouv/anssi-recommandations-cyber), et d'y indexer de nouveaux documents RAG.

## 📦 Comment installer ?

### Directement sur l'hôte

Il faut installer deux dépendances systèmes, `python` et `uv`.
Ensuite, la première fois il faut créer un environnement virtuel avec `uv venv`.

Dès lors, l'environnement est activable via `source .venv/bin/activate`.
Les dépendances déclarées sont installables via `uv sync`.

## 🧪 Comment valider ?

Dans un environnement virtuel :
* lancer `mypy` pour vérifier la validité des annotations de types,
* et lancer `pytest` pour valider le comportement à l'exécution.

## ⚙️ Comment Définir mes variables d'environnement ?

Il faut créer à la racine du projet un fichier `.env`.
A minima, ce fichier devra défnir les variables déclarées dans le fichier `.env.template`.

## 🧪 Générer les réponses du bot pour le jeu de validation

### 🎒 Prérequis

1. Cloner et lancer en local l’application [anssi-recommandations-cyber](https://github.com/betagouv/anssi-recommandations-cyber).  
   Exemple :
   ```bash
   env $(cat .env) python src/main.py
   ```
   ⚠️ Pensez à compléter le fichier `.env` à partir du modèle `.env.template`.

2. Vérifier que l’application **MQC** démarre bien en local (endpoint `/pose_question` accessible).

### ▶️ Génération des réponses
<a id="gen-reponses"></a>

Exécuter la commande suivante :

```bash

uv run python -m src.main_remplir_csv   --csv donnees/QA-labelisé-Question_par_guide.csv   --prefixe evaluation   --sortie donnees/sortie
```

- `--csv` : chemin vers le fichier CSV contenant les questions à évaluer.  
- `--prefixe` : préfixe utilisé dans le nom du fichier de sortie.  
- `--sortie` : dossier où sera écrit le CSV enrichi.  

Un fichier nommé `evaluation_YYYY-MM-DD_H_M_S.csv` sera alors généré dans `donnees/sortie/` avec une colonne **Réponse Bot** remplie automatiquement.

## 📊 Évaluer avec Evalap

### 🎒 Prérequis

1. Avoir défini dans votre fichier `.env` la variable `ALBERT_API_KEY`.  
⚠️ Sans cette variable, Evalap ne pourra pas interroger l’API Albert.
2. Disposer de [docker](https://docs.docker.com/get-docker/) et [docker compose](https://docs.docker.com/compose/install/) installés sur votre machine.  

### ▶️ Lancer Evalap

Depuis la racine du projet, exécuter :

```bash
docker compose -f evalap-compose.yml up -d
```

### ✅ Vérifications

S’assurer que les conteneurs démarrent correctement et que l’interface Evalap est accessible :
- l'IHM de l'API est accessible à l'adresse : http://localhost:8000/docs
- l'IHM de l'application web est accessible à l'adresse : http://localhost:8501

Si les urls ne semblent pas accessibles, vérifier qu’aucun conflit de port n’apparaît dans les logs.

### 📊 Évaluation

Une fois l'application lancée, pour évaluer un jeu de données :

1) Ajouter un dataset. Exécutez :
```bash
uv run python -m src.main_evalap --csv donnees/sortie/evaluation_2025-09-30_17-20-16.csv --nom nom_dataset 
```
Le chemin passé à `--csv` est celui généré à l’étape [« ▶️ Génération des réponses »](#gen-reponses)