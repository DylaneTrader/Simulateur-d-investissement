# ui/forms.py
# ---------------------------------------------------------
# Gère toute la logique d'affichage des formulaires utilisateur :
# - choix du paramètre à calculer
# - saisie des valeurs (pv, fv, pmt, rate, n_years)
#
# Retourne :
#   inputs : dict propre contenant toutes les valeurs saisies
#   calculation_mode : str ("Montant Final", etc.)
# ---------------------------------------------------------

import streamlit as st
from core.config import PRIMARY_COLOR


def parameter_form():
    """
    Affiche le formulaire complet de paramétrage.
    Retourne :
        - inputs : dict des paramètres
        - calculation_mode : str du paramètre ciblé
    """

    st.markdown(
        f"""
        <h2 style="color:{PRIMARY_COLOR}; margin-bottom:8px;">
            Paramètres de la simulation
        </h2>
        """,
        unsafe_allow_html=True
    )

    # -------- MODE DE CALCUL --------
    calculation_mode = st.radio(
        "Quel paramètre souhaitez-vous déterminer ?",
        ("Montant Final", "Versement Mensuel", "Montant Initial", "Horizon de Placement"),
        horizontal=True
    )

    st.markdown("---")

    inputs = {}

    # -------- SAISIES --------

    # FV
    if calculation_mode != "Montant Final":
        inputs["fv"] = st.number_input(
            "Montant Final (Objectif en FCFA)",
            value=10_000_000,
            step=100_000,
            format="%d",
        )
    else:
        inputs["fv"] = 0

    # PV
    if calculation_mode != "Montant Initial":
        inputs["pv"] = st.number_input(
            "Montant Initial (Capital de départ)",
            value=100_000,
            step=10_000,
            format="%d",
        )
    else:
        inputs["pv"] = 0

    # PMT
    if calculation_mode != "Versement Mensuel":
        inputs["pmt"] = st.number_input(
            "Versement Mensuel (Contribution régulière)",
            value=50_000,
            step=5_000,
            format="%d",
        )
    else:
        inputs["pmt"] = 0

    # RATE
    rate_input = st.number_input(
        "Rendement Annualisé (en %)",
        value=5.0,
        step=0.1,
        format="%.2f",
    )
    inputs["rate"] = rate_input

    # HORIZON
    if calculation_mode != "Horizon de Placement":
        inputs["n_years"] = st.number_input(
            "Horizon de Placement (en années)",
            min_value=1,
            value=5,
            step=1,
            format="%d",
        )
    else:
        inputs["n_years"] = 0

    st.markdown("---")

    return inputs, calculation_mode
