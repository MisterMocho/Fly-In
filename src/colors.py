# Códigos ANSI básicos
RESET = "\033[0m"

# Dicionário com mapeamento de nomes comuns para códigos ANSI
# Inclui variações (light, dark, bright) mapeadas para a cor base mais próxima
COLORS = {
    # --- Cores Base ---
    "red": "\033[91m",      # Vermelho Brilhante
    "green": "\033[92m",    # Verde Brilhante
    "blue": "\033[94m",     # Azul Brilhante
    "yellow": "\033[93m",   # Amarelo
    "magenta": "\033[95m",  # Magenta/Rosa
    "cyan": "\033[96m",     # Ciano/Azul Claro
    "white": "\033[97m",    # Branco
    "black": "\033[30m",    # Preto
    "gray": "\033[90m",     # Cinzento

    # --- Aliases / Variações Comuns em Mapas ---

    # Vermelhos / Laranjas
    "crimson": "\033[31m",  # Vermelho Escuro
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
    "navy": "\033[34m",     # Azul Escuro
    "dark_blue": "\033[34m",
    "sky": "\033[96m",
    "teal": "\033[96m",
    "indigo": "\033[34m",

    # Rosas / Roxos
    "pink": "\033[95m",
    "purple": "\033[35m",   # Roxo Escuro
    "violet": "\033[35m",
    "fuchsia": "\033[95m",

    # Outros
    "silver": "\033[37m",   # Cinza Claro
    "gold": "\033[33m",
    "maroon": "\033[31m",   # Castanho avermelhado (Restricted)
    "rainbow": "\033[96m",  # Ciano Brilhante (Para o Goal!)
}


def get_color_code(name: str | None) -> str:
    """
    Retorna o código ANSI.
    Tenta ser inteligente: ignora maiúsculas/minúsculas e substitui '_'
    por espaço se necessário.
    """
    if not name:
        return COLORS["white"]

    # Normalização da chave
    clean_name = name.lower().strip()

    # 1. Tenta encontrar a cor exata ou alias
    if clean_name in COLORS:
        return COLORS[clean_name]

    # 2. DEBUG:
    # (Podes comentar este print depois de corrigir)
    # print(f"[DEBUG] Cor desconhecida: {clean_name}")

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
