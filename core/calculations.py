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


def calculate_fv(pv: float, pmt: float, rate: float, n_years: float) -> float:
    """
    Calcule la Valeur Future totale (FV) d’un investissement.
    - pv  : montant initial
    - pmt : versement mensuel
    - rate : rendement annuel en %
    - n_years : durée en années
    """
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


def calculate_pmt(fv: float, pv: float, rate: float, n_years: float) -> float:
    """
    Calcule le versement mensuel nécessaire pour atteindre un montant final FV.
    """
    n_periods = int(n_years * 12)
    rate_monthly = rate / 100 / 12

    if rate_monthly == 0:
        # Cas simple sans rendement
        return (fv - pv) / n_periods

    # FV provenant uniquement du capital initial
    fv_pv = pv * (1 + rate_monthly) ** n_periods

    fv_required_from_pmt = fv - fv_pv

    if fv_required_from_pmt <= 0:
        return 0  # Le capital initial suffit déjà

    return fv_required_from_pmt / (((1 + rate_monthly) ** n_periods - 1) / rate_monthly)


def calculate_pv(fv: float, pmt: float, rate: float, n_years: float) -> float:
    """
    Calcule le montant initial (PV) nécessaire pour atteindre FV.
    """
    n_periods = int(n_years * 12)
    rate_monthly = rate / 100 / 12

    # FV des versements
    if rate_monthly == 0:
        fv_pmt = pmt * n_periods
    else:
        fv_pmt = pmt * (((1 + rate_monthly) ** n_periods - 1) / rate_monthly)

    if fv <= fv_pmt:
        return 0  # Les versements seuls permettent d’atteindre l’objectif

    if rate_monthly == 0:
        return fv - fv_pmt

    return (fv - fv_pmt) / ((1 + rate_monthly) ** n_periods)


def calculate_n_years(fv: float, pv: float, pmt: float, rate: float) -> float:
    """
    Calcule le nombre d'années nécessaires pour atteindre FV.
    Utilise une simulation mois par mois (robuste et stable).
    """
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
