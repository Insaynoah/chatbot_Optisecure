import pandas as pd

def create_star_rating(note: float) -> str:
    """
    Crée une représentation étoilée d'une note.

    Args:
        note (float): Note sur 5.

    Returns:
        str: Chaîne contenant les étoiles (ex. "⭐⭐⭐⭐🌑").
    """
    if pd.isnull(note):
        return "Aucune donnée"
    
    note = round(note * 2) / 2  # Arrondir à la demi-étoile
    full_stars = '🌕' * int(note)  # Étoiles pleines
    half_star = '🌗' if note % 1 != 0 else ''  # Étoile à moitié remplie
    empty_stars = '🌑' * (5 - len(full_stars) - (1 if half_star else 0))  # Étoiles vides

    return full_stars + half_star + empty_stars
