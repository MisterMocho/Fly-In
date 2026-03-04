from models import Drone, Zone, Connection
from parser import MapParser
from pathfinder import PathFinder
from visualizer import Visualizer


class Simulation:
    def __init__(self, parser: MapParser) -> None:
        self.zones: dict[str, Zone] = parser.zones
        self.connections: list[Connection] = parser.connections
        if parser.start_hub is None or parser.end_hub is None:
            raise ValueError("Parser failed to start properly, hubs missing.")
        self.start_hub: str = parser.start_hub
        self.end_hub: str = parser.end_hub
        self.nb_drones: int = parser.nb_drones
        self.drones: list[Drone] = []
        self.turn: int = 0
        self.pathfinder = PathFinder(self.zones, self.connections)
        self._initialize_drones()

    def _initialize_drones(self) -> None:
        print(f"[Debug] Planning routes for {self.nb_drones} drones...")
        for i in range(1, self.nb_drones + 1):
            drone = Drone(drone_id=i, current_zone=self.start_hub)
            self.drones.append(drone)
        for drone in self.drones:
            path = self.pathfinder.find_path_with_reservations(
                self.start_hub,
                self.end_hub,
                start_time=0
            )
            if not path:
                print(f"[Warning] D{drone.drone_id} with no possible route")
            else:
                simple_path = [step[0] for step in path]
                drone.set_path(simple_path)
                self._reserve_path_capacity(path)

    def _reserve_path_capacity(self, path: list[tuple[str, int]]) -> None:
        if not path:
            return

        # Opcional: Reservar a posição inicial no tempo 0
        start_zone, start_time = path[0]
        self.pathfinder.add_reservation(start_zone, start_time)

        # Itera pelo caminho par a par para preencher os intervalos de tempo
        for i in range(len(path) - 1):
            prev_zone, t_start = path[i]
            curr_zone, t_end = path[i+1]

            # Se a zona for a mesma, é um WAIT, não consome Link
            is_waiting = (curr_zone == prev_zone)

            # Durante o intervalo de movimento/trânsito
            for t in range(t_start + 1, t_end + 1):
                # 1. Reserva a Zona de destino
                self.pathfinder.add_reservation(curr_zone, t)
                # 2. Reserva o Link usado (Se houve movimento real)
                if not is_waiting:
                    self.pathfinder.add_link_reservation(prev_zone,
                                                         curr_zone, t)

    def run(self, visual_mode: bool = False) -> None:
        print("--- Flying ---")
        if visual_mode:
            Visualizer.print_map(self.zones, self.drones, self.turn,
                                 self.start_hub, self.end_hub)
        all_arrived = False
        while not all_arrived and self.turn < 200:
            self.turn += 1
            moves_this_turn: list[str] = []
            for drone in self.drones:
                if drone.has_arrived(self.end_hub):  # why self.end_hub
                    continue

                if drone.path:
                    self._move_command(drone, moves_this_turn)

            if visual_mode:
                Visualizer.print_map(self.zones, self.drones, self.turn,
                                     self.start_hub, self.end_hub)

            if moves_this_turn:
                print(f"Turn {self.turn}")
                print(" ".join(moves_this_turn))

            if all(d.has_arrived(self.end_hub) for d in self.drones):
                all_arrived = True
        print(f"--- Fim (Turnos: {self.turn}) ---")

    def _move_command(self, drone: Drone, moves_this_turn: list[str]) -> None:
        next_target = drone.path[0]
        # Lógica de Wait Time para Zonas Restritas (Custo 2)
        if drone.wait_time > 0:
            drone.wait_time -= 1
            # Ainda a voar (na conexão)?
            if drone.wait_time > 0:
                # Opcional: mostrar que está na conexão
                moves_this_turn.append(f"D{drone.drone_id}-{next_target}")
            else:
                # Chegou!
                drone.current_zone = next_target
                drone.path.pop(0)
                moves_this_turn.append(f"D{drone.drone_id}-{next_target}")
            return

        # Iniciar Movimento
        if next_target == drone.current_zone:
            # Ação de Esperar (Wait) -> Removemos do path mas não movemos
            drone.path.pop(0)
            return

        zone_type = self.zones[next_target].zone_type

        if zone_type == "restricted":
            # Inicia viagem de 2 turnos
            drone.wait_time = 1  # Falta 1 turno de espera
            moves_this_turn.append(f"D{drone.drone_id}-{next_target}")
        else:
            # Movimento normal (1 turno)
            drone.current_zone = next_target
            drone.path.pop(0)
            moves_this_turn.append(f"D{drone.drone_id}-{next_target}")
