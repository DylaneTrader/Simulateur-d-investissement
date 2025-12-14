# pages/2_Analyse.py
# ------------------------------------------------------------
# Page d'analyse avancée pour clients expérimentés :
#   - Comparaison plusieurs horizons de placement
#   - Sensibilité au taux
#   - Sensibilité aux versements
#   - Scénarios de retraits réguliers
#   - Analyses et visualisations avancées
#
# Utilise Altair pour les visualisations.
# ------------------------------------------------------------

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

from ui.sidebar import display_sidebar
from core.config import (
    get_theme_css, 
    PRIMARY_COLOR, 
    SECONDARY_COLOR, 
    ACCENT_COLOR, 
    APP_NAME,
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_MONTHLY_PAYMENT,
    DEFAULT_ANNUAL_RATE,
    DEFAULT_HORIZON_YEARS
)
from core.calculations import calculate_fv
from core.utils import fmt_money


def simulate_series(pv, pmt, rate, horizons):
    """Retourne un DataFrame contenant FV pour plusieurs horizons."""
    rows = []
    for n in horizons:
        fv = calculate_fv(pv, pmt, rate, n)
        rows.append({"Horizon": n, "FV": fv})
    return pd.DataFrame(rows)


def simulate_rate_sensitivity(pv, pmt, n_years, rates):
    """Sensibilité aux taux."""
    rows = []
    for r in rates:
        fv = calculate_fv(pv, pmt, r, n_years)
        rows.append({"Rendement (%)": r, "FV": fv})
    return pd.DataFrame(rows)


def simulate_pmt_sensitivity(pv, rate, n_years, pmt_values):
    """Sensibilité aux versements mensuels."""
    rows = []
    for p in pmt_values:
        fv = calculate_fv(pv, p, rate, n_years)
        rows.append({"Versement Mensuel": p, "FV": fv})
    return pd.DataFrame(rows)


def simulate_withdrawal_scenario(pv, pmt, rate, accumulation_years, withdrawal_monthly, withdrawal_years):
    """
    Simule un scénario avec phase d'accumulation puis phase de retrait.
    
    Phase 1 (accumulation) : pv + pmt réguliers pendant accumulation_years
    Phase 2 (retrait) : retraits réguliers de withdrawal_monthly pendant withdrawal_years
    
    Retourne un DataFrame avec l'évolution du capital.
    """
    rate_m = rate / 100 / 12
    data = []
    
    # Phase d'accumulation
    value = pv
    for month in range(int(accumulation_years * 12)):
        value = value * (1 + rate_m) + pmt
        data.append({
            "Mois": month,
            "Année": month / 12,
            "Capital": value,
            "Phase": "Accumulation"
        })
    
    # Phase de retrait
    accumulated_capital = value
    offset_months = int(accumulation_years * 12)
    
    for month in range(int(withdrawal_years * 12)):
        value = value * (1 + rate_m) - withdrawal_monthly
        if value < 0:
            value = 0  # Le capital est épuisé
        
        data.append({
            "Mois": offset_months + month,
            "Année": (offset_months + month) / 12,
            "Capital": value,
            "Phase": "Retrait"
        })
    
    return pd.DataFrame(data), accumulated_capital


def simulate_inflation_impact(pv, pmt, rate, n_years, inflation_rate):
    """
    Compare la valeur nominale vs valeur réelle (ajustée de l'inflation).
    """
    rate_m = rate / 100 / 12
    inflation_m = inflation_rate / 100 / 12
    
    data = []
    value_nominal = pv
    
    for month in range(int(n_years * 12) + 1):
        if month > 0:
            value_nominal = value_nominal * (1 + rate_m) + pmt
        
        # Valeur réelle = valeur nominale déflatée
        value_real = value_nominal / ((1 + inflation_m) ** month)
        
        data.append({
            "Année": month / 12,
            "Valeur Nominale": value_nominal,
            "Valeur Réelle": value_real
        })
    
    return pd.DataFrame(data)


