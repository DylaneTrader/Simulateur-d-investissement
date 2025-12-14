# app.py
# ============================================================
# Point d'entrée principal du Simulateur d'Investissement
# Application Streamlit multi-pages pour CGF GESTION
# ============================================================

import streamlit as st
from ui.sidebar import display_sidebar
from core.config import get_theme_css, APP_NAME, PRIMARY_COLOR

# Charger les variables d'environnement depuis .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv n'est pas installé, on utilise les variables système

# Configuration de la page principale
st.set_page_config(
    page_title=APP_NAME,
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Appliquer le thème CSS personnalisé
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Afficher la sidebar
display_sidebar()

# Contenu de la page d'accueil
st.markdown(
    f"""
    <h1 style='color: {PRIMARY_COLOR}; text-align: center;'>
        Bienvenue sur le Simulateur d'Investissement
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Description de l'application
st.markdown(
    """
    ## 🎯 À propos de cette application
    
    Ce simulateur d'investissement est conçu spécifiquement pour les **commerciaux de CGF GESTION** 
    afin de faciliter la présentation de simulations financières aux clients.
    
    ### 📊 Fonctionnalités principales
    
    L'application permet de calculer de manière flexible l'un des quatre paramètres suivants 
    en fonction des trois autres :
    
    1. **Montant Final (Objectif)** - Le capital que vous souhaitez atteindre
    2. **Versement Mensuel (Contribution)** - Votre épargne régulière
    3. **Montant Initial (Capital de départ)** - Votre investissement de départ
    4. **Horizon de Placement (Durée)** - Le temps nécessaire pour atteindre votre objectif
    
    ### 🚀 Comment utiliser l'application
    
    Utilisez le menu de navigation dans la barre latérale pour accéder aux différentes sections :
    
    - **Simulation** : Effectuez vos calculs d'investissement personnalisés
    - **Scénarios & Projections** : Explorez des scénarios avancés et analyses de sensibilité
    
    ### 📈 Modèle Financier
    
    Le simulateur repose sur la formule de la **Valeur Future d'une Annuité**, 
    qui modélise la croissance d'un capital initial avec des versements périodiques réguliers, 
    soumis à un taux de rendement annualisé.
    
    ---
    
    *Développé par Dylane Emmanuel Reyane NDOUDY-BAMOUENIZO pour CGF GESTION.*
    """
)

st.markdown("---")

# Statistiques rapides ou informations supplémentaires
col1, col2, col3 = st.columns(3)

with col1:
    st.info("💼 **Outil Professionnel**\n\nConçu pour les commerciaux CGF GESTION")

with col2:
    st.info("🧮 **Calculs Précis**\n\nFormules financières validées")

with col3:
    st.info("📊 **Visualisations**\n\nGraphiques interactifs avec Plotly")
