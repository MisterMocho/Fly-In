import heapq
from models import Zone, Connection


class PathFinder:
    """
    Handles pathfinding logic using a cooperative A* algorithm (Space-Time A*).

    This class is responsible for calculating the optimal path for drones while
    respecting static map constraints (walls, blocked zones) and dynamic
    constraints (reservations from other drones).
    """
    def __init__(self, zones: dict[str, Zone],
                 connections: list[Connection]) -> None:
        """
        Initializes the PathFinder with map data.

        Args:
            zones: A dictionary mapping zone names to Zone objects.
            connections: A list of Connection objects defining the graph edges.
        """
        self.zones = zones
        self.connections = connections
        self.graph: dict[str, list[str]] = self._build_graph()
        self.reservations: dict[tuple[str, int], int] = {}
        self.link_capacities: dict[tuple[str, str], int] = {}
        self.link_reservations: dict[tuple[str, str, int], int] = {}
        self._init_link_capacities()

    def _build_graph(self) -> dict[str, list[str]]:
        """
        Constructs an adjacency dictionary from the connection list.

        Returns:
            A dictionary where keys are zone names and values are lists of
            neighboring zone names.
        """
        graph: dict[str, list[str]] = {
            name: [] for name in self.zones
        }
        for conn in self.connections:
            graph[conn.zone_1].append(conn.zone_2)
            graph[conn.zone_2].append(conn.zone_1)
        return graph

    def _get_link_key(self, z1: str, z2: str) -> tuple[str, str]:
        if z1 < z2:
            return (z1, z2)
        return (z2, z1)

    def _init_link_capacities(self) -> None:
        for conn in self.connections:
            # Ordenamos para garantir que A-B é igual a B-A
            key = self._get_link_key(conn.zone_1, conn.zone_2)
            # AQUI: Usamos o valor que vem do parser/models
            self.link_capacities[key] = conn.max_link_capacity

    def add_reservation(self, zone_name: str, time: int) -> None:
        """
        Registers a drone's presence in a specific zone at a specific time.

        Used to update the dynamic obstacle map after a path is finalized.

        Args:
            zone_name: The name of the zone to reserve.
            time: The time step (turn) when the zone will be occupied.
        """
        current_count = self.reservations.get((zone_name, time), 0)
        self.reservations[(zone_name, time)] = current_count + 1

    def add_link_reservation(self, z1: str, z2: str, time: int) -> None:
        key = self._get_link_key(z1, z2)
        # Chave composta: (Zona1, Zona2, Tempo)
        full_key = (key[0], key[1], time)
        self.link_reservations[full_key] = (
            self.link_reservations.get(full_key, 0) + 1
        )

    def heuristic(self, start: str, end: str) -> int:
        """
        Calculates the Manhattan distance heuristic between two zones.

        Args:
            start: The name of the starting zone.
            end: The name of the target zone.

        Returns:
            The Manhattan distance (|dx| + |dy|) as an integer.
        """
        z1 = self.zones[start]
        z2 = self.zones[end]
        return int(abs(z1.x - z2.x) + abs(z1.y - z2.y))

    def find_path_with_reservations(self, start: str, end: str,
                                    start_time: int) -> list[tuple[str, int]]:
        """
        Finds the shortest path respecting capacity constraints (reservations).

        Implements Space-Time A* search. It considers time as a dimension to
        avoid collisions with drones that have already reserved their paths.

        Args:
            start: The starting zone name.
            end: The destination zone name.
            start_time: The simulation turn when the drone begins moving.

        Returns:
            A list of tuples (zone_name, arrival_time).
            Returns an empty list if no path is found.
        """
        open_set: list[tuple[float, int, str, list[tuple[str, int]]]] = []
        initial_h = self.heuristic(start, end)
        heapq.heappush(open_set, (initial_h, start_time,
                                  start, [(start, start_time)]))
        visited: set[tuple[str, int]] = set()
        visited.add((start, start_time))
        while open_set:
            _, current_time, current_zone_name, path = heapq.heappop(open_set)
            if current_zone_name == end:
                return path
            possible_moves = (self.graph.get(current_zone_name, [])
                              + [current_zone_name])
            for next_zone_name in possible_moves:
                zone_obj = self.zones[next_zone_name]
                if zone_obj.zone_type == "blocked":
                    continue
                is_waiting = (next_zone_name == current_zone_name)
                move_cost = 1
                if not is_waiting and zone_obj.zone_type == "restricted":
                    move_cost = 2
                arrival_time = current_time + move_cost
                link_key = None
                link_max_cap = 9999
                if not is_waiting:
                    link_key = self._get_link_key(current_zone_name,
                                                  next_zone_name)
                    # Se não houver registo, assume 1 (padrão do enunciado)
                    link_max_cap = self.link_capacities.get(link_key, 1)
                conflict = False
                for t in range(current_time + 1, arrival_time + 1):
                    count = self.reservations.get((next_zone_name, t), 0)
                    if count >= zone_obj.max_drones:
                        conflict = True
                        break
                    if not is_waiting and link_key:
                        # Verifica ocupação do link neste turno específico
                        current_link_usage = self.link_reservations.get(
                            (link_key[0], link_key[1], t), 0
                        )
                        if current_link_usage >= link_max_cap:
                            conflict = True
                            break
                if conflict:
                    continue
                state = (next_zone_name, arrival_time)
                if state not in visited:
                    visited.add(state)
                    priority_bonus = 0.5 if (zone_obj.zone_type ==
                                             "priority") else 0
                    estimated_cost = (arrival_time +
                                      self.heuristic(next_zone_name, end) -
                                      priority_bonus)
                    new_path = list(path)
                    new_path.append((next_zone_name, arrival_time))
                    heapq.heappush(open_set,
                                   (estimated_cost,
                                    arrival_time,
                                    next_zone_name,
                                    new_path))
        return []
