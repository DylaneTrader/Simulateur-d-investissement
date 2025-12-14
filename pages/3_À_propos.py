# pages/3_À_propos.py
# ------------------------------------------------------------
# Page "À propos" : Documentation des formules mathématiques
# 
# Cette page explique toutes les formules financières utilisées
# dans l'application avec des illustrations et des exemples pratiques.
# ------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from ui.sidebar import display_sidebar
from core.config import (
    get_theme_css, 
    APP_NAME,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR
)
from core.calculations import calculate_fv, calculate_pmt, calculate_pv, calculate_n_years
from core.utils import fmt_money


def main():
    # Configuration
    st.set_page_config(page_title="À propos | " + APP_NAME, layout="wide")
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    
    # Sidebar
    display_sidebar()
    
    # Titre principal
    st.markdown(
        f"""
        <h1 style='color: {PRIMARY_COLOR}; text-align: center;'>
            📚 À propos - Formules Mathématiques
        </h1>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Introduction
    st.markdown(
        """
        ## 🎯 Introduction
        
        Le **Simulateur d'Investissement CGF GESTION** utilise des formules financières classiques 
        basées sur la **valeur temporelle de l'argent** (Time Value of Money). Cette page détaille 
        toutes les formules mathématiques utilisées dans l'application.
        
        ### Concept fondamental : La Valeur Future d'une Annuité
        
        L'application modélise la croissance d'un capital composé de :
        - 📊 **Un capital initial** (PV - Present Value) 
        - 💰 **Des versements périodiques réguliers** (PMT - Payment)
        - 📈 **Un taux de rendement annualisé** (r - Rate)
        - ⏱️ **Une durée d'investissement** (n - Number of years)
        """
    )
    
    st.markdown("---")
    
    # Section 1: Calcul de la Valeur Future (FV)
    st.markdown(
        f"""
        <h2 style='color: {PRIMARY_COLOR};'>
            1️⃣ Calcul de la Valeur Future (FV)
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        ### 📐 Formule mathématique
        
        La valeur future totale est la somme de deux composantes :
        """
    )
    
    # Formule LaTeX pour FV
    st.latex(r"""
    FV_{total} = FV_{capital} + FV_{versements}
    """)
    
    st.markdown("**Composante 1 : Valeur future du capital initial**")
    st.latex(r"""
    FV_{capital} = PV \times (1 + r_m)^n
    """)
    
    st.markdown("**Composante 2 : Valeur future des versements mensuels**")
    st.latex(r"""
    FV_{versements} = PMT \times \frac{(1 + r_m)^n - 1}{r_m}
    """)
    
    st.markdown("**Formule complète :**")
    st.latex(r"""
    FV = PV \times (1 + r_m)^n + PMT \times \frac{(1 + r_m)^n - 1}{r_m}
    """)
    
    st.markdown(
        """
        Où :
        - **FV** = Valeur Future (montant final)
        - **PV** = Present Value (capital initial)
        - **PMT** = Payment (versement mensuel)
        - **r_m** = Taux mensuel = (Taux annuel) / 12
        - **n** = Nombre de périodes mensuelles = Années × 12
        """
    )
    
    # Exemple interactif FV
    with st.expander("💡 Exemple interactif - Calcul de la Valeur Future", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            pv_example = st.number_input("Capital initial (FCFA)", value=1_000_000, step=100_000, key="fv_pv")
            pmt_example = st.number_input("Versement mensuel (FCFA)", value=50_000, step=10_000, key="fv_pmt")
            rate_example = st.number_input("Taux annuel (%)", value=5.0, step=0.5, key="fv_rate")
            years_example = st.number_input("Durée (années)", value=10, step=1, key="fv_years")
        
        with col2:
            fv_result = calculate_fv(pv_example, pmt_example, rate_example, years_example)
            
            st.markdown("### Résultat")
            st.metric("Valeur Future", fmt_money(fv_result))
            
            # Détails du calcul
            rate_monthly = rate_example / 100 / 12
            n_periods = int(years_example * 12)
            fv_pv_component = pv_example * (1 + rate_monthly) ** n_periods
            fv_pmt_component = pmt_example * (((1 + rate_monthly) ** n_periods - 1) / rate_monthly) if rate_monthly != 0 else pmt_example * n_periods
            
            st.markdown(f"""
            **Détails :**
            - FV du capital : {fmt_money(fv_pv_component)}
            - FV des versements : {fmt_money(fv_pmt_component)}
            - **Total : {fmt_money(fv_result)}**
            """)
        
        # Graphique d'évolution
        create_evolution_chart(pv_example, pmt_example, rate_example, years_example)
    
    st.markdown("---")
    
    # Section 2: Calcul du Versement Mensuel (PMT)
    st.markdown(
        f"""
        <h2 style='color: {PRIMARY_COLOR};'>
            2️⃣ Calcul du Versement Mensuel (PMT)
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        ### 📐 Formule mathématique
        
        Pour calculer le versement mensuel nécessaire pour atteindre un objectif :
        """
    )
    
    st.latex(r"""
    PMT = \frac{FV - PV \times (1 + r_m)^n}{\frac{(1 + r_m)^n - 1}{r_m}}
    """)
    
    st.markdown(
        """
        **Dérivation :**
        1. On calcule d'abord la valeur future générée par le capital initial seul
        2. On soustrait cette valeur de l'objectif FV pour obtenir la contribution nécessaire des versements
        3. On résout pour PMT en inversant la formule de FV des versements
        
        **Cas particuliers :**
        - Si **r = 0** : PMT = (FV - PV) / n
        - Si **FV ≤ FV du capital initial** : PMT = 0 (le capital initial suffit)
        """
    )
    
    # Exemple interactif PMT
    with st.expander("💡 Exemple interactif - Calcul du Versement Mensuel", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fv_target = st.number_input("Objectif (FCFA)", value=10_000_000, step=500_000, key="pmt_fv")
            pv_pmt = st.number_input("Capital initial (FCFA)", value=1_000_000, step=100_000, key="pmt_pv")
            rate_pmt = st.number_input("Taux annuel (%)", value=5.0, step=0.5, key="pmt_rate")
            years_pmt = st.number_input("Durée (années)", value=10, step=1, key="pmt_years")
        
        with col2:
            pmt_result = calculate_pmt(fv_target, pv_pmt, rate_pmt, years_pmt)
            
            st.markdown("### Résultat")
            st.metric("Versement Mensuel Nécessaire", fmt_money(pmt_result))
            
            st.markdown(f"""
            **Équivalences périodiques :**
            - Par trimestre : {fmt_money(pmt_result * 3)}
            - Par semestre : {fmt_money(pmt_result * 6)}
            - Par an : {fmt_money(pmt_result * 12)}
            """)
            
            total_versements = pmt_result * years_pmt * 12
            st.markdown(f"""
            **Total des versements sur {years_pmt} ans :**
            {fmt_money(total_versements)}
            """)
    
    st.markdown("---")
    
    # Section 3: Calcul du Capital Initial (PV)
    st.markdown(
        f"""
        <h2 style='color: {PRIMARY_COLOR};'>
            3️⃣ Calcul du Capital Initial (PV)
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        ### 📐 Formule mathématique
        
        Pour calculer le capital initial nécessaire pour atteindre un objectif avec des versements donnés :
        """
    )
    
    st.latex(r"""
    PV = \frac{FV - PMT \times \frac{(1 + r_m)^n - 1}{r_m}}{(1 + r_m)^n}
    """)
    
    st.markdown(
        """
        **Dérivation :**
        1. On calcule la valeur future générée par les versements mensuels seuls
        2. On soustrait cette valeur de l'objectif FV
        3. On actualise (discount) ce montant restant à la valeur présente
        
        **Cas particuliers :**
        - Si **r = 0** : PV = FV - (PMT × n)
        - Si **FV ≤ FV des versements** : PV = 0 (les versements suffisent)
        """
    )
    
    # Exemple interactif PV
    with st.expander("💡 Exemple interactif - Calcul du Capital Initial", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fv_pv = st.number_input("Objectif (FCFA)", value=10_000_000, step=500_000, key="pv_fv")
            pmt_pv = st.number_input("Versement mensuel (FCFA)", value=50_000, step=10_000, key="pv_pmt")
            rate_pv = st.number_input("Taux annuel (%)", value=5.0, step=0.5, key="pv_rate")
            years_pv = st.number_input("Durée (années)", value=10, step=1, key="pv_years")
        
        with col2:
            pv_result = calculate_pv(fv_pv, pmt_pv, rate_pv, years_pv)
            
            st.markdown("### Résultat")
            st.metric("Capital Initial Nécessaire", fmt_money(pv_result))
            
            # Calcul des contributions
            total_versements = pmt_pv * years_pv * 12
            total_investi = pv_result + total_versements
            gains = fv_pv - total_investi
            
            st.markdown(f"""
            **Analyse des contributions :**
            - Capital initial : {fmt_money(pv_result)}
            - Total des versements : {fmt_money(total_versements)}
            - **Total investi : {fmt_money(total_investi)}**
            - **Gains générés : {fmt_money(gains)}**
            - **ROI : {(gains / total_investi * 100):.2f}%**
            """)
    
    st.markdown("---")
    
    # Section 4: Calcul de la Durée (n_years)
    st.markdown(
        f"""
        <h2 style='color: {PRIMARY_COLOR};'>
            4️⃣ Calcul de la Durée (n)
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        ### 📐 Méthode de calcul
        
        Le calcul de la durée nécessaire pour atteindre un objectif est **itératif** car il n'existe pas 
        de formule analytique simple lorsqu'on combine un capital initial ET des versements réguliers.
        
        **Algorithme de simulation :**
        """
    )
    
    st.code("""
# Pseudo-code
capital_actuel = PV
mois = 0
taux_mensuel = taux_annuel / 12 / 100

tant que capital_actuel < FV et mois < 1200:
    capital_actuel = capital_actuel × (1 + taux_mensuel) + PMT
    mois = mois + 1

durée_années = mois / 12
    """, language="python")
    
    st.markdown(
        """
        **Cas particuliers :**
        - Si **r = 0 et PMT = 0** : Impossible d'atteindre FV si FV > PV → n = ∞
        - Si **r = 0 et PMT > 0** : n = (FV - PV) / (PMT × 12)
        - Si **FV ≤ PV** : Objectif déjà atteint → n = 0
        """
    )
    
    # Exemple interactif n_years
    with st.expander("💡 Exemple interactif - Calcul de la Durée", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fv_n = st.number_input("Objectif (FCFA)", value=10_000_000, step=500_000, key="n_fv")
            pv_n = st.number_input("Capital initial (FCFA)", value=1_000_000, step=100_000, key="n_pv")
            pmt_n = st.number_input("Versement mensuel (FCFA)", value=50_000, step=10_000, key="n_pmt")
            rate_n = st.number_input("Taux annuel (%)", value=5.0, step=0.5, key="n_rate")
        
        with col2:
            n_result = calculate_n_years(fv_n, pv_n, pmt_n, rate_n)
            
            st.markdown("### Résultat")
            if np.isinf(n_result):
                st.error("⚠️ Impossible d'atteindre cet objectif avec ces paramètres")
            else:
                st.metric("Durée Nécessaire", f"{n_result:.1f} ans")
                
                # Conversion en mois
                mois = int(n_result * 12)
                annees = mois // 12
                mois_restants = mois % 12
                
                st.markdown(f"""
                **Durée détaillée :**
                - {annees} ans et {mois_restants} mois
                - Soit {mois} mois au total
                """)
                
                # Total investi
                total_versements = pmt_n * mois
                total_investi = pv_n + total_versements
                gains = fv_n - total_investi
                
                st.markdown(f"""
                **Bilan financier :**
                - Total investi : {fmt_money(total_investi)}
                - Gains générés : {fmt_money(gains)}
                - ROI : {(gains / total_investi * 100):.2f}%
                """)
    
    st.markdown("---")
    
    # Section 5: Concepts clés
    st.markdown(
        f"""
        <h2 style='color: {PRIMARY_COLOR};'>
            5️⃣ Concepts Clés en Finance
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            ### 🔄 Capitalisation des Intérêts Composés
            
            Le principe des **intérêts composés** signifie que les intérêts générés sont réinvestis 
            et génèrent eux-mêmes des intérêts.
            """
        )
        
        st.latex(r"""
        A = P \times (1 + r)^n
        """)
        
        st.markdown(
            """
            où :
            - **A** = Montant final
            - **P** = Principal (capital initial)
            - **r** = Taux par période
            - **n** = Nombre de périodes
            
            **Exemple :** 1 000 000 FCFA à 5% par an pendant 10 ans
            """
        )
        
        st.latex(r"""
        A = 1\,000\,000 \times (1.05)^{10} = 1\,628\,895\text{ FCFA}
        """)
        
        st.markdown("### 📊 Taux Effectif vs Taux Nominal")
        
        st.markdown(
            """
            Quand le taux est **composé mensuellement** (comme dans notre application) :
            """
        )
        
        st.latex(r"""
        \text{Taux effectif annuel} = \left(1 + \frac{r_{nominal}}{12}\right)^{12} - 1
        """)
        
        st.markdown(
            """
            **Exemple :** Un taux nominal de 5% par an capitalisé mensuellement donne un taux effectif de 5.12%.
            """
        )
    
    with col2:
        st.markdown(
            """
            ### 💰 Valeur Temporelle de l'Argent
            
            Le principe fondamental : **Un FCFA aujourd'hui vaut plus qu'un FCFA demain** 
            car il peut être investi et générer des rendements.
            
            **Actualisation (Discounting) :**
            """
        )
        
        st.latex(r"""
        PV = \frac{FV}{(1 + r)^n}
        """)
        
        st.markdown(
            """
            **Capitalisation (Compounding) :**
            """
        )
        
        st.latex(r"""
        FV = PV \times (1 + r)^n
        """)
        
        st.markdown("### 📈 Rendement sur Investissement (ROI)")
        
        st.markdown(
            """
            Le ROI mesure le gain par rapport à l'investissement initial :
            """
        )
        
        st.latex(r"""
        ROI = \frac{\text{Gains}}{\text{Total Investi}} \times 100\%
        """)
        
        st.markdown(
            """
            où :
            - **Gains** = FV - (PV + Total des versements)
            - **Total Investi** = PV + Total des versements
            """
        )
    
    st.markdown("---")
    
    # Section 6: Tableau récapitulatif
    st.markdown(
        f"""
        <h2 style='color: {PRIMARY_COLOR};'>
            6️⃣ Tableau Récapitulatif des Formules
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    # Créer un DataFrame avec les formules
    formulas_data = {
        "Paramètre": ["Valeur Future (FV)", "Versement (PMT)", "Capital Initial (PV)", "Durée (n)"],
        "Ce qu'on calcule": [
            "Montant final à atteindre",
            "Versement mensuel nécessaire",
            "Capital initial nécessaire",
            "Temps nécessaire"
        ],
        "Ce qu'on connaît": [
            "PV, PMT, r, n",
            "FV, PV, r, n",
            "FV, PMT, r, n",
            "FV, PV, PMT, r"
        ],
        "Méthode": [
            "Formule analytique",
            "Formule analytique",
            "Formule analytique",
            "Simulation itérative"
        ]
    }
    
    df_formulas = pd.DataFrame(formulas_data)
    st.dataframe(df_formulas, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Section 7: Limites et Hypothèses
    st.markdown(
        f"""
        <h2 style='color: {PRIMARY_COLOR};'>
            7️⃣ Limites et Hypothèses du Modèle
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            ### ✅ Hypothèses du modèle
            
            - **Versements constants** : Les versements mensuels restent identiques
            - **Taux constant** : Le taux de rendement ne varie pas dans le temps
            - **Pas de frais** : Aucun frais de gestion ou de transaction n'est pris en compte
            - **Réinvestissement total** : Tous les gains sont automatiquement réinvestis
            - **Versements en fin de période** : Les versements interviennent à la fin de chaque mois
            """
        )
    
    with col2:
        st.markdown(
            """
            ### ⚠️ Limites du modèle
            
            - **Volatilité ignorée** : Les marchés réels sont volatils, le taux peut varier
            - **Inflation non considérée** : Les calculs sont en valeur nominale
            - **Fiscalité non incluse** : Les impôts sur les gains ne sont pas pris en compte
            - **Liquidité supposée** : On suppose qu'on peut toujours investir et retirer
            - **Risques non modélisés** : Pas de prise en compte du risque de perte
            """
        )
    
    st.info(
        """
        💡 **Conseil professionnel** : Ces formules donnent des **estimations** basées sur des hypothèses 
        simplificatrices. Dans la réalité, les performances passées ne garantissent pas les résultats futurs. 
        Il est recommandé de consulter un conseiller financier pour des décisions d'investissement importantes.
        """
    )
    
    st.markdown("---")
    
    # Footer
    st.markdown(
        f"""
        <div style='text-align: center; color: {SECONDARY_COLOR}; padding: 20px;'>
            <p><strong>Simulateur d'Investissement - CGF GESTION</strong></p>
            <p>Développé par Dylane Emmanuel Reyane NDOUDY-BAMOUENIZO</p>
            <p><em>Toutes les formules mathématiques sont conformes aux standards de la finance moderne</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )


def create_evolution_chart(pv, pmt, rate, n_years):
    """Crée un graphique d'évolution du capital sur la durée."""
    
    months = []
    capital_values = []
    versements_cumules = []
    
    rate_monthly = rate / 100 / 12
    current_capital = pv
    total_versements = 0
    
    # Calcul mois par mois
    for month in range(int(n_years * 12) + 1):
        months.append(month / 12)
        capital_values.append(current_capital)
        versements_cumules.append(pv + total_versements)
        
        # Appliquer le rendement et ajouter le versement
        if month < int(n_years * 12):
            current_capital = current_capital * (1 + rate_monthly) + pmt
            total_versements += pmt
    
    # Créer le graphique avec Plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=capital_values,
        mode='lines',
        name='Valeur du portefeuille',
        line=dict(color=PRIMARY_COLOR, width=3),
        fill='tozeroy',
        fillcolor=f'rgba(17, 75, 128, 0.1)'
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=versements_cumules,
        mode='lines',
        name='Total investi (sans intérêts)',
        line=dict(color=SECONDARY_COLOR, width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Évolution du capital dans le temps",
        xaxis_title="Années",
        yaxis_title="Montant (FCFA)",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
