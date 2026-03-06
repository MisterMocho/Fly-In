import heapq
from models import Zone, Connection


class PathFinder:
    """
    Implements a cooperative pathfinding algorithm (Space-Time A*) to route
    multiple drones.

    This class manages the graph representation, reservation tables for
    collision avoidance, and heuristic calculations using a backward search
    from the goal.
    """
    def __init__(self, zones: dict[str, Zone],
                 connections: list[Connection], end_hub: str) -> None:
        """
        Initializes the PathFinder with the map data and pre-computes
        heuristics.

        Args:
            zones (dict[str, Zone]): Dictionary of all zones in the map.
            connections (list[Connection]): List of connections between zones.
            end_hub (str): The name of the destination zone (Goal).
        """
        self.zones = zones
        self.connections = connections
        self.graph: dict[str, list[str]] = self._build_graph()
        self.reservations: dict[tuple[str, int], int] = {}
        self.link_capacities: dict[tuple[str, str], int] = {}
        self.link_reservations: dict[tuple[str, str, int], int] = {}
        self._init_link_capacities()
        self.heuristic_map: dict[str, int] = \
            self._compute_true_distances(end_hub)

    def _build_graph(self) -> dict[str, list[str]]:
        """Constructs an adjacency list representation of the map graph."""
        graph: dict[str, list[str]] = {
            name: [] for name in self.zones
        }
        for conn in self.connections:
            graph[conn.zone_1].append(conn.zone_2)
            graph[conn.zone_2].append(conn.zone_1)
        return graph

    def _compute_true_distances(self, end_hub: str) -> dict[str, int]:
        """
        Performs a Backward Dijkstra search starting from the end hub.

        This calculates the exact minimal cost (in turns) from every zone to
        the end hub, accounting for specific zone costs (e.g., restricted = 2).
        This serves as an admissible and consistent heuristic for A*.

        Returns:
            dict[str, int]: A map of zone names to their true distance to
            the goal.
        """
        distances: dict[str, int] = {end_hub: 0}
        # Priority Queue: (custo_acumulado, nome_zona)
        pq: list[tuple[int, str]] = [(0, end_hub)]
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            if current_dist > distances.get(current_node, float('inf')):
                continue
            # Explorar vizinhos inversamente: quem pode chegar a current_node?
            neighbors = self.graph.get(current_node, [])
            for neighbor in neighbors:
                # Custo para mover de 'neighbor' -> 'current_node'
                # O custo é determinado pela zona de destino (current_node)
                target_zone_obj = self.zones[current_node]
                move_cost = self._get_move_cost(target_zone_obj)
                if move_cost is None:
                    continue
                new_dist = current_dist + move_cost
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))
        return distances

    def _get_link_key(self, z1: str, z2: str) -> tuple[str, str]:
        """
        Generates a canonical key for an undirected connection between two
        zones.
        Ensures that the connection (A, B) produces the same key as (B, A) by
        sorting the zone names.

        Args:
            z1 (str): Name of the first zone.
            z2 (str): Name of the second zone.

        Returns:
            tuple[str, str]: A sorted tuple representing the unique link ID.
        """
        if z1 < z2:
            return (z1, z2)
        return (z2, z1)

    def _init_link_capacities(self) -> None:
        """
        Populates the link capacity lookup table from the connection list.

        This allows O(1) access to maximum capacity constraints for any given
        connection during pathfinding.
        """
        for conn in self.connections:
            key = self._get_link_key(conn.zone_1, conn.zone_2)
            self.link_capacities[key] = conn.max_link_capacity

    def add_reservation(self, zone_name: str, time: int) -> None:
        """
        Reserves a slot in a specific zone at a specific time.

        Increments the occupancy count for the given zone-time pair. This is
        used to enforce 'max_drones' constraints per zone.

        Args:
            zone_name (str): The name of the zone to reserve.
            time (int): The simulation turn for the reservation.
        """
        current_count = self.reservations.get((zone_name, time), 0)
        self.reservations[(zone_name, time)] = current_count + 1

    def add_link_reservation(self, z1: str, z2: str, time: int) -> None:
        """
        Reserves capacity on a connection between two zones at a specific time.

        Increments the usage count for the link. This is used to enforce
        'max_link_capacity' constraints, preventing overcrowding on narrow
        paths.

        Args:
            z1 (str): The source zone of the movement.
            z2 (str): The destination zone of the movement.
            time (int): The simulation turn when the link is traversed.
        """
        key = self._get_link_key(z1, z2)
        full_key = (key[0], key[1], time)
        self.link_reservations[full_key] = (
            self.link_reservations.get(full_key, 0) + 1
        )

    def heuristic(self, start: str) -> int:
        """
        Retrieves the pre-computed true distance from the start zone to the
        goal.

        Since the 'True Distance' map is computed using a backward search from
        the goal, this lookup provides an exact or highly accurate estimate of
        the remaining cost, making the A* search extremely efficient.

        Args:
            start (str): The current zone name.

        Returns:
            int: The estimated cost (true distance) to the goal. Returns a high
            value if the zone is unreachable.
        """
        return self.heuristic_map.get(start, 999999)

    def _get_move_cost(self, zone_obj: Zone,
                       is_waiting: bool = False) -> int | None:
        """Retorna o custo de tempo para entrar numa zona ou esperar."""
        if is_waiting:
            return 1
        if zone_obj.zone_type == "blocked":
            return None
        if zone_obj.zone_type == "restricted":
            return 2
        return 1

    def find_path_with_reservations(self, start: str, end: str,
                                    start_time: int) -> list[tuple[str, int]]:
        """
        Finds a collision-free path for a drone using Space-Time A*.

        This method considers existing reservations in both zones and links
        to ensure the new path does not violate capacity constraints.

        Args:
            start (str): The starting zone name.
            end (str): The destination zone name.
            start_time (int): The simulation turn at which the drone begins.

        Returns:
            list[tuple[str, int]]: A list of (zone_name, arrival_time)
            tuples representing the path. Returns an empty list if no path
            is found.
        """
        open_set: list[tuple[float, int, str, list[tuple[str, int]]]] = []
        # A* guiado pela distância real (Heurística Admissível e Consistente)
        initial_h = self.heuristic(start)
        heapq.heappush(open_set, (start_time + initial_h, start_time,
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
                zone_obj: Zone = self.zones[next_zone_name]
                is_waiting = (next_zone_name == current_zone_name)
                # Custo base
                move_cost = self._get_move_cost(zone_obj, is_waiting)
                if move_cost is None:
                    continue
                arrival_time = current_time + move_cost
                # Verificações de Capacidade
                link_key = None
                link_max_cap = 9999
                if not is_waiting:
                    link_key = self._get_link_key(current_zone_name,
                                                  next_zone_name)
                    link_max_cap = self.link_capacities.get(link_key, 1)
                conflict = False
                for t in range(current_time + 1, arrival_time + 1):
                    count = self.reservations.get((next_zone_name, t), 0)
                    if count >= zone_obj.max_drones:
                        conflict = True
                        break
                    if not is_waiting and link_key:
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
                    h_cost = self.heuristic(next_zone_name)
                    priority_bonus = 0.5 if (zone_obj.zone_type ==
                                             "priority") else 0
                    estimated_cost = (arrival_time + h_cost - priority_bonus)
                    new_path = list(path)
                    new_path.append((next_zone_name, arrival_time))
                    heapq.heappush(open_set,
                                   (estimated_cost,
                                    arrival_time,
                                    next_zone_name,
                                    new_path))
        return []
