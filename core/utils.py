# core/utils.py
# ---------------------------------------------------------
# Fonctions auxiliaires réutilisables dans toute l'app :
# - formatage des montants
# - validation
# - arrondis
# - helpers généraux
# ---------------------------------------------------------

import math
from typing import Union


def fmt_money(value: float) -> str:
    """
    Formatte proprement un montant en FCFA avec séparateurs.
    
    Args:
        value: Montant à formater
        
    Returns:
        str: Montant formaté avec séparateurs (ex: "1 500 000 FCFA")
        
    Example:
        >>> fmt_money(1500000)
        '1 500 000 FCFA'
    """
    try:
        return f"{value:,.0f} FCFA".replace(",", " ")
    except Exception:
        return str(value)


def is_positive_number(x: Union[int, float, str]) -> bool:
    """
    Vérifie si x est un nombre positif ou zéro.
    
    Args:
        x: Valeur à vérifier (peut être int, float ou str)
        
    Returns:
        bool: True si x est un nombre positif ou zéro, False sinon
        
    Example:
        >>> is_positive_number(100)
        True
        >>> is_positive_number(-50)
        False
        >>> is_positive_number("abc")
        False
    """
    try:
        return float(x) >= 0
    except:
        return False


def round_up(value: float, decimals: int = 0) -> float:
    """
    Arrondit un nombre vers le haut.
    
    Args:
        value: Valeur à arrondir
        decimals: Nombre de décimales (défaut: 0)
        
    Returns:
        float: Valeur arrondie vers le haut
        
    Example:
        >>> round_up(123.456, 2)
        123.46
    """
    factor = 10 ** decimals
    return math.ceil(value * factor) / factor


def round_down(value: float, decimals: int = 0) -> float:
    """
    Arrondit un nombre vers le bas.
    
    Args:
        value: Valeur à arrondir
        decimals: Nombre de décimales (défaut: 0)
        
    Returns:
        float: Valeur arrondie vers le bas
        
    Example:
        >>> round_down(123.456, 2)
        123.45
    """
    factor = 10 ** decimals
    return math.floor(value * factor) / factor
