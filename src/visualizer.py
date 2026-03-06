from models import Zone, Drone
import colors


class Visualizer:
    """
    Handles the rendering of the simulation state to the terminal.

    This class provides static methods to draw the map grid, optimizing the
    lookup of zones and drones using coordinate-based hashing (dictionaries)
    instead of linear searches.
    """

    @staticmethod
    def print_map(zones: dict[str, Zone], drones: list[Drone],
                  turn: int, start_hub: str, end_hub: str) -> None:
        """
        Renders the current state of the map grid to standard output.

        This method pre-calculates the positions of all zones and drones
        to allow O(1) lookup time during the rendering loop, significantly
        improving performance on large maps.

        Args:
            zones (Dict[str, Zone]): Dictionary of all zones in the map.
            drones (List[Drone]): List of all drones in the simulation.
            turn (int): The current simulation turn number.
            start_hub (str): Name of the start zone (marked as 'S').
            end_hub (str): Name of the end zone (marked as 'E').
        """
        if not zones:
            print("Map is empty.")
            return

        # 1. Pre-calculation: Create coordinate maps for O(1) access
        # Mapping: (x, y) -> Zone Object
        zone_grid: dict[tuple[int, int], Zone] = {
            (z.x, z.y): z for z in zones.values()
        }

        # Mapping: (x, y) -> List of Drones present at that location
        drone_grid: dict[tuple[int, int], list[Drone]] = {}
        for drone in drones:
            # We must find the coordinates of the drone's current zone
            # drone.current_zone is a string name
            current_z_obj = zones.get(drone.current_zone)
            if current_z_obj:
                coord = (current_z_obj.x, current_z_obj.y)
                if coord not in drone_grid:
                    drone_grid[coord] = []
                drone_grid[coord].append(drone)

        # 2. Determine Map Boundaries
        # We can just extract keys from zone_grid which are (x,y) tuples
        xs = [coords[0] for coords in zone_grid.keys()]
        ys = [coords[1] for coords in zone_grid.keys()]

        if not xs or not ys:
            return

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # 3. Draw line by line
        print(f"--- Turn {turn} ---")
        for y in range(min_y, max_y + 1):
            line = ""
            for x in range(min_x, max_x + 1):
                # O(1) Lookup instead of linear search
                zone = zone_grid.get((x, y))
                drones_here = drone_grid.get((x, y), [])

                symbol = "."
                color = colors.COLORS["white"]  # Default background color

                if zone:
                    color = colors.get_color_code(zone.color)
                    # Logic: Drones > Special Zones > Normal Zones
                    if drones_here:
                        if len(drones_here) > 1:
                            # If multiple drones, show count (e.g., "3")
                            symbol = str(len(drones_here))
                        else:
                            # If single drone, show ID (e.g., "D1")
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
                        symbol = "N"

                # Formatting: 3 chars wide, centered, resets color after
                line += f"{color}{symbol:^3}{colors.RESET} "

            print(line)
        # Dynamic separator line based on width
        print("-" * ((max_x - min_x + 1) * 4))
