from datetime import datetime

def calculate_dob(age: int) -> str:
    """Calcul approximatif de la date de naissance."""
    if not age: return None
    year = datetime.now().year - age
    return f"{year}-01-01"
