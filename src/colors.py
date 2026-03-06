# Códigos ANSI básicos
RESET = "\033[0m"

# Dicionário com mapeamento de nomes comuns para códigos ANSI
COLORS = {
    # --- Cores Base ---
    "red": "\033[91m",
    "green": "\033[92m",
    "blue": "\033[94m",
    "yellow": "\033[93m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "black": "\033[30m",
    "gray": "\033[90m",

    # Vermelhos / Laranjas
    "crimson": "\033[31m",
    "darkred": "\033[31m",
    "orange": "\033[33m",   # Usa Amarelo/Castanho (ANSI não tem laranja)
    "brown": "\033[33m",
    "coral": "\033[91m",

    # Verdes
    "lime": "\033[92m",
    "dark_green": "\033[32m",
    "olive": "\033[33m",
    "forest": "\033[32m",

    # Azuis
    "navy": "\033[34m",
    "dark_blue": "\033[34m",
    "sky": "\033[96m",
    "teal": "\033[96m",
    "indigo": "\033[34m",

    # Rosas / Roxos
    "pink": "\033[95m",
    "purple": "\033[35m",
    "violet": "\033[35m",
    "fuchsia": "\033[95m",

    # Outros
    "silver": "\033[37m",
    "gold": "\033[33m",
    "maroon": "\033[31m",
    "rainbow": "\033[96m",
}


def get_color_code(name: str | None) -> str:
    """
    Retrieves the ANSI escape sequence for a given color name.

    This function normalizes the input color name (case-insensitive) and looks
    it up in the predefined `COLORS` dictionary. It includes a fallback
    mechanism to match partial names (e.g., 'light_blue' matching 'blue')
    if an exact match is not found.

    Args:
        name (str | None): The name of the color to retrieve (e.g., 'red',
            'Navy'). If None, returns the code for white.

    Returns:
        str: The ANSI escape code string corresponding to the color. Returns
        the code for white if the color name is unrecognized.
    """
    if not name:
        return COLORS["white"]
    # Normalização da chave
    clean_name = name.lower().strip()
    # 1. Tenta encontrar a cor exata ou alias
    if clean_name in COLORS:
        return COLORS[clean_name]
    # 2. Fallback inteligente (ex: "light_blue" tenta encontrar "blue")
    if "green" in clean_name:
        return COLORS["green"]
    if "red" in clean_name:
        return COLORS["red"]
    if "blue" in clean_name:
        return COLORS["blue"]
    if "yellow" in clean_name:
        return COLORS["yellow"]
    if "gray" in clean_name or "grey" in clean_name:
        return COLORS["gray"]
    if "purple" in clean_name:
        return COLORS["purple"]
    if "pink" in clean_name:
        return COLORS["magenta"]

    return COLORS["white"]
