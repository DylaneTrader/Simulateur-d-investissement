# core/utils.py
# ---------------------------------------------------------
# Fonctions auxiliaires réutilisables dans toute l'app :
# - formatage des montants
# - validation
# - arrondis
# - helpers généraux
# ---------------------------------------------------------

import math


def fmt_money(value: float) -> str:
    """
    Formatte proprement un montant en FCFA avec séparateurs.
    Exemple : 1500000 → "1 500 000 FCFA"
    """
    try:
        return f"{value:,.0f} FCFA".replace(",", " ")
    except Exception:
        return str(value)


def is_positive_number(x) -> bool:
    """Vérifie si x est un nombre positif."""
    try:
        return float(x) >= 0
    except:
        return False


def round_up(value: float, decimals: int = 0) -> float:
    """Arrondi supérieur."""
    factor = 10 ** decimals
    return math.ceil(value * factor) / factor


def round_down(value: float, decimals: int = 0) -> float:
    """Arrondi inférieur."""
    factor = 10 ** decimals
    return math.floor(value * factor) / factor