def main():
    st.set_page_config(page_title="Analyse | " + APP_NAME, layout="wide")
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    display_sidebar()

    st.markdown(
        f"""
        <h1 style="color:{PRIMARY_COLOR};">📊 Analyse Avancée</h1>
        <p style="font-size: 16px; color: #666;">
        Section destinée aux clients expérimentés : explorez différents scénarios d'investissement, 
        de retrait, et analysez l'impact de multiples variables sur votre patrimoine.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # -------------------------------
    # PARAMÈTRES DE BASE POUR L'ANALYSE
    # -------------------------------
    st.markdown(f"### 🎯 Paramètres de base")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pv = st.number_input("Montant initial (FCFA)", value=DEFAULT_INITIAL_CAPITAL, step=10_000, format="%d")
    with col2:
        pmt = st.number_input("Versement mensuel (FCFA)", value=DEFAULT_MONTHLY_PAYMENT, step=5_000, format="%d")
    with col3:
        rate = st.number_input("Rendement annuel (%)", value=DEFAULT_ANNUAL_RATE, step=0.1, format="%.2f")
    with col4:
        n_years = st.number_input("Horizon (années)", value=DEFAULT_HORIZON_YEARS, step=1, format="%d")

    st.markdown("---")

    # ============================================================
    # 1) COMPARAISON PAR HORIZON
    # ============================================================
    with st.expander("📊 Comparaison par horizon de placement", expanded=True):
        
        st.markdown(
            """
            **💡 Commentaire :** Cette analyse montre l'effet du temps sur votre investissement. 
            Plus l'horizon est long, plus l'effet des intérêts composés est significatif.
            """
        )

        horizons = [5, 10, 15, 20]
        df = simulate_series(pv, pmt, rate, horizons)

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("Horizon:O", title="Horizon (années)"),
                y=alt.Y("FV:Q", title="Valeur Future (FCFA)"),
                color=alt.value(PRIMARY_COLOR),
                tooltip=[
                    alt.Tooltip("Horizon:O"),
                    alt.Tooltip("FV:Q", format=",.0f", title="Valeur Future")
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart, use_container_width=True)
        
        # Tableau récapitulatif
        st.markdown("**📋 Tableau récapitulatif :**")
        df_display = df.copy()
        df_display["FV"] = df_display["FV"].apply(lambda x: f"{x:,.0f} FCFA")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ============================================================
    # 2) SENSIBILITÉ AUX TAUX
    # ============================================================
    with st.expander("📈 Analyse de sensibilité aux taux de rendement"):
        
        st.markdown(
            """
            **💡 Commentaire :** Cette analyse illustre l'importance du taux de rendement. 
            Une différence de 1-2% peut avoir un impact majeur sur le capital final, 
            surtout sur des horizons longs.
            """
        )

        rates = [rate - 1, rate, rate + 1, rate + 2]
        rates = [r for r in rates if r > 0]
        df_r = simulate_rate_sensitivity(pv, pmt, n_years, rates)

        chart_r = (
            alt.Chart(df_r)
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("Rendement (%):Q", title="Taux de rendement annuel (%)"),
                y=alt.Y("FV:Q", title="Valeur Future (FCFA)"),
                color=alt.value(SECONDARY_COLOR),
                tooltip=[
                    alt.Tooltip("Rendement (%):Q", format=".2f"),
                    alt.Tooltip("FV:Q", format=",.0f", title="Valeur Future"),
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart_r.interactive(), use_container_width=True)

    # ============================================================
    # 3) SENSIBILITÉ AUX VERSEMENTS
    # ============================================================
    with st.expander("💵 Sensibilité aux versements mensuels"):
        
        st.markdown(
            """
            **💡 Commentaire :** Cette analyse démontre l'impact d'augmenter vos versements mensuels. 
            Doubler les versements peut plus que doubler le capital final grâce aux intérêts composés.
            """
        )

        pmt_values = [pmt * x for x in [0.5, 1, 1.5, 2]]
        df_p = simulate_pmt_sensitivity(pv, rate, n_years, pmt_values)

        chart_p = (
            alt.Chart(df_p)
            .mark_bar()
            .encode(
                x=alt.X("Versement Mensuel:O", title="Versement Mensuel (FCFA)"),
                y=alt.Y("FV:Q", title="Valeur Future (FCFA)"),
                color=alt.value(PRIMARY_COLOR),
                tooltip=[
                    alt.Tooltip("Versement Mensuel:O", format=",.0f"),
                    alt.Tooltip("FV:Q", format=",.0f", title="Valeur Future")
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart_p, use_container_width=True)

    # ============================================================
    # 4) SCÉNARIO DE RETRAITS RÉGULIERS
    # ============================================================
    with st.expander("🏦 Scénario de retraits réguliers (Phase d'accumulation + Phase de retrait)"):
        
        st.markdown(
            """
            **💡 Commentaire :** Ce scénario est idéal pour planifier une retraite ou des revenus futurs. 
            Il montre combien de temps votre capital peut soutenir des retraits réguliers après 
            une phase d'accumulation. Ajustez les paramètres pour optimiser votre stratégie.
            """
        )
        
        col1, col2 = st.columns(2)
        with col1:
            accum_years = st.number_input(
                "Durée d'accumulation (années)",
                value=15,
                min_value=1,
                max_value=50,
                step=1,
                key="accum_years"
            )
        with col2:
            withdrawal_years = st.number_input(
                "Durée des retraits (années)",
                value=10,
                min_value=1,
                max_value=50,
                step=1,
                key="withdrawal_years"
            )
        
        withdrawal_monthly = st.number_input(
            "Retrait mensuel souhaité (FCFA)",
            value=100_000,
            step=10_000,
            format="%d",
            key="withdrawal_monthly"
        )
        
        df_withdrawal, accumulated = simulate_withdrawal_scenario(
            pv, pmt, rate, accum_years, withdrawal_monthly, withdrawal_years
        )
        
        # Graphique
        color_scale = alt.Scale(
            domain=["Accumulation", "Retrait"],
            range=[PRIMARY_COLOR, SECONDARY_COLOR]
        )
        
        chart_withdrawal = (
            alt.Chart(df_withdrawal)
            .mark_line(strokeWidth=3)
            .encode(
                x=alt.X("Année:Q", title="Années"),
                y=alt.Y("Capital:Q", title="Capital (FCFA)"),
                color=alt.Color("Phase:N", scale=color_scale),
                tooltip=[
                    alt.Tooltip("Année:Q", format=".1f"),
                    alt.Tooltip("Capital:Q", format=",.0f"),
                    alt.Tooltip("Phase:N")
                ]
            )
            .properties(height=400)
        )
        
        st.altair_chart(chart_withdrawal, use_container_width=True)
        
        # Métriques importantes
        final_capital = df_withdrawal.iloc[-1]["Capital"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Capital accumulé", fmt_money(accumulated))
        with col2:
            st.metric("Total des retraits", fmt_money(withdrawal_monthly * withdrawal_years * 12))
        with col3:
            if final_capital > 0:
                st.metric("Capital restant", fmt_money(final_capital), delta="✅ Viable")
            else:
                st.metric("Capital restant", fmt_money(0), delta="⚠️ Épuisé")
        
        if final_capital <= 0:
            st.warning(
                "⚠️ **Attention :** Votre capital sera épuisé avant la fin de la période de retrait. "
                "Considérez d'augmenter la période d'accumulation, réduire les retraits, ou améliorer le rendement."
            )

    # ============================================================
    # 5) IMPACT DE L'INFLATION
    # ============================================================
    with st.expander("📉 Impact de l'inflation sur la valeur réelle"):
        
        st.markdown(
            """
            **💡 Commentaire :** L'inflation érode le pouvoir d'achat de votre capital. 
            Cette analyse compare la valeur nominale (en FCFA courants) à la valeur réelle 
            (pouvoir d'achat constant). Assurez-vous que votre rendement dépasse l'inflation.
            """
        )
        
        inflation_rate = st.slider(
            "Taux d'inflation annuel moyen (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.5,
            step=0.1,
            key="inflation_rate"
        )
        
        df_inflation = simulate_inflation_impact(pv, pmt, rate, n_years, inflation_rate)
        
        # Graphique comparatif
        df_inflation_melted = df_inflation.melt(
            id_vars=["Année"],
            value_vars=["Valeur Nominale", "Valeur Réelle"],
            var_name="Type",
            value_name="Valeur"
        )
        
        chart_inflation = (
            alt.Chart(df_inflation_melted)
            .mark_line(strokeWidth=3)
            .encode(
                x=alt.X("Année:Q", title="Années"),
                y=alt.Y("Valeur:Q", title="Capital (FCFA)"),
                color=alt.Color(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["Valeur Nominale", "Valeur Réelle"],
                        range=[PRIMARY_COLOR, ACCENT_COLOR]
                    )
                ),
                strokeDash=alt.StrokeDash(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["Valeur Nominale", "Valeur Réelle"],
                        range=[[1, 0], [5, 5]]
                    )
                ),
                tooltip=[
                    alt.Tooltip("Année:Q", format=".1f"),
                    alt.Tooltip("Valeur:Q", format=",.0f"),
                    alt.Tooltip("Type:N")
                ]
            )
            .properties(height=400)
        )
        
        st.altair_chart(chart_inflation, use_container_width=True)
        
        # Calcul de la perte de pouvoir d'achat
        final_nominal = df_inflation.iloc[-1]["Valeur Nominale"]
        final_real = df_inflation.iloc[-1]["Valeur Réelle"]
        purchasing_power_loss = ((final_nominal - final_real) / final_nominal * 100) if final_nominal > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Valeur nominale finale", fmt_money(final_nominal))
        with col2:
            st.metric("Valeur réelle finale", fmt_money(final_real))
        with col3:
            st.metric("Perte de pouvoir d'achat", f"{purchasing_power_loss:.1f}%", delta=f"-{purchasing_power_loss:.1f}%")
        
        # Recommandation
        real_return = rate - inflation_rate
        if real_return > 2:
            st.success(
                f"✅ **Bon rendement réel** : Votre rendement ({rate}%) dépasse largement l'inflation "
                f"({inflation_rate}%), avec un rendement réel de {real_return:.1f}%."
            )
        elif real_return > 0:
            st.info(
                f"ℹ️ **Rendement réel positif** : Votre rendement ({rate}%) dépasse l'inflation "
                f"({inflation_rate}%), mais modestement. Rendement réel : {real_return:.1f}%."
            )
        else:
            st.error(
                f"⚠️ **Attention** : Votre rendement ({rate}%) ne couvre pas l'inflation "
                f"({inflation_rate}%). Vous perdez du pouvoir d'achat avec un rendement réel de {real_return:.1f}%."
            )


if __name__ == "__main__":
    main()
