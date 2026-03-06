"""
Entry point for the Fly-in Drone Simulation.

This script orchestrates the entire simulation pipeline:
1. Validates command-line arguments.
2. Invokes the MapParser to load and validate the map file.
3. Initializes the Simulation engine with the parsed data.
4. Executes the simulation loop, optionally with visual output.

Usage:
    python src/main.py <map_path> [--visual]
"""
import sys
from parser import MapParser
from simulation import Simulation


def main() -> None:
    """
    Executes the main program flow.

    Retrieves the map file path from command-line arguments, initializes
    the parsing and simulation components, and handles top-level exceptions
    to ensure graceful error reporting.

    Command Line Arguments:
        map_path (str): Path to the map configuration file (mandatory).
        --visual (flag): Enables visual representation of the simulation
        (optional).

    Raises:
        SystemExit: Exits with code 1 if arguments are missing, the file
                    is not found, the map format is invalid, or an unexpected
                    error occurs.
    """
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
