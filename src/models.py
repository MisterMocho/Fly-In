from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: Optional[str] = None
    max_drones: int = 1

    def __post_init__(self) -> None:
        valid_types = {"normal", "blocked", "restricted", "priority"}
        if self.zone_type not in valid_types:
            raise ValueError(f"Zone {self.zone_type} "
                             "not recognized and therefore invalid")
        if self.max_drones < 1:
            raise ValueError("max_drones must be positive in the "
                             f"zone {self.name}")


@dataclass
class Connection:
    zone_1: str
    zone_2: str
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        if self.max_link_capacity < 1:
            raise ValueError("max_link_capacity must be higher than 1")


@dataclass
class Drone:
    drone_id: int
    current_zone: str
    path: list[str] = field(default_factory=lambda: [])
    status: str = "ready"
    wait_time: int = 0

    def has_arrived(self, end_zone: str) -> bool:
        return self.current_zone == end_zone

    def set_path(self, new_path: list[str]) -> None:
        self.path = new_path
        if self.path and self.path[0] == self.current_zone:
            self.path.pop(0)
