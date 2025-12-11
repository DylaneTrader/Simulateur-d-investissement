# ui/sidebar.py
# -----------------------------------
# Gère l'affichage complet de la sidebar :
# - Logo CGF Gestion
# - Nom de l'application / sections
# - À propos
#
# Les couleurs proviennent de `/core/config.py`.

import streamlit as st
from PIL import Image
import base64
import io

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

    display_about_section()


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

