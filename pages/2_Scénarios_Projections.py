# pages/2_Scénarios_Projections.py
# ------------------------------------------------------------
# Page de scénarios avancés et projections pour clients expérimentés :
#   - Comparaison plusieurs horizons de placement
#   - Sensibilité au taux
#   - Sensibilité aux versements
#   - Scénarios de retraits réguliers
#   - Impact de l'inflation
#   - Analyses et visualisations avancées
#
# Cette page peut utiliser les résultats de la simulation ou 
# fonctionner de manière indépendante avec des paramètres personnalisés.
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
    st.set_page_config(page_title="Scénarios & Projections | " + APP_NAME, layout="wide")
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    display_sidebar()
    
    # ---- Initialize session state for simulation results ----
    # Use None instead of {} to properly detect absence of simulation
    if "simulation_results" not in st.session_state:
        st.session_state.simulation_results = None

    st.markdown(
        f"""
        <h1 style="color:{PRIMARY_COLOR};">🎯 Scénarios & Projections</h1>
        <p style="font-size: 16px; color: #666;">
        Explorez différents scénarios d'investissement, analysez l'impact des variations de paramètres, 
        et planifiez votre stratégie financière à long terme avec des projections détaillées.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    
    # -------------------------------
    # RÉCUPÉRATION DES RÉSULTATS DE SIMULATION
    # -------------------------------
    simulation_results = st.session_state.get('simulation_results', None)
    has_simulation_results = (
        simulation_results is not None 
        and isinstance(simulation_results, dict) 
        and len(simulation_results) > 0
    )
    
    # Déterminer les valeurs par défaut
    if has_simulation_results:
        default_pv = int(simulation_results.get('pv', DEFAULT_INITIAL_CAPITAL))
        default_pmt = int(simulation_results.get('pmt', DEFAULT_MONTHLY_PAYMENT))
        default_rate = float(simulation_results.get('rate', DEFAULT_ANNUAL_RATE))
        default_n_years = int(simulation_results.get('n_years', DEFAULT_HORIZON_YEARS))
        
        # Afficher un message informatif
        st.info(
            f"✅ **Paramètres chargés depuis votre simulation précédente.**\n\n"
            f"Mode de calcul utilisé : *{simulation_results.get('calculation_mode', 'N/A')}*. "
            f"Vous pouvez modifier les paramètres ci-dessous pour explorer d'autres scénarios."
        )
    else:
        default_pv = DEFAULT_INITIAL_CAPITAL
        default_pmt = DEFAULT_MONTHLY_PAYMENT
        default_rate = DEFAULT_ANNUAL_RATE
        default_n_years = DEFAULT_HORIZON_YEARS
        
        st.warning(
            "ℹ️ **Aucune simulation détectée.**\n\n"
            "Vous pouvez utiliser cette page indépendamment en définissant vos propres paramètres, "
            "ou retourner à la page **Simulation** pour effectuer un calcul d'abord."
        )

    # -------------------------------
    # PARAMÈTRES DE BASE POUR L'ANALYSE
    # -------------------------------
    st.markdown(f"### 🎯 Paramètres de base pour les projections")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pv = st.number_input("Montant initial (FCFA)", value=default_pv, step=10_000, format="%d", key="proj_pv")
    with col2:
        pmt = st.number_input("Versement mensuel (FCFA)", value=default_pmt, step=5_000, format="%d", key="proj_pmt")
    with col3:
        rate = st.number_input("Rendement annuel (%)", value=default_rate, step=0.1, format="%.2f", key="proj_rate")
    with col4:
        n_years = st.number_input("Horizon (années)", value=default_n_years, step=1, format="%d", min_value=1, key="proj_n_years")

    st.markdown("---")

    # ============================================================
    # 1) COMPARAISON PAR HORIZON INTELLIGENT
    # ============================================================
    with st.expander("📊 Comparaison par horizon de placement", expanded=True):
        
        st.markdown(
            """
            **💡 Commentaire :** Cette analyse montre l'effet du temps sur votre investissement. 
            Plus l'horizon est long, plus l'effet des intérêts composés est significatif.
            """
        )
        
        # Générer des horizons adaptés à la valeur actuelle de n_years
        # On crée une progression intelligente autour de n_years
        base_horizons = [
            max(1, n_years // 2),  # La moitié
            n_years,                # Actuel
            int(n_years * 1.5),    # 1.5x
            n_years * 2             # Double
        ]
        horizons = sorted(set(base_horizons))  # Enlever les doublons et trier

        df = simulate_series(pv, pmt, rate, horizons)
        
        # Calculer les gains additionnels entre chaque horizon
        df['Gain vs Précédent'] = df['FV'].diff()
        df['% Croissance'] = df['FV'].pct_change() * 100

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("Horizon:O", title="Horizon (années)"),
                y=alt.Y("FV:Q", title="Valeur Future (FCFA)"),
                color=alt.condition(
                    alt.datum.Horizon == n_years,
                    alt.value(ACCENT_COLOR),  # Couleur différente pour l'horizon actuel
                    alt.value(PRIMARY_COLOR)
                ),
                tooltip=[
                    alt.Tooltip("Horizon:O", title="Horizon"),
                    alt.Tooltip("FV:Q", format=",.0f", title="Valeur Future")
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart, use_container_width=True)
        
        # Tableau récapitulatif amélioré
        st.markdown("**📋 Tableau récapitulatif détaillé :**")
        df_display = df.copy()
        df_display["Valeur Future"] = df_display["FV"].apply(lambda x: f"{x:,.0f} FCFA")
        df_display["Gain additionnel"] = df_display["Gain vs Précédent"].apply(
            lambda x: f"{x:,.0f} FCFA" if pd.notna(x) else "—"
        )
        df_display["Croissance"] = df_display["% Croissance"].apply(
            lambda x: f"+{x:.1f}%" if pd.notna(x) else "—"
        )
        df_display = df_display[["Horizon", "Valeur Future", "Gain additionnel", "Croissance"]]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Insight intelligent
        if len(df) >= 2:
            doubling_time = horizons[-1] - horizons[0]
            value_increase = df.iloc[-1]["FV"] / df.iloc[0]["FV"]
            st.info(
                f"📈 **Insight :** En passant de {horizons[0]} à {horizons[-1]} ans (+{doubling_time} ans), "
                f"votre capital est multiplié par **{value_increase:.2f}x**, "
                f"démontrant la puissance des intérêts composés sur le long terme."
            )

    # ============================================================
    # 2) SENSIBILITÉ AUX TAUX AMÉLIORÉE
    # ============================================================
    with st.expander("📈 Analyse de sensibilité aux taux de rendement"):
        
        st.markdown(
            """
            **💡 Commentaire :** Cette analyse illustre l'importance du taux de rendement. 
            Une différence de 1-2% peut avoir un impact majeur sur le capital final, 
            surtout sur des horizons longs.
            """
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Plage d'analyse :**")
        with col2:
            rate_range = st.slider(
                "Écart de taux (+/-)",
                min_value=0.5,
                max_value=5.0,
                value=2.0,
                step=0.5,
                key="rate_range_slider"
            )
        
        # Générer une plage de taux intelligente
        rates = [
            max(0.1, rate - rate_range),
            max(0.1, rate - rate_range/2),
            rate,
            rate + rate_range/2,
            rate + rate_range
        ]
        rates = sorted([round(r, 2) for r in rates])
        df_r = simulate_rate_sensitivity(pv, pmt, n_years, rates)
        
        # Calculer l'impact en FCFA et en %
        current_fv = df_r[df_r["Rendement (%)"] == rate]["FV"].iloc[0] if rate in df_r["Rendement (%)"].values else None
        if current_fv:
            df_r["Écart vs Actuel"] = df_r["FV"] - current_fv
            df_r["% Impact"] = (df_r["FV"] / current_fv - 1) * 100

        chart_r = (
            alt.Chart(df_r)
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("Rendement (%):Q", title="Taux de rendement annuel (%)"),
                y=alt.Y("FV:Q", title="Valeur Future (FCFA)"),
                color=alt.value(SECONDARY_COLOR),
                tooltip=[
                    alt.Tooltip("Rendement (%):Q", format=".2f", title="Taux"),
                    alt.Tooltip("FV:Q", format=",.0f", title="Valeur Future"),
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart_r.interactive(), use_container_width=True)
        
        # Tableau avec impact détaillé
        if current_fv:
            st.markdown("**📋 Impact détaillé par taux :**")
            df_display = df_r.copy()
            df_display["Taux"] = df_display["Rendement (%)"].apply(lambda x: f"{x:.2f}%")
            df_display["Valeur Future"] = df_display["FV"].apply(lambda x: f"{x:,.0f} FCFA")
            df_display["Écart"] = df_display["Écart vs Actuel"].apply(
                lambda x: f"{x:+,.0f} FCFA" if pd.notna(x) else "—"
            )
            df_display["Impact"] = df_display["% Impact"].apply(
                lambda x: f"{x:+.1f}%" if pd.notna(x) else "—"
            )
            df_display = df_display[["Taux", "Valeur Future", "Écart", "Impact"]]
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Insight sur la sensibilité
            min_fv = df_r["FV"].min()
            max_fv = df_r["FV"].max()
            fv_variation = max_fv - min_fv
            st.warning(
                f"⚠️ **Sensibilité élevée :** Une variation de ±{rate_range}% du taux de rendement "
                f"peut faire varier votre capital final de **{fv_variation:,.0f} FCFA** "
                f"({(fv_variation/current_fv*100):.1f}% du montant actuel). "
                f"Choisissez un placement avec un taux stable et fiable !"
            )

    # ============================================================
    # 3) SENSIBILITÉ AUX VERSEMENTS AMÉLIORÉE
    # ============================================================
    with st.expander("💵 Sensibilité aux versements mensuels"):
        
        st.markdown(
            """
            **💡 Commentaire :** Cette analyse démontre l'impact d'augmenter vos versements mensuels. 
            Doubler les versements peut plus que doubler le capital final grâce aux intérêts composés.
            """
        )
        
        # Options de versements intelligentes basées sur le versement actuel
        if pmt > 0:
            pmt_multipliers = [0.5, 0.75, 1, 1.25, 1.5, 2]
            pmt_values = [int(pmt * x) for x in pmt_multipliers]
        else:
            # Si pas de versement, proposer des valeurs standards
            pmt_values = [25_000, 50_000, 75_000, 100_000, 150_000, 200_000]
        
        df_p = simulate_pmt_sensitivity(pv, rate, n_years, pmt_values)
        
        # Calculer le ROI de chaque versement additionnel
        df_p["Investissement Total"] = pv + df_p["Versement Mensuel"] * n_years * 12
        df_p["Intérêts Générés"] = df_p["FV"] - df_p["Investissement Total"]
        df_p["ROI %"] = (df_p["Intérêts Générés"] / df_p["Investissement Total"] * 100)

        chart_p = (
            alt.Chart(df_p)
            .mark_bar()
            .encode(
                x=alt.X("Versement Mensuel:O", title="Versement Mensuel (FCFA)", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("FV:Q", title="Valeur Future (FCFA)"),
                color=alt.condition(
                    alt.datum["Versement Mensuel"] == pmt,
                    alt.value(ACCENT_COLOR),
                    alt.value(PRIMARY_COLOR)
                ),
                tooltip=[
                    alt.Tooltip("Versement Mensuel:O", format=",.0f", title="Versement"),
                    alt.Tooltip("FV:Q", format=",.0f", title="Valeur Future")
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart_p, use_container_width=True)
        
        # Tableau détaillé avec ROI
        st.markdown("**📋 Analyse comparative des versements :**")
        df_display = df_p.copy()
        df_display["Versement"] = df_display["Versement Mensuel"].apply(lambda x: f"{x:,.0f} FCFA")
        df_display["Valeur Finale"] = df_display["FV"].apply(lambda x: f"{x:,.0f} FCFA")
        df_display["Total Investi"] = df_display["Investissement Total"].apply(lambda x: f"{x:,.0f} FCFA")
        df_display["Intérêts"] = df_display["Intérêts Générés"].apply(lambda x: f"{x:,.0f} FCFA")
        df_display["ROI"] = df_display["ROI %"].apply(lambda x: f"{x:.1f}%")
        df_display = df_display[["Versement", "Valeur Finale", "Total Investi", "Intérêts", "ROI"]]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Recommandation intelligente
        if len(df_p) >= 2:
            best_roi_idx = df_p["ROI %"].idxmax()
            best_pmt = df_p.loc[best_roi_idx, "Versement Mensuel"]
            best_roi = df_p.loc[best_roi_idx, "ROI %"]
            
            if pmt > 0 and best_pmt != pmt:
                diff_pmt = best_pmt - pmt
                diff_fv = df_p.loc[best_roi_idx, "FV"] - df_p[df_p["Versement Mensuel"] == pmt]["FV"].iloc[0]
                st.success(
                    f"💡 **Opportunité :** En augmentant votre versement mensuel de **{diff_pmt:,.0f} FCFA** "
                    f"(pour atteindre {best_pmt:,.0f} FCFA), vous pourriez gagner **{diff_fv:,.0f} FCFA** "
                    f"supplémentaires avec un ROI optimal de {best_roi:.1f}%."
                )

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
        total_withdrawals = withdrawal_monthly * withdrawal_years * 12
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Capital accumulé", fmt_money(accumulated))
        with col2:
            st.metric("Total des retraits", fmt_money(total_withdrawals))
        with col3:
            if final_capital > 0:
                st.metric("Capital restant", fmt_money(final_capital), delta="✅ Viable")
            else:
                st.metric("Capital restant", fmt_money(0), delta="⚠️ Épuisé")
        with col4:
            # Calculer le taux de retrait annuel
            withdrawal_rate = (withdrawal_monthly * 12 / accumulated * 100) if accumulated > 0 else 0
            st.metric("Taux de retrait", f"{withdrawal_rate:.2f}%", 
                     help="Pourcentage du capital retiré chaque année")
        
        # Analyse et recommandations intelligentes
        if final_capital <= 0:
            # Calculer combien de mois le capital peut tenir
            months_sustainable = 0
            capital_depleted = False
            for idx, row in df_withdrawal[df_withdrawal["Phase"] == "Retrait"].iterrows():
                if row["Capital"] <= 0:
                    months_sustainable = int(row["Mois"]) - int(accum_years * 12)
                    capital_depleted = True
                    break
            
            if capital_depleted and months_sustainable > 0:
                years_sustainable = months_sustainable / 12
                # Calcul de la différence de rendement nécessaire (toujours positif)
                rate_diff = abs(withdrawal_rate - 4) if withdrawal_rate > 4 else 4 - withdrawal_rate
                st.error(
                    f"⚠️ **Capital épuisé après {years_sustainable:.1f} ans de retraits** "
                    f"(sur {withdrawal_years} ans prévus).\n\n"
                    f"**Recommandations :**\n"
                    f"- Réduire les retraits mensuels à environ {withdrawal_monthly * 0.7:,.0f} FCFA (-30%)\n"
                    f"- Ou augmenter la période d'accumulation de {int((withdrawal_years - years_sustainable) * 1.5)} ans\n"
                    f"- Ou viser un rendement supérieur d'au moins {rate_diff:.1f} points de pourcentage"
                )
            else:
                # Capital épuisé immédiatement
                st.error(
                    f"⚠️ **Capital insuffisant pour ce scénario de retraits.**\n\n"
                    f"**Recommandations :**\n"
                    f"- Augmenter significativement la période d'accumulation\n"
                    f"- Ou réduire les retraits mensuels à {withdrawal_monthly * 0.5:,.0f} FCFA (-50%)\n"
                    f"- Ou augmenter les versements mensuels durant l'accumulation"
                )
        else:
            # Le scénario est viable
            sustainability_ratio = final_capital / accumulated
            if sustainability_ratio > 0.5:
                st.success(
                    f"✅ **Scénario très viable !** Après {withdrawal_years} ans de retraits, "
                    f"il vous reste encore {sustainability_ratio*100:.1f}% de votre capital initial. "
                    f"Vous pourriez augmenter vos retraits mensuels jusqu'à environ {withdrawal_monthly * 1.3:,.0f} FCFA."
                )
            elif sustainability_ratio > 0.2:
                st.info(
                    f"ℹ️ **Scénario viable.** Votre stratégie est équilibrée avec {sustainability_ratio*100:.1f}% "
                    f"du capital restant après {withdrawal_years} ans."
                )
            else:
                st.warning(
                    f"⚠️ **Scénario juste viable.** Seulement {sustainability_ratio*100:.1f}% du capital reste. "
                    f"Considérez de réduire légèrement les retraits pour plus de sécurité."
                )
        
        # Calcul de la "règle des 4%" pour comparaison
        safe_withdrawal = accumulated * 0.04 / 12
        st.markdown("---")
        if withdrawal_monthly > 0:
            safe_vs_actual = (safe_withdrawal / withdrawal_monthly * 100)
            st.markdown(
                f"**📊 Référence - Règle des 4% :** Selon cette règle classique de planification financière, "
                f"un retrait mensuel sûr serait d'environ **{safe_withdrawal:,.0f} FCFA** "
                f"({safe_vs_actual:.0f}% de votre retrait actuel)."
            )
        else:
            st.markdown(
                f"**📊 Référence - Règle des 4% :** Selon cette règle classique de planification financière, "
                f"un retrait mensuel sûr serait d'environ **{safe_withdrawal:,.0f} FCFA**."
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
