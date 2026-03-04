import re
from typing import Optional, Dict, List
from models import Zone, Connection


class MapParser:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.nb_drones: int = 0
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []

    def parse(self) -> None:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.splitlines()

            # 1. Primeira passagem: Encontrar nb_drones
            for line in lines:
                clean = line.split('#')[0].strip()
                if clean.startswith("nb_drones:"):
                    try:
                        self.nb_drones = int(clean.split(':')[1].strip())
                        break
                    except ValueError:
                        raise ValueError("Invalid nb_drones format.")

            if self.nb_drones == 0:
                raise ValueError("nb_drones definition missing or invalid.")

            # 2. Segunda passagem: Processar Zonas e Conexões
            for line_num, line in enumerate(lines, 1):
                clean = line.split('#')[0].strip()
                # Ignora linhas vazias ou a linha de nb_drones (já lida)
                if not clean or clean.startswith("nb_drones:"):
                    continue
                self._parse_line(clean, line_num)

        except FileNotFoundError:
            raise ValueError(f"File not found: {self.file_path}")
        self._validate_map()

    def _parse_line(self, line: str, line_num: int) -> None:
        metadata_match = re.search(r'\[(.*?)\]', line)
        metadata_str = metadata_match.group(1) if metadata_match else ""
        metadata = self._parse_metadata(metadata_str)
        base_line = re.sub(r'\s*\[.*?\]\s*', '', line).strip()
        if base_line.startswith("nb_drones:"):
            try:
                self.nb_drones = int(base_line.split(':')[1].strip())
            except ValueError:
                raise ValueError(f"Error line {line_num}: invalid nb_drones.")
        elif (base_line.startswith("start_hub:")
              or base_line.startswith("end_hub:")
              or base_line.startswith("hub:")):
            self._parse_zone(base_line, metadata, line_num)
        elif base_line.startswith("connection:"):
            self._parse_connection(base_line, metadata, line_num)
        else:
            raise ValueError(f"Unknown syntax on line: {line_num}: {line}")

    def _parse_metadata(self, metadata_str: str) -> Dict[str, str]:
        if not metadata_str:
            return {}
        meta_dict: Dict[str, str] = {}
        for item in metadata_str.split():
            if '=' in item:
                key, value = item.split('=', 1)
                meta_dict[key] = value
        return meta_dict

    def _parse_zone(self, base_line: str,
                    metadata: Dict[str, str], line_num: int) -> None:
        parts: list[str] = base_line.split()
        if len(parts) != 4:
            raise ValueError(f"Error in line {line_num}: invalid format")
        prefix = parts[0]
        name = parts[1]
        if '-' in name:
            raise ValueError(f"Error in line {line_num}: names cant have '-'")
        try:
            x = int(parts[2])
            y = int(parts[3])
        except ValueError:
            raise ValueError("Coordinates must be an int")
        raw_max = metadata.get('max_drones')
        if raw_max is not None:
            # Se o utilizador definiu manualmente, respeitamos o valor dele
            final_max = int(raw_max)
        else:
            # Se NÃO definiu (está omisso):
            if prefix in ("start_hub:", "end_hub:"):
                # Start e End ganham capacidade para todos os drones
                final_max = self.nb_drones
            else:
                # Zonas normais ganham o default 1
                final_max = 1
        zone = Zone(name, x, y,
                    zone_type=metadata.get('zone', 'normal'),
                    color=metadata.get('color'),
                    max_drones=final_max)
        self.zones[name] = zone
        if prefix == "start_hub:":
            if self.start_hub:
                raise ValueError("There can only be one start_hub")
            self.start_hub = name
        elif prefix == "end_hub:":
            if self.end_hub:
                raise ValueError("There can only be one end_hub")
            self.end_hub = name

    def _parse_connection(self, base_line: str,
                          metadata: Dict[str, str], line_num: int) -> None:
        parts = base_line.split()
        if len(parts) != 2:
            raise ValueError(f"Error on line {line_num}: invalid format")
        try:
            connectors: str = parts[1]
            zone_1, zone_2 = connectors.split('-')
        except ValueError:
            raise ValueError(f"Error on line {line_num}: invalid format")
        connected = Connection(
            zone_1,
            zone_2,
            max_link_capacity=int(metadata.get('max_link_capacity', 1))
        )
        self.connections.append(connected)

    def _validate_map(self) -> None:
        if self.nb_drones <= 0:
            raise ValueError("The number of drones must be a positive number")
        if not self.start_hub:
            raise ValueError("There must be a starting zone")
        if not self.end_hub:
            raise ValueError("There must be an end zone")
        for conn in self.connections:
            if conn.zone_1 not in self.zones or conn.zone_2 not in self.zones:
                raise ValueError(
                    f"Connect {conn.zone_1}-{conn.zone_2} are not valid zones"
                )
