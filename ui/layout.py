# ui/layout.py
# ----------------------------------------
# Composants d'affichage du contenu principal
# (résultats, métriques, cartes, graphiques)
#
# Utilise la palette provenant de `core/config.py`

import streamlit as st

from core.config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
from ui.charts import create_simulation_chart


def display_results(inputs: dict, calculation_mode: str):
    """
    Affiche le bloc principal des résultats et appelle le graphique.
    `inputs` : dict contenant les valeurs 'pv', 'pmt', 'fv', 'rate', 'n_years'
    `calculation_mode` : texte (Montant Final, PV, PMT, Horizon)
    """

    st.markdown(
        f"""
        <h2 style="
            color: {PRIMARY_COLOR};
            font-weight: 700;
            margin-top: 10px;">
            Résultats — {calculation_mode}
        </h2>
        """,
        unsafe_allow_html=True
    )

    # On récupère les données déjà calculées en amont
    pv = inputs.get("pv", 0)
    pmt = inputs.get("pmt", 0)
    fv = inputs.get("fv", 0)
    rate = inputs.get("rate", 0)
    n_years = inputs.get("n_years", 0)

    # ----------- BLOC DES MÉTRIQUES -----------
    st.markdown(
        f"""
        <div class="accent-bg" style="
            background:{ACCENT_COLOR}33;
            padding:12px;
            border-radius:10px;
            margin-top: 15px;
            ">
            <h4 style="color:{PRIMARY_COLOR}; margin-bottom:6px;">
                Paramètres actuels
            </h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Montant Initial", f"{pv:,.0f} FCFA")
    with col2:
        st.metric("Versement Mensuel", f"{pmt:,.0f} FCFA")
    with col3:
        st.metric("Rendement", f"{rate:.2f} %")
    with col4:
        st.metric("Horizon (années)", f"{n_years}")

    st.markdown("---")

    # ----------- BLOC DU GRAPHIQUE -----------
    st.markdown(
        f"""
        <h3 style="color:{PRIMARY_COLOR};">Évolution du portefeuille</h3>
        """,
        unsafe_allow_html=True
    )

    # Graphique principal
    create_simulation_chart(
        pv=pv,
        pmt=pmt,
        rate=rate,
        n_years=n_years,
        fv_target=inputs.get("fv")
    )

