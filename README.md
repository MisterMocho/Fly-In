*This project has been created as part of the 42 curriculum by luida-cu.*

# Fly-in: Autonomous Drone Routing System

## Description

**Fly-in** is a high-performance simulation engine designed to route a fleet of autonomous drones through complex networks of connected zones.

The primary goal is to navigate all drones from a **Start Hub** to an **End Hub** in the minimum number of simulation turns possible.

This project tackles the challenge of **Multi-Agent Pathfinding (MAPF)** under strict constraints:
* **Capacity Limits:** Zones and connections have maximum occupancy limits.
* **Dynamic Costs:** Different zone types impose different movement penalties (e.g., Restricted zones take 2 turns to traverse).
* **Collision Avoidance:** Algorithms must prevent conflicts in both space and time.

The system is capable of solving scenarios ranging from simple linear paths to the "Impossible Dream" challenger map, requiring extreme algorithmic optimization.

## Instructions

### Prerequisites
* Python 3.10 or higher.
* `make` utility.

### Installation
To set up the environment and install necessary dependencies (flake8, mypy):
```bash
make install
```
### Execution:

To run the simulation with a specific map:
```bash
make run ARGS="maps/easy/01_linear_path.txt"
```
### Visual Mode:

To enable the step-by-step visual representation of the map and drone movements:
```bash
make visual ARGS="maps/hard/01_maze_nightmare.txt"
```
### Linting:

Check code quality and type safety:
```bash
make lint
make lint-strict
```
### Cleaning: 

Remove temporary files and caches:
```bash
make clean
```
## Algorithm & Implementation Strategy

To solve the Multi-Agent Pathfinding (MAPF) problem efficiently, this project implements a **Space-Time A* (Cooperative Pathfinding)** algorithm.

### 1. Cooperative A* (Space-Time)
Unlike standard A* which plans on a static 2D grid `(x, y)`, our algorithm plans in 3D `(location, time)`.
* **Sequential Planning:** Drones calculate their paths one by one based on priority.
* **Reservation Table:** Once a drone calculates a path, it reserves specific zones and links for specific time steps.
* **Conflict Avoidance:** Subsequent drones treat these reserved space-time slots as dynamic obstacles.

### 2. Heuristic: Backward Dijkstra (True Distance)
To ensure the A* search is extremely efficient, we pre-compute a **Backward Dijkstra** map starting from the Goal node.
* **True Cost:** This map stores the exact movement cost (in turns) from every zone to the end, accounting for terrain types like Restricted zones (cost of 2).
* **Admissibility:** This heuristic is admissible and consistent, allowing the A* algorithm to find the optimal path through the static geometry almost instantly, only branching when dynamic conflicts are encountered.

### 3. Handling Constraints
* **Restricted Zones:** The engine handles the 2-turn cost by treating the drone as "in-transit" during the intermediate turn. It occupies the link capacity but not the destination zone capacity until arrival.
* **Link Capacity:** The system tracks usage of connections between zones to prevent overcrowding in bottlenecks, regardless of the direction of travel.

## Visual Representation

The project includes a terminal-based visualizer that renders the simulation state at every turn using ANSI escape codes. This feature is crucial for debugging and understanding bottleneck behaviors.

* **Grid Rendering:** Displays the map layout while preserving relative coordinates.
* **Dynamic Symbols:**
    * `S` / `E`: Start and End hubs.
    * `D<ID>`: A single drone (e.g., `D1`).
    * `<Number>`: A count of drones if multiple occupy one hub.
* **Color Coding:**
    * **Green:** Start/End hubs.
    * **Red/Orange:** Restricted zones or bottlenecks.
    * **Cyan:** Priority zones.
    * **White:** Normal paths.

## Resources

### References
* **Pathfinding:** Introduction to A* Search.
* **Heuristics:** Dijkstra's Algorithm and True Distance heuristics.
* **Python:** `heapq` documentation for Priority Queues.

### AI Usage
Artificial Intelligence tools were utilized in specific parts of this development process as permitted by the subject:
* **Refactoring & Modularity:** AI assisted in separating the `PathFinder` logic into helper methods (e.g., `_get_move_cost`) to centralize rule management.
* **Debugging Logic:** Used to analyze the behavior of Restricted Zones and the "Wait" mechanic to ensure compliance with the subject's turn-counting rules.
* **Makefile Generation:** Assisted in creating a robust Makefile compliant with the subject's specific requirements.