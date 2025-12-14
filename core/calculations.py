# core/calculations.py
# ---------------------------------------------------------
# Toutes les fonctions financières utilisées dans l'app :
# - Valeur future (FV)
# - Versement mensuel (PMT)
# - Valeur actuelle nécessaire (PV)
# - Horizon de placement (n_years)
#
# Chaque fonction est indépendante pour faciliter les tests unitaires
# et la maintenance de l'application.
# ---------------------------------------------------------

import numpy as np
import streamlit as st
from typing import Union


class CalculationError(Exception):
    """Exception personnalisée pour les erreurs de calcul."""
    pass


def validate_inputs(pv: float, pmt: float, rate: float, n_years: float) -> None:
    """
    Valide les paramètres d'entrée des calculs.
    
    Args:
        pv: Montant initial
        pmt: Versement mensuel
        rate: Taux de rendement annuel en %
        n_years: Durée en années
        
    Raises:
        CalculationError: Si les paramètres sont invalides
    """
    if pv < 0:
        raise CalculationError("Le montant initial ne peut pas être négatif")
    if pmt < 0:
        raise CalculationError("Le versement mensuel ne peut pas être négatif")
    if n_years < 0:
        raise CalculationError("L'horizon ne peut pas être négatif")
    if rate < -100:
        raise CalculationError("Le taux ne peut pas être inférieur à -100%")
    if n_years > 100:
        raise CalculationError("L'horizon ne peut pas dépasser 100 ans")


@st.cache_data
def calculate_fv(pv: float, pmt: float, rate: float, n_years: float) -> float:
    """
    Calcule la Valeur Future totale (FV) d'un investissement.
    
    Args:
        pv: Montant initial
        pmt: Versement mensuel
        rate: Rendement annuel en %
        n_years: Durée en années
        
    Returns:
        float: Valeur future calculée
        
    Raises:
        CalculationError: Si les paramètres sont invalides
        ValueError: Si une erreur de calcul survient
    """
    validate_inputs(pv, pmt, rate, n_years)
    
    if n_years == 0:
        return pv
    
    try:
        n_periods = int(n_years * 12)
        rate_monthly = rate / 100 / 12

        # FV du capital initial
        fv_pv = pv * (1 + rate_monthly) ** n_periods

        # FV des versements mensuels
        if rate_monthly == 0:
            fv_pmt = pmt * n_periods
        else:
            fv_pmt = pmt * (((1 + rate_monthly) ** n_periods - 1) / rate_monthly)

        return fv_pv + fv_pmt
    except (ZeroDivisionError, OverflowError) as e:
        raise ValueError(f"Erreur de calcul: {e}")


@st.cache_data
def calculate_pmt(fv: float, pv: float, rate: float, n_years: float) -> float:
    """
    Calcule le versement mensuel nécessaire pour atteindre un montant final FV.
    
    Args:
        fv: Montant cible à atteindre
        pv: Montant initial
        rate: Rendement annuel en %
        n_years: Durée en années
        
    Returns:
        float: Versement mensuel nécessaire
        
    Raises:
        CalculationError: Si les paramètres sont invalides
        ValueError: Si une erreur de calcul survient
    """
    validate_inputs(pv, 0, rate, n_years)
    
    if n_years == 0:
        return 0
    
    try:
        n_periods = int(n_years * 12)
        rate_monthly = rate / 100 / 12

        if rate_monthly == 0:
            # Cas simple sans rendement
            return max((fv - pv) / n_periods, 0)

        # FV provenant uniquement du capital initial
        fv_pv = pv * (1 + rate_monthly) ** n_periods

        fv_required_from_pmt = fv - fv_pv

        if fv_required_from_pmt <= 0:
            return 0  # Le capital initial suffit déjà

        return fv_required_from_pmt / (((1 + rate_monthly) ** n_periods - 1) / rate_monthly)
    except (ZeroDivisionError, OverflowError) as e:
        raise ValueError(f"Erreur de calcul: {e}")


@st.cache_data
def calculate_pv(fv: float, pmt: float, rate: float, n_years: float) -> float:
    """
    Calcule le montant initial (PV) nécessaire pour atteindre FV.
    
    Args:
        fv: Montant cible à atteindre
        pmt: Versement mensuel
        rate: Rendement annuel en %
        n_years: Durée en années
        
    Returns:
        float: Montant initial nécessaire
        
    Raises:
        CalculationError: Si les paramètres sont invalides
        ValueError: Si une erreur de calcul survient
    """
    validate_inputs(0, pmt, rate, n_years)
    
    if n_years == 0:
        return max(fv, 0)
    
    try:
        n_periods = int(n_years * 12)
        rate_monthly = rate / 100 / 12

        # FV des versements
        if rate_monthly == 0:
            fv_pmt = pmt * n_periods
        else:
            fv_pmt = pmt * (((1 + rate_monthly) ** n_periods - 1) / rate_monthly)

        if fv <= fv_pmt:
            return 0  # Les versements seuls permettent d'atteindre l'objectif

        if rate_monthly == 0:
            return fv - fv_pmt

        return (fv - fv_pmt) / ((1 + rate_monthly) ** n_periods)
    except (ZeroDivisionError, OverflowError) as e:
        raise ValueError(f"Erreur de calcul: {e}")


@st.cache_data
def calculate_n_years(fv: float, pv: float, pmt: float, rate: float) -> Union[float, type(np.inf)]:
    """
    Calcule le nombre d'années nécessaires pour atteindre FV.
    Utilise une simulation mois par mois (robuste et stable).
    
    Args:
        fv: Montant cible à atteindre
        pv: Montant initial
        pmt: Versement mensuel
        rate: Rendement annuel en %
        
    Returns:
        Union[float, np.inf]: Nombre d'années nécessaires, ou np.inf si impossible
        
    Raises:
        CalculationError: Si les paramètres sont invalides
    """
    validate_inputs(pv, pmt, rate, 10)  # Valide avec n_years=10 par défaut
    
    if rate == 0:
        if pmt == 0:
            return np.inf if fv > pv else 0
        return max((fv - pv) / pmt / 12, 0)

    rate_monthly = rate / 100 / 12

    if fv <= pv:
        return 0.0

    current_fv = pv

    # On limite à 100 ans (1200 mois)
    for month in range(1, 1201):
        current_fv = current_fv * (1 + rate_monthly) + pmt

        if current_fv >= fv:
            return month / 12

    return np.inf
