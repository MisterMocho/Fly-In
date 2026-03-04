from models import Zone, Drone
import colors


class Visualizer:
    """
    Responsável por toda a saída gráfica no terminal.
    """

    @staticmethod
    def print_map(zones: dict[str, Zone], drones: list[Drone],
                  turn: int, start_hub: str, end_hub: str) -> None:
        """Desenha a matriz do mapa no terminal."""
        if not zones:
            print("Map is empty.")
            return
        # 1. Calcular limites
        xs = [z.x for z in zones.values()]
        ys = [z.y for z in zones.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        print(f"\n--- Visual Map (Turn {turn}) ---")

        # 2. Desenhar linha a linha
        for y in range(min_y, max_y + 1):
            line = ""
            for x in range(min_x, max_x + 1):
                # Encontrar zona nesta coordenada
                zone = next((z for z in zones.values()
                             if z.x == x and z.y == y), None)

                # Símbolo base (assumindo vazio)
                symbol = "."
                color = colors.COLORS["white"]  # Cor padrão para o ponto

                if zone:
                    # Encontrar drones nesta zona
                    drones_here = [d for d in drones
                                   if d.current_zone == zone.name]
                    # Obter cor da zona
                    color = colors.get_color_code(zone.color)
                    # LÓGICA NOVA: Símbolo
                    if drones_here:
                        if len(drones_here) > 1:
                            # Se houver vários, mostra a contagem (ex: "3")
                            symbol = str(len(drones_here))
                        else:
                            # Se for só um, mostra D + ID (ex: "D1", "D5")
                            symbol = f"D{drones_here[0].drone_id}"
                    elif zone.name == start_hub:
                        symbol = "S"
                    elif zone.name == end_hub:
                        symbol = "E"
                    elif zone.zone_type == "blocked":
                        symbol = "X"
                    elif zone.zone_type == "restricted":
                        symbol = "R"
                    elif zone.zone_type == "priority":
                        symbol = "P"
                    else:
                        symbol = "N"  # Normal
                # Formatação com largura fixa (3 espaços, centrado)
                # Isto garante que "D10" ocupa o mesmo espaço que " . "
                line += f"{color}{symbol:^3}{colors.RESET} "

            print(line)
        print("-" * ((max_x - min_x + 1) * 4))
