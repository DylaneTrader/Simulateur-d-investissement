# ui/layout.py
# ----------------------------------------
# Composants d'affichage du contenu principal
# (résultats, métriques, cartes, graphiques)
#
# Utilise la palette provenant de `core/config.py`

import math
import streamlit as st

from core.config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
from core.calculations import calculate_fv, calculate_pmt, calculate_pv, calculate_n_years
from core.utils import fmt_money
from ui.charts import create_simulation_chart


def display_results(inputs: dict, calculation_mode: str):
    """
    Affiche le bloc principal des résultats et appelle le graphique.
    `inputs` : dict contenant les valeurs 'pv', 'pmt', 'fv', 'rate', 'n_years'
    `calculation_mode` : texte (Montant Final, PV, PMT, Horizon)
    """

    # On récupère les données
    pv = inputs.get("pv", 0)
    pmt = inputs.get("pmt", 0)
    fv = inputs.get("fv", 0)
    rate = inputs.get("rate", 0)
    n_years = inputs.get("n_years", 0)

    # -------- CALCUL DU PARAMÈTRE MANQUANT --------
    calculated_value = None
    
    try:
        if calculation_mode == "Montant Final":
            calculated_value = calculate_fv(pv, pmt, rate, n_years)
            fv = calculated_value
            result_text = f"Montant Final calculé : **{fmt_money(calculated_value)}**"
            
        elif calculation_mode == "Versement Mensuel":
            calculated_value = calculate_pmt(fv, pv, rate, n_years)
            pmt = calculated_value
            result_text = f"Versement Mensuel calculé : **{fmt_money(calculated_value)}**"
            
            # Afficher aussi les équivalents trimestriels et annuels
            pmt_quarterly = calculated_value * 3
            pmt_yearly = calculated_value * 12
            result_text += f"\n\n*Équivalents :*\n- Par trimestre : {fmt_money(pmt_quarterly)}\n- Par an : {fmt_money(pmt_yearly)}"
            
        elif calculation_mode == "Montant Initial":
            calculated_value = calculate_pv(fv, pmt, rate, n_years)
            pv = calculated_value
            result_text = f"Montant Initial calculé : **{fmt_money(calculated_value)}**"
            
        elif calculation_mode == "Horizon de Placement":
            calculated_value = calculate_n_years(fv, pv, pmt, rate)
            n_years = calculated_value
            
            if not math.isfinite(calculated_value):
                result_text = "⚠️ **Impossible d'atteindre l'objectif** avec ces paramètres (horizon infini requis)"
            else:
                years = int(calculated_value)
                months = int((calculated_value - years) * 12)
                result_text = f"Horizon de Placement calculé : **{years} ans et {months} mois** ({calculated_value:.2f} années)"
        
        else:
            st.error("Mode de calcul non reconnu")
            return

    except Exception as e:
        st.error(f"Erreur lors du calcul : {str(e)}")
        return

    # -------- AFFICHAGE DU RÉSULTAT --------
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

    # Affichage du résultat calculé dans une boîte mise en évidence
    st.success(result_text)

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

