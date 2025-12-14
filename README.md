# Simulateur d'Investissement Flexible

## Description du Projet

Ce simulateur d'investissement est une application web développée avec **Streamlit** et conçue spécifiquement pour les **commerciaux** de CGF GESTION. Son objectif principal est de faciliter la présentation de simulations financières aux clients, en offrant une flexibilité totale dans le calcul des paramètres clés d'un placement.

L'application permet de déterminer l'un des quatre paramètres suivants en fonction des trois autres :
1.  **Montant Final (Objectif)**
2.  **Versement Mensuel (Contribution)**
3.  **Montant Initial (Capital de départ)**
4.  **Horizon de Placement (Durée)**

L'interface est épurée, utilise les couleurs de la marque (Bleu foncé et Gris) pour une cohérence visuelle, et intègre des graphiques interactifs pour une meilleure compréhension des projections.

## Fonctionnalités Clés

*   **Calcul Flexible** : L'utilisateur choisit le paramètre à calculer, et l'application détermine sa valeur en fonction des entrées restantes.
*   **Visualisation Interactive** : Utilisation de Plotly et Altair pour des graphiques dynamiques montrant l'évolution de la valeur totale, du capital investi et des intérêts accumulés au fil du temps.
*   **Aide à la Vente** : Pour le calcul du **Versement Mensuel**, l'application affiche automatiquement les cotisations équivalentes par mois, par trimestre et par année, facilitant la discussion avec le client sur ses capacités d'épargne.
*   **Cohérence de Marque** : Intégration du logo et des couleurs de la marque pour une présentation professionnelle.
*   **Gestion des Informations Commerciales** : Saisie et sauvegarde des informations client (interlocuteur, nom du client, pays) dans la barre latérale.
*   **Interface Moderne en Cartes** : Présentation des métriques et résultats dans des cartes élégantes avec icônes, couleurs et pourcentages.

## Modèle Financier

Le simulateur repose sur la formule de la **Valeur Future d'une Annuité** (Future Value of an Annuity), qui modélise la croissance d'un capital initial avec des versements périodiques réguliers, soumis à un taux de rendement annualisé.

La formule de base est :

$$FV = PV \times (1 + r_{mensuel})^n + PMT \times \frac{(1 + r_{mensuel})^n - 1}{r_{mensuel}}$$

Où :
*   $FV$ : Montant Final (Future Value)
*   $PV$ : Montant Initial (Present Value)
*   $PMT$ : Versement Mensuel (Payment)
*   $r_{mensuel}$ : Taux de rendement mensuel ($r_{annuel} / 12$)
*   $n$ : Nombre total de mois

Les calculs pour $PMT$, $PV$, et $n$ sont dérivés de cette formule pour assurer la flexibilité de l'outil.

## Installation et Utilisation

Pour exécuter l'application, vous devez avoir Python installé sur votre système.

### 1. Prérequis

Assurez-vous d'avoir les librairies nécessaires. Utilisez le fichier `requirements.txt` fourni :

```bash
pip install -r requirements.txt
```

Ou installez manuellement les dépendances :

```bash
pip install streamlit>=1.28.0 pandas>=2.0.0 numpy>=1.24.0 plotly>=5.17.0 altair>=5.1.0 Pillow>=10.0.0
```

### 2. Exécution de l'Application

1.  Clonez ou téléchargez le repository complet
2.  Le logo est déjà présent dans le dossier `assets/`
3.  Lancez l'application via votre terminal :

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur web.

### 3. Navigation

L'application comporte plusieurs pages accessibles via le menu latéral :
- **Accueil** : Page de présentation de l'application
- **Simulation** : Calculateur d'investissement flexible
- **Scénarios & Projections** : Analyses avancées et scénarios de sensibilité
  - Comparaison intelligente par horizon de placement
  - Analyse de sensibilité aux taux de rendement avec impacts détaillés
  - Analyse de sensibilité aux versements mensuels avec ROI
  - Scénario de retraits réguliers pour planification retraite (avec règle des 4%)
  - Impact de l'inflation sur le pouvoir d'achat et rendement réel

## Paramètres de l'Application

| Paramètre | Unité | Description |
| :--- | :--- | :--- |
| **Montant Final** | FCFA | L'objectif d'épargne à atteindre. |
| **Montant Initial** | FCFA | Le capital de départ investi. |
| **Versement Mensuel** | FCFA | La contribution régulière par mois. |
| **Rendement Annualisé** | % | Le taux d'intérêt annuel estimé (par défaut : 5%). |
| **Horizon de Placement** | Années | La durée totale de l'investissement (par défaut : 5 ans). |

## Architecture du Projet

Le projet est organisé en modules distincts pour une meilleure maintenabilité :

