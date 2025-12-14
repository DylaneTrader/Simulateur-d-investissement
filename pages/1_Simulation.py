# pages/1_Simulation.py
# ------------------------------------------------------------
# Page principale : Simulateur d'investissement
#
# Utilise :
#   - ui.sidebar.display_sidebar()
#   - ui.forms.parameter_form()
#   - ui.layout.display_results()
#
# ------------------------------------------------------------

import streamlit as st

from ui.sidebar import display_sidebar
from ui.forms import parameter_form
from ui.layout import display_results
from core.config import get_theme_css, APP_NAME


def main():
    # ---- Configuration générale ----
    st.set_page_config(page_title="Simulation | " + APP_NAME, layout="wide")
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    
    # ---- Initialize session state for simulation results ----
    # Using None instead of {} to properly distinguish between "not yet initialized" and "no simulation run"
    # This ensures pages can accurately detect if a simulation has been performed
    if "simulation_results" not in st.session_state:
        st.session_state.simulation_results = None

    # ---- Sidebar ----
    display_sidebar()

    st.markdown(
        "<h1 style='margin-bottom: 5px;'>Simulateur d'investissement</h1>",
        unsafe_allow_html=True
    )
    st.markdown("<p>Calculez un paramètre clé en fonction des autres.</p>", unsafe_allow_html=True)

    # ---- Formulaire ----
    inputs, calculation_mode = parameter_form()

    # Bouton Lancer
    if st.button("Lancer la simulation", type="primary"):
        display_results(inputs, calculation_mode)


if __name__ == "__main__":
    main()
