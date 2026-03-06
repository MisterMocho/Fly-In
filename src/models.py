from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Zone:
    """
    Represents a node in the map graph.

    Attributes:
        name (str): Unique identifier for the zone.
        x (int): X-coordinate for visualization.
        y (int): Y-coordinate for visualization.
        zone_type (str): Type of the zone ('normal', 'blocked',
        'restricted', 'priority').
        color (Optional[str]): Color code for UI representation.
        max_drones (int): Maximum capacity of the zone at any given turn.
    """
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: Optional[str] = None
    max_drones: int = 1

    def __post_init__(self) -> None:
        """Validates zone attributes after initialization."""
        valid_types = {"normal", "blocked", "restricted", "priority"}
        if self.zone_type not in valid_types:
            raise ValueError(f"Zone {self.zone_type} "
                             "not recognized and therefore invalid")
        if self.max_drones < 1:
            raise ValueError("max_drones must be positive in the "
                             f"zone {self.name}")


@dataclass
class Connection:
    """
    Represents a directed or undirected edge between two zones.

    Attributes:
        zone_1 (str): Name of the first connected zone.
        zone_2 (str): Name of the second connected zone.
        max_link_capacity (int): Maximum number of drones that can
        traverse this link simultaneously.
    """
    zone_1: str
    zone_2: str
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        """Validates connection attributes after initialization."""
        if self.max_link_capacity < 1:
            raise ValueError("max_link_capacity must be higher than 1")


@dataclass
class Drone:
    """
    Represents an agent within the simulation.

    Attributes:
        drone_id (int): Unique identifier for the drone.
        current_zone (str): The name of the zone the drone currently occupies.
        path (list[str]): List of zone names representing the planned route.
        status (str): Current status of the drone (e.g., 'ready', 'flying').
        wait_time (int): Remaining turns to wait before entering a
        restricted zone.
    """
    drone_id: int
    current_zone: str
    path: list[str] = field(default_factory=lambda: [])
    status: str = "ready"
    wait_time: int = 0

    def has_arrived(self, end_zone: str) -> bool:
        """Checks if the drone has reached the destination zone."""
        return self.current_zone == end_zone

    def set_path(self, new_path: list[str]) -> None:
        """
        Assigns a new navigation path to the drone.

        Removes the first step if it corresponds to the drone's current
        location.
        """
        self.path = new_path
        if self.path and self.path[0] == self.current_zone:
            self.path.pop(0)
