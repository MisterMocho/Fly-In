import sys
from parser import MapParser
from simulation import Simulation


def main() -> None:
    # Verifica se o utilizador passou o argumento do mapa
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <map_path>")
        sys.exit(1)

    map_path: str = sys.argv[1]
    visual_mode: bool = "--visual" in sys.argv
    try:
        # 1. Carregar e Validar o Mapa
        parser = MapParser(map_path)
        parser.parse()
        # 2. Iniciar a Simulação
        sim = Simulation(parser)
        # 3. Correr até ao fim
        sim.run(visual_mode=visual_mode)

    except FileNotFoundError:
        print(f"Error: Map file not found at '{map_path}'")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid map format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