```
Simulateur-d-investissement/
├── app.py                        # Point d'entrée principal (page d'accueil)
├── requirements.txt              # Dépendances Python
├── .gitignore                    # Fichiers à exclure du versioning
├── README.md                     # Ce fichier
├── COHERENCE_REPORT.md          # Rapport de cohérence du projet
├── assets/
│   ├── logo.png                 # Logo CGF GESTION (utilisé dans l'app)
│   └── logo cgf gestion.jpeg    # Logo original
├── core/                        # Logique métier et calculs
│   ├── calculations.py          # Fonctions financières (FV, PMT, PV, n)
│   ├── config.py                # Configuration globale et palette de couleurs
│   └── utils.py                 # Utilitaires (formatage monétaire, etc.)
├── pages/                       # Pages de l'application Streamlit
│   ├── 1_Simulation.py          # Page de simulation interactive
│   └── 2_Scénarios_Projections.py  # Page de scénarios et projections avancées
└── ui/                          # Composants d'interface utilisateur
    ├── charts.py                # Graphiques et visualisations
    ├── forms.py                 # Formulaires de saisie
    ├── layout.py                # Mise en page et affichage des résultats
    └── sidebar.py               # Barre latérale de navigation
```

### Description des Modules

#### `core/` - Logique Métier

- **`calculations.py`** : Contient toutes les fonctions de calcul financier
  - `calculate_fv()` : Calcule la valeur future (montant final)
  - `calculate_pmt()` : Calcule le versement mensuel nécessaire
  - `calculate_pv()` : Calcule le montant initial nécessaire
  - `calculate_n_years()` : Calcule l'horizon de placement nécessaire

- **`config.py`** : Configuration centralisée
  - Palette de couleurs de la marque CGF GESTION
  - Constantes globales (nom de l'app, styles CSS)
  - Fonction `get_theme_css()` pour le thème personnalisé

- **`utils.py`** : Fonctions utilitaires
  - `fmt_money()` : Formatage des montants en FCFA
  - Autres utilitaires de formatage et conversion

#### `pages/` - Pages de l'Application

- **`1_Simulation.py`** : Page principale de simulation
  - Formulaire de saisie des paramètres
  - Calcul dynamique du paramètre manquant
  - Affichage des résultats avec graphiques

- **`2_Scénarios_Projections.py`** : Scénarios et projections avancées
  - Charge automatiquement les paramètres depuis la simulation
  - Comparaison intelligente par horizon de placement (adaptatif)
  - Analyse de sensibilité au taux de rendement (avec impact détaillé)
  - Analyse de sensibilité aux versements mensuels (avec ROI)
  - Scénario de retraits réguliers (phase accumulation + phase retrait)
  - Impact de l'inflation sur la valeur réelle du capital

#### `ui/` - Composants UI

- **`sidebar.py`** : Barre latérale avec logo, navigation et informations commerciales
  - Affichage du logo CGF GESTION
  - Formulaires de saisie des informations commerciales (interlocuteur, nom du client)
  - Sélecteur de pays (UEMOA)
  - Section "À propos"
- **`forms.py`** : Formulaires de saisie des paramètres
- **`layout.py`** : Affichage des résultats et mise en page
  - Cartes de métriques avec icônes et couleurs
- **`charts.py`** : Génération des graphiques Altair et visualisations interactives

## Exemples d'Utilisation

### Scénario 1 : Calculer le montant final

**Question client** : "Si je place 500 000 FCFA aujourd'hui et que j'ajoute 50 000 FCFA par mois pendant 10 ans à 5% de rendement annuel, combien aurai-je ?"

**Paramètres** :
- Mode de calcul : **Montant Final**
- Montant Initial : 500 000 FCFA
- Versement Mensuel : 50 000 FCFA
- Rendement : 5%
- Horizon : 10 ans

**Résultat** : L'application calculera automatiquement le montant final et affichera l'évolution du capital avec un graphique interactif.

### Scénario 2 : Calculer le versement mensuel nécessaire

**Question client** : "Je veux avoir 10 000 000 FCFA dans 5 ans. J'ai déjà 1 000 000 FCFA. Combien dois-je épargner par mois ?"

**Paramètres** :
- Mode de calcul : **Versement Mensuel**
- Montant Final : 10 000 000 FCFA
- Montant Initial : 1 000 000 FCFA
- Rendement : 5%
- Horizon : 5 ans

**Résultat** : L'application calculera le versement mensuel nécessaire et affichera également les équivalents trimestriels et annuels.

### Scénario 3 : Calculer l'horizon de placement

**Question client** : "Avec 2 000 000 FCFA de départ et 100 000 FCFA par mois, combien de temps me faudra-t-il pour atteindre 15 000 000 FCFA ?"

**Paramètres** :
- Mode de calcul : **Horizon de Placement**
- Montant Final : 15 000 000 FCFA
- Montant Initial : 2 000 000 FCFA
- Versement Mensuel : 100 000 FCFA
- Rendement : 5%

**Résultat** : L'application calculera le nombre d'années nécessaires.

## Informations Commerciales

Les informations commerciales saisies dans la barre latérale sont :
- **Sauvegardées dans la session** pour éviter de les ressaisir
- **Persistantes** durant toute la navigation dans l'application

Champs disponibles :
- **Date** : Générée automatiquement à la date du jour
- **Interlocuteur (Commercial)** : Nom du commercial CGF GESTION
- **Nom du client** : Nom du client ou prospect
- **Entreprise** : CGF GESTION (fixe)
- **Adresse** : RIVIERA 4, immeuble BRANDON & MCAIN (fixe)
- **Pays** : Sélection parmi les pays de l'UEMOA (Côte d'Ivoire, Bénin, Burkina Faso, etc.)

