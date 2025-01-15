<details open>
    <summary><b style="font-size: 14pt; background: linear-gradient(90deg, #00f 0, #fff 50%, #f00 100%); color: transparent; background-clip: text; display: inline-block;">Français</b></summary>

# Traduction automatique pour les langues anciennes peu documentées

## FTF

> Ce travail a été réalisé dans le cadre d'un projet autonome en M1 TAL.

L'objectif initial du projet était de créer une application de traduction automatique entre le français et le vieux français. Le latin et le grec ancien sont également disponibles, ainsi qu'une transcription automatique en API pour ces derniers au travers de différentes époques et régions.

Ce dépôt contient une liste de sources utilisées pour agréger des données textuelles (voir [ici](./sources/sources.xml)), des données textuelles utiles au projet (voir [là](./data/)), des scripts pour récupérer, nettoyer et formater les données, ainsi que pour entraîner, tester et évaluer un modèle ([par ici](./scripts/)).

Une application Flask permet également d'afficher les résultats de la traduction et de la transcription phonétique dans une interface utilisateur web accessible (voir [ici](./web/)).

### Pour commencer

> Si vous débutez, vous pouvez vous référer à [HELP.md](./HELP.md) pour lire un guide contenant les commandes classiques générales et celles utiles pour ce projet.

- Cloner le dépôt : `git clone https://github.com/mi-1000/ftf`
- Créer un environnement virtuel : `python -m .venv venv`
- L'activer :
  - Bash/zsh : `source venv/bin/activate` (Linux, MacOS, WSL2)
  - CMD: `.\venv\Scripts\activate` (Windows)
  - PowerShell : `.\venv\Scripts\Activate.ps1` (Windows)
    - En cas d'erreur, entrer d'abord `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Installer les dépendances : `pip install -r requirements.txt`
  - Certains modèles utilisés devront être installés séparément (par exemple *via* `SpaCy` ou `Ollama`, se référer aux erreurs le cas échéant)
- Lancer l'application Flask :
  - Se placer dans le dossier `web` : `cd web`
  - Démarrer le serveur : `flask run`
  - Accéder au site : [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Fonctionnalités

- Liste de sources utilisées pour récupérer des données.
- Scripts pour agréger, nettoyer et formater des données textuelles dans les langues anciennes mentionnées.
- Scripts pour entraîner et évaluer un modèle de traduction automatique.
- Traduction automatique entre le français, le vieux français, le latin et le grec ancien.
- Transcription phonétique automatique suivant différents standards et époques pour le français, le vieux français, le latin et le grec ancien.
- Détection d'anachronismes à partir d'une base de données contenant les dates de première attestation de mots français.
- Interface utilisateur web pour visualiser les résultats.

|:information_source:|Si vous êtes pour une raison quelconque intéressé par le projet, un rapport détaillant plus minutieusement les étapes, la conception et l'état du projet est disponible. Vous pouvez [m'envoyer un message](https://github.com/mi-1000) le cas échéant.|
|-------------------|:----------------|

</details>
<details>
    <summary><b style="font-size: 14pt;">English</b></summary>

# Enabling Automatic Translation For Low-Resource Ancient Languages

## FTF

> This work was carried out as part of an unsupervised project in the first year of NLP master's degree.

The initial goal of the project was to create a machine translation application between modern French and Old French. Latin and Ancient Greek are also available, with automatic IPA transcription for them across different eras and regions.

This repository contains a list of sources used to gather textual data (see [here](./sources/sources.xml)), textual data useful for the project (see [there](./data/)), scripts to retrieve, clean, and format the data, as well as to train, test, and evaluate a model ([over here](./scripts/)).

A Flask application also displays translation and phonetic transcription results in an accessible web user interface (see [here](./web/)).

### Getting Started

> If you’re just starting out, you can consult [HELP.md](./HELP.md) for a guide on typical commands in general, as well as those useful for this project.

- Clone the repository: `git clone https://github.com/mi-1000/ftf`
- Create a virtual environment:
`python -m .venv venv`
- Activate it:
  - Bash/zsh: `source venv/bin/activate` (Linux, MacOS, WSL2)
  - CMD: `.\venv\Scripts\activate` (Windows)
  - PowerShell: `.\venv\Scripts\Activate.ps1` (Windows)
    - If you get an error, run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` first
- Install dependencies: `pip install -r requirements.txt`
  - Some models used will need to be installed separately (for example via `SpaCy` or `Ollama`, refer to errors if necessary)
- Launch the Flask application:
  - Navigate to the `web` folder: `cd web`
  - Start the server: `flask run`
  - Access the site at [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Features

- List of sources used to retrieve data
- Scripts to aggregate, clean, and format textual data in the aforementioned ancient languages
- Scripts to train and evaluate a machine translation model
- Machine translation between modern French, Old French, Latin, and Ancient Greek
- Automatic phonetic transcription according to different standards and eras for French, Old French, Latin, and Ancient Greek
- Detection of anachronisms from a database containing the earliest attestation dates of French words
- Web-based user interface to visualize results

|:information_source:|If for any reason you’re interested in the project, a detailed report describing the steps, design, and current state of the project is available. You can [send me a message](https://github.com/mi-1000) if needed.|
|-------------------|:----------------|

</details>
