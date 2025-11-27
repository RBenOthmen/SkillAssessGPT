# SkillAssessGPT

SkillAssessGPT est un système d'automatisation IA conçu pour générer automatiquement des grilles d'évaluation selon l'Approche Par Compétences (APC) et des situations d'évaluation authentiques.

## Vue d'ensemble

Le système utilise une architecture à deux agents IA :
- **Agent Générateur** : Crée la grille APC avec les niveaux ND/NI/NA, la situation d'évaluation et le barème
- **Agent Critique** : Valide la cohérence pédagogique de la grille générée

## Fonctionnalités

- ✅ Génération automatique de grilles APC structurées (ND, NI, NA)
- ✅ Création de situations d'évaluation authentiques
- ✅ Génération de barèmes de notation
- ✅ Validation pédagogique par un second agent IA
- ✅ Export en JSON et Markdown
- ✅ Support complet du français

## Prérequis

- Python 3.8 ou supérieur
- Clé API Google Gemini (obtenir sur [Google AI Studio](https://aistudio.google.com/app/apikey))

## Installation

1. Cloner le dépôt :
```bash
git clone <repository-url>
cd SkillAssessGPT
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer la clé API :

Créer un fichier `.env` à la racine du projet et ajouter votre clé API :
```
GOOGLE_API_KEY=votre_clé_api_ici
```

## Utilisation

### Interface en ligne de commande

```bash
python src/main.py
```

Le système vous guidera à travers les étapes suivantes :
1. Saisie de la compétence à évaluer
2. Saisie des paramètres contextuels (niveau, parcours, spécialité, durée)
3. Génération automatique de la grille APC
4. Validation par l'agent critique
5. Export des résultats

### Interface Jupyter Notebook

```bash
jupyter notebook notebook.ipynb
```

## Structure du projet

```
SkillAssessGPT/
├── src/                    # Code source
│   ├── models.py          # Modèles de données
│   ├── input_collector.py # Collecte des entrées utilisateur
│   ├── generator.py       # Agent générateur
│   ├── critic.py          # Agent critique
│   ├── exporter.py        # Module d'export
│   └── main.py            # Pipeline principal
├── tests/                  # Tests unitaires et property-based
├── outputs/                # Fichiers générés (JSON, Markdown)
├── requirements.txt        # Dépendances Python
├── .env                    # Configuration API (non versionné)
└── README.md              # Ce fichier
```

## Exemple de sortie

### Grille APC générée

| Niveau | Critères | Indicateurs |
|--------|----------|-------------|
| ND     | Critère 1 | Indicateur 1, 2, 3 |
| NI     | Critère 2 | Indicateur 1, 2, 3 |
| NA     | Critère 3 | Indicateur 1, 2, 3 |

### Formats d'export

- **JSON** : Structure complète avec tous les champs
- **Markdown** : Format lisible avec tableaux formatés

## Tests

Exécuter les tests unitaires :
```bash
pytest tests/
```

Exécuter les tests property-based :
```bash
pytest tests/test_properties.py
```

## Architecture

Le système suit un pipeline séquentiel :

```
Entrée Utilisateur → Agent Générateur → Agent Critique → Module Export → Fichiers de sortie
```

### Composants principaux

1. **InputCollector** : Collecte et valide les entrées utilisateur
2. **GeneratorAgent** : Génère la grille APC et la situation d'évaluation
3. **CriticAgent** : Valide la cohérence pédagogique
4. **ExportModule** : Formate et sauvegarde les résultats

## Dépendances

- `google-generativeai` : Appels API vers Google Gemini
- `requests` : Requêtes HTTP
- `python-dotenv` : Gestion des variables d'environnement
- `hypothesis` : Tests property-based
- `pytest` : Framework de tests

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces étapes :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

[À définir]

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt GitHub.