## Configuration Avancée

### Personnalisation des Couleurs

Les couleurs de l'application sont définies dans `core/config.py` :

```python
PRIMARY_COLOR   = "#114B80"  # Bleu profond
SECONDARY_COLOR = "#567389"  # Bleu-gris
ACCENT_COLOR    = "#ACC7DF"  # Bleu clair
```

Pour changer les couleurs, modifiez ces valeurs dans le fichier de configuration.

### Modification du Logo

Pour utiliser votre propre logo :
1. Placez votre logo dans le dossier `assets/`
2. Nommez-le `logo.png`
3. Format recommandé : PNG avec fond transparent, dimensions 200x200px minimum

### Ajustement des Paramètres par Défaut

Les valeurs par défaut (taux de rendement, horizon, etc.) peuvent être ajustées dans `ui/forms.py`.

## Déploiement

### Déploiement Local

L'application peut être déployée localement comme indiqué dans la section Installation.

### Déploiement sur Streamlit Cloud

1. Créez un compte sur [Streamlit Cloud](https://streamlit.io/cloud)
2. Connectez votre repository GitHub
3. Sélectionnez le fichier `app.py` comme point d'entrée
4. Déployez !

### Déploiement avec Docker

Créez un fichier `Dockerfile` :

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Puis construisez et lancez :

```bash
docker build -t simulateur-investissement .
docker run -p 8501:8501 simulateur-investissement
```

### Déploiement sur Heroku

1. Créez un fichier `setup.sh` :
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

2. Créez un `Procfile` :
```
web: sh setup.sh && streamlit run app.py
```

3. Déployez :
```bash
heroku create
git push heroku main
```

## Développement et Contribution

### Standards de Code

- **Style** : Suivre PEP 8 pour le code Python
- **Documentation** : Toutes les fonctions doivent avoir des docstrings
- **Imports** : Organiser les imports par catégorie (standard, tiers, local)
- **Couleurs** : Toujours utiliser les constantes de `core/config.py`, jamais de valeurs en dur

### Conventions de Nommage

- **Fonctions** : `snake_case`
- **Classes** : `PascalCase`
- **Constantes** : `UPPER_SNAKE_CASE`
- **Fichiers** : `snake_case.py`
- **Pages Streamlit** : `N_Titre_Page.py` (avec préfixe numérique)

### Ajouter une Nouvelle Page

1. Créez un fichier dans `pages/` avec un préfixe numérique : `3_Ma_Page.py`
2. Suivez la structure des pages existantes :
```python
import streamlit as st
from ui.sidebar import display_sidebar
from core.config import get_theme_css, APP_NAME

def main():
    st.set_page_config(page_title="Ma Page | " + APP_NAME, layout="wide")
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    display_sidebar()
    
    # Votre contenu ici
    st.title("Ma Nouvelle Page")

if __name__ == "__main__":
    main()
```

### Ajouter une Nouvelle Fonction de Calcul

1. Ajoutez la fonction dans `core/calculations.py`
2. Écrivez des tests unitaires (recommandé)
3. Documentez la fonction avec une docstring claire
4. Utilisez NumPy pour les calculs mathématiques

### Tests

Bien qu'il n'y ait pas encore de tests automatisés dans le projet, il est recommandé d'ajouter :

```python
# test_calculations.py (à créer)
import pytest
from core.calculations import calculate_fv, calculate_pmt

def test_calculate_fv():
    # Test avec valeurs connues
    result = calculate_fv(pv=1000, pmt=100, rate=5, n_years=1)
    assert result > 0
    assert result > 1000  # Le résultat doit être supérieur au capital initial
```

Pour exécuter les tests (une fois créés) :
```bash
pip install pytest
pytest
```

## Résolution de Problèmes

### L'application ne démarre pas

**Problème** : Erreur "ModuleNotFoundError"
**Solution** : Vérifiez que toutes les dépendances sont installées :
```bash
pip install -r requirements.txt
```

**Problème** : "Logo introuvable"
**Solution** : Vérifiez que le fichier `assets/logo.png` existe. Si vous avez seulement le JPEG, renommez ou convertissez-le.

### Les calculs semblent incorrects

**Problème** : Résultats inattendus
**Solution** : Vérifiez que :
- Le taux de rendement est en pourcentage (5 pour 5%, pas 0.05)
- L'horizon est en années, pas en mois
- Les montants sont positifs

### Les graphiques ne s'affichent pas

**Problème** : Graphiques vides ou erreurs Plotly
**Solution** : 
1. Vérifiez la version de Plotly : `pip install --upgrade plotly`
2. Effacez le cache Streamlit : `streamlit cache clear`

### Problèmes de performances

**Problème** : L'application est lente
**Solution** :
- Utilisez `@st.cache_data` pour les calculs lourds
- Réduisez la granularité des graphiques si nécessaire
- Vérifiez votre connexion internet (pour le CDN de Plotly)

### Erreurs de formatage des montants

**Problème** : Montants mal formatés
**Solution** : Utilisez toujours la fonction `fmt_money()` de `core/utils.py` :
```python
from core.utils import fmt_money
formatted = fmt_money(1000000)  # Retourne "1 000 000 FCFA"
```

## FAQ

**Q : Puis-je utiliser une autre devise que le FCFA ?**
R : Oui, modifiez la fonction `fmt_money()` dans `core/utils.py` pour changer la devise affichée.

**Q : Les calculs sont-ils fiables pour des conseils financiers ?**
R : Les calculs sont basés sur des formules financières standard. Cependant, cet outil est conçu pour l'illustration et la simulation. Pour des conseils financiers personnalisés, consultez toujours un professionnel qualifié.

**Q : Puis-je utiliser des versements autres que mensuels ?**
R : Actuellement, l'application est configurée pour des versements mensuels. Pour d'autres fréquences, vous devrez adapter les fonctions dans `core/calculations.py`.

**Q : Les informations commerciales sont-elles sauvegardées ?**
R : Oui, les informations saisies dans la barre latérale (interlocuteur, nom du client, pays) sont conservées dans la session Streamlit pendant toute la durée de votre utilisation de l'application. Elles ne sont pas sauvegardées sur disque et seront perdues si vous fermez le navigateur.

**Q : Comment signaler un bug ou suggérer une fonctionnalité ?**
R : Contactez directement le développeur (voir section Contact et Support ci-dessous) pour signaler un bug ou suggérer des améliorations.

## Technologies Utilisées

- **[Streamlit](https://streamlit.io/)** (≥1.28.0) - Framework d'application web
- **[Pandas](https://pandas.pydata.org/)** (≥2.0.0) - Manipulation de données
- **[NumPy](https://numpy.org/)** (≥1.24.0) - Calculs numériques
- **[Plotly](https://plotly.com/python/)** (≥5.17.0) - Graphiques interactifs
- **[Altair](https://altair-viz.github.io/)** (≥5.1.0) - Visualisations déclaratives
- **[Pillow](https://pillow.readthedocs.io/)** (≥10.0.0) - Traitement d'images

## Licence

Ce projet est développé pour un usage interne par CGF GESTION. Tous droits réservés.

Pour toute question concernant l'utilisation ou la distribution de ce logiciel, veuillez contacter CGF GESTION.

## Contact et Support

**Développeur** : Dylane Emmanuel Reyane NDOUDY-BAMOUENIZO

**Organisation** : CGF GESTION

Pour toute question, suggestion ou problème technique concernant l'application, veuillez contacter :
- Le développeur via les canaux de communication internes de CGF GESTION
- Le service informatique de CGF GESTION pour le support technique

## Remerciements

- Équipe CGF GESTION pour les spécifications et le feedback
- Communauté Streamlit pour l'excellent framework
- Tous les contributeurs au projet

## Historique des Versions

### Version 1.0.0 (Décembre 2025)
- ✅ Version initiale avec calcul flexible des 4 paramètres
- ✅ Interface utilisateur avec thème CGF GESTION
- ✅ Graphiques interactifs avec Plotly et Altair
- ✅ Page d'analyse avancée avec scénarios de sensibilité
- ✅ Interface moderne avec cartes de métriques
- ✅ Gestion des informations commerciales dans la sidebar
- ✅ Sélection de pays UEMOA
- ✅ Documentation complète

---
*Développé par Dylane Emmanuel Reyane NDOUDY-BAMOUENIZO pour CGF GESTION.*
