# 📚 QCM par thème et leçon

Application Streamlit de QCM et cartes d'apprentissage, basée sur des fichiers JSON de questions organisés par thèmes et leçons. L’interface est optimisée pour un usage sur mobile et propose un thème sombre par défaut, un mode QCM et un mode Cartes.

---

## 1. Fonctionnalités

- Scan automatique des leçons depuis des fichiers JSON dans `lessons/` (monté depuis `data/lessons/` sur l’hôte).
- Sélection d’un **thème** et d’une **leçon** via la barre latérale Streamlit.
- Mode **QCM** :
  - Questions tirées au hasard avec réponses mélangées.
  - Validation, score, pourcentage de réussite.
  - Affichage de la correction complète pour la leçon.
- Mode **Cartes** :
  - Afficher / cacher la réponse par carte.
  - Option dans le menu de gauche pour afficher automatiquement les réponses.
- Thème sombre et UI adaptée aux écrans de smartphone (boutons full-width, marges réduites).

---

## 2. Structure des données (`lessons`)

Les questions sont stockées dans des fichiers JSON dans un dossier `lessons` à l’intérieur du conteneur (lié à `data/lessons` sur l’hôte). Nom de fichier recommandé :  

```text
<Thème> - <Leçon>.json

### 2.1 Exemple de fichier JSON

{
  "questions": [
    {
      "question": "Texte de la question",
      "reponses": [
        "Réponse A",
        "Réponse B",
        "Réponse C"
      ],
      "bonne_reponse": "Réponse B",
      "explication": "Explication optionnelle de la réponse."
    }
  ]
}


Le code s’attend à trouver une clé "questions" contenant une liste d’objets avec question, reponses, bonne_reponse et éventuellement explication.

## 3. Arborescence du projet
Côté projet Docker (hôte) :
projet-qcm/
├─ app.py                 # Script Streamlit principal
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ .gitignore
├─ .streamlit/
│  └─ config.toml         # Thème sombre (optionnel)
└─ data/
   └─ lessons/            # Fichiers JSON de leçons (non versionnés)
      ├─ Theme1 - Leçon 1.json
      └─ ...

Dans le conteneur, le dossier data/lessons est monté sur /app/lessons, ce qui permet de préserver tes fichiers JSON indépendamment des mises à jour de l'image Docker.

## 4. Installation et exécution avec Docker
### 4.1 Prérequis
Docker et Docker Compose installés sur la machine (Linux, macOS ou Windows).

### 4.2 Cloner le dépôt

## 4. Installation et exécution avec Docker
### 4.1 Prérequis
Docker et Docker Compose installés sur la machine (Linux, macOS ou Windows).

### 4.2 Cloner le dépôt
git clone https://github.com/<ton-user>/<ton-repo-qcm>.git
cd <ton-repo-qcm>

### 4.3 Préparer les leçons
Créer le dossier de données local (s’il n’existe pas) :
mkdir -p data/lessons

Ajouter vos fichiers JSON de leçons dans data/lessons/ (voir format ci-dessus). Ces fichiers sont ignorés par Git (via .gitignore) et ne seront jamais écrasés par les mises à jour du code depuis GitHub.

### 4.4 Construire et lancer avec Docker Compose
Build + run en détaché :

docker compose up --build -d

L’application est ensuite disponible sur :
http://localhost:8501
Les fichiers JSON sous data/lessons/ sont montés comme volume et restent inchangés lors des rebuilds de l'image.

## 5. Thème sombre (Streamlit)
Pour forcer un thème sombre par défaut dans Streamlit, ajouter un fichier :
.streamlit/config.toml

Avec le contenu :
[theme]
base = "dark"
primaryColor = "#4CAF50"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1E222A"
textColor = "#FAFAFA"
font = "sans serif"

Ce fichier configure le thème global de l’application Streamlit en mode sombre.

## 6. Développement local (sans Docker)
Tu peux aussi lancer l’app directement avec Python pour développer plus rapidement :

python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows

pip install -r requirements.txt
streamlit run app.py

L’interface sera accessible sur :
http://localhost:8501
