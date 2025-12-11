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
*   **Visualisation Interactive** : Utilisation de Plotly pour des graphiques dynamiques montrant l'évolution de la valeur totale, du capital investi et des intérêts accumulés au fil du temps.
*   **Aide à la Vente** : Pour le calcul du **Versement Mensuel**, l'application affiche automatiquement les cotisations équivalentes par mois, par trimestre et par année, facilitant la discussion avec le client sur ses capacités d'épargne.
*   **Cohérence de Marque** : Intégration du logo et des couleurs de la marque pour une présentation professionnelle.

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

Assurez-vous d'avoir les librairies nécessaires :

```bash
pip install streamlit pandas numpy plotly Pillow
```

### 2. Exécution de l'Application

1.  Enregistrez le code Python fourni (`app.py`) dans un fichier.
2.  Placez le fichier du logo (`1631360014014.jpeg`) dans le même répertoire (ou mettez à jour le chemin dans `app.py`).
3.  Lancez l'application via votre terminal :

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur web.

## Paramètres de l'Application

| Paramètre | Unité | Description |
| :--- | :--- | :--- |
| **Montant Final** | FCFA | L'objectif d'épargne à atteindre. |
| **Montant Initial** | FCFA | Le capital de départ investi. |
| **Versement Mensuel** | FCFA | La contribution régulière par mois. |
| **Rendement Annualisé** | % | Le taux d'intérêt annuel estimé (par défaut : 5%). |
| **Horizon de Placement** | Années | La durée totale de l'investissement (par défaut : 5 ans). |

---
*Développé par Dylane Emmanuel Reyane NDOUDY-BAMOUENIZO pour CGF GESTION.*
