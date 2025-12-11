# ui/sidebar.py
# -----------------------------------
# Gère l'affichage complet de la sidebar :
# - Logo CGF Gestion
# - Nom de l'application / sections
# - Informations commerciales
# - À propos
#
# Les couleurs proviennent de `/core/config.py`.

import streamlit as st
from PIL import Image
import base64
import io
from datetime import datetime

from core.config import APP_NAME, PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR


def _load_logo_base64(path: str) -> str:
    """
    Charge une image, la convertit en base64 et la retourne pour affichage HTML.
    """
    try:
        img = Image.open(path)
        img.thumbnail((180, 180))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return img_str
    except Exception:
        return ""


def display_sidebar():
    """
    Affiche la sidebar complète :
    - Logo
    - Nom de l’application
    - Ligne de séparation
    - Section "À propos"
    """

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # ---- LOGO CGF GESTION ----
    img_b64 = _load_logo_base64("assets/logo.png")  # Mets ton fichier ici

    if img_b64:
        st.sidebar.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{img_b64}"
                     style="max-width: 100%; margin-bottom: 14px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.error("⚠️ Logo introuvable dans assets/logo.png")

    # ---- Titre ----
    st.sidebar.markdown(
        f"""
        <h2 style="
            text-align: center;
            color: {PRIMARY_COLOR};
            font-weight: 700;
            margin-top: -5px;">
            {APP_NAME}
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")

    # ---- Informations commerciales ----
    display_commercial_info()
    
    st.sidebar.markdown("---")

    display_about_section()


def display_commercial_info():
    """
    Affiche les informations commerciales et client dans la sidebar.
    """
    st.sidebar.markdown(
        f"""
        <h3 style="color:{PRIMARY_COLOR};">Informations</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Date auto-actualisée
    current_date = datetime.now().strftime("%d/%m/%Y")
    st.sidebar.markdown(f"**📅 Date :** {current_date}")
    
    # Interlocuteur (commercial)
    if "interlocuteur" not in st.session_state:
        st.session_state.interlocuteur = ""
    
    interlocuteur = st.sidebar.text_input(
        "👤 Interlocuteur (Commercial)",
        value=st.session_state.interlocuteur,
        key="interlocuteur_input",
        placeholder="Nom du/de la commercial(e)"
    )
    st.session_state.interlocuteur = interlocuteur
    
    # Nom du client
    if "client_name" not in st.session_state:
        st.session_state.client_name = ""
    
    client_name = st.sidebar.text_input(
        "👥 Nom du client",
        value=st.session_state.client_name,
        key="client_name_input",
        placeholder="Nom du client"
    )
    st.session_state.client_name = client_name
    
    # Entreprise (fixe)
    st.sidebar.markdown("**🏢 Entreprise :** CGF GESTION")
    
    # Adresse (fixe)
    st.sidebar.markdown("**📍 Adresse :** RIVIERA 4, immeuble BRANDON & MCAIN")
    
    # Pays (sélection UEMOA)
    uemoa_countries = [
        "Côte d'Ivoire",
        "Bénin",
        "Burkina Faso",
        "Guinée-Bissau",
        "Mali",
        "Niger",
        "Sénégal",
        "Togo"
    ]
    
    if "country" not in st.session_state:
        st.session_state.country = "Côte d'Ivoire"
    
    country = st.sidebar.selectbox(
        "🌍 Pays",
        options=uemoa_countries,
        index=uemoa_countries.index(st.session_state.country) if st.session_state.country in uemoa_countries else 0,
        key="country_input"
    )
    st.session_state.country = country


def display_about_section():
    """
    Section 'À propos' affichée dans la sidebar.
    """
    st.sidebar.markdown(
        f"""
        <h3 style="color:{PRIMARY_COLOR};">À propos</h3>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.info(
        """
        Cette application permet d'effectuer des **simulations d'investissement**
        afin de déterminer :
        - un **Montant Final**
        - un **Versement Mensuel**
        - un **Montant Initial**
        - un **Horizon de Placement**

        Elle utilise les formules financières standard (annuités, capitalisation mensuelle).
        """
    )

