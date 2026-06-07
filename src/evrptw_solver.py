from __future__ import annotations

from dataclasses import dataclass, field, asdict
from math import dist
from pathlib import Path
import argparse
import json
import time
from typing import Dict, Iterable, List, Optional, Tuple


CHARGER_MODES: Dict[str, Dict[str, float]] = {
    "normal": {"time_per_unit": 3.47, "cost_per_unit": 1.0},
    "fast": {"time_per_unit": 0.62, "cost_per_unit": 1.1},
    "super_fast": {"time_per_unit": 0.28, "cost_per_unit": 1.2},
}


@dataclass(frozen=True)
class Node:
    node_id: str
    node_type: str
    x: float
    y: float
    demand: float
    ready_time: float
    due_time: float
    service_time: float


@dataclass(frozen=True)
class InstanceConfig:
    battery_capacity: float
    load_capacity: float
    consumption_rate: float
    inverse_refueling_rate: float
    velocity: float


@dataclass
class EVRPTWInstance:
    name: str
    depot: Node
    stations: List[Node]
    customers: List[Node]
    config: InstanceConfig
    nodes_by_id: Dict[str, Node]
    distance_matrix: Dict[Tuple[str, str], float]


@dataclass
class RechargeEvent:
    charge_added: float
    charger_mode: str
    charging_time: float
    charging_cost: float


@dataclass
class StopRecord:
    node_id: str
    node_type: str
    arrival_time: float
    departure_time: float
    battery_after: float
    load_used: float
    recharge: Optional[RechargeEvent] = None


@dataclass
class RouteResult:
    route_id: int
    distance: float = 0.0
    demand_served: float = 0.0
    stops: List[StopRecord] = field(default_factory=list)


@dataclass
class SolverResult:
    instance_name: str
    feasible: bool
    vehicles_used: int
    total_distance: float
    total_energy_cost: float
    total_charging_time: float
    runtime_seconds: float
    routes: List[RouteResult]
    unserved_customers: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def parse_instance_file(path: Path) -> EVRPTWInstance:
    lines = [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()]
    node_lines: List[str] = []
    config_values: Dict[str, float] = {}

    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("StringID"):
            continue
        if stripped.startswith("Q "):
            config_values["battery_capacity"] = _extract_config_value(stripped)
            continue
        if stripped.startswith("C "):
            config_values["load_capacity"] = _extract_config_value(stripped)
            continue
        if stripped.startswith("r "):
            config_values["consumption_rate"] = _extract_config_value(stripped)
            continue
        if stripped.startswith("g "):
            config_values["inverse_refueling_rate"] = _extract_config_value(stripped)
            continue
        if stripped.startswith("v "):
            config_values["velocity"] = _extract_config_value(stripped)
            continue
        node_lines.append(stripped)

    if len(config_values) != 5:
        raise ValueError(f"Missing configuration values in {path}")

    nodes: List[Node] = []
    for line in node_lines:
        parts = line.split()
        if len(parts) != 8:
            raise ValueError(f"Unexpected node format: {line}")
        nodes.append(
            Node(
                node_id=parts[0],
                node_type=parts[1],
                x=float(parts[2]),
                y=float(parts[3]),
                demand=float(parts[4]),
                ready_time=float(parts[5]),
                due_time=float(parts[6]),
                service_time=float(parts[7]),
            )
        )

    depot = next(node for node in nodes if node.node_type == "d")
    stations = [node for node in nodes if node.node_type == "f"]
    customers = [node for node in nodes if node.node_type == "c"]
    nodes_by_id = {node.node_id: node for node in nodes}
    distance_matrix = {
        (a.node_id, b.node_id): euclidean_distance(a, b) for a in nodes for b in nodes
    }
    config = InstanceConfig(**config_values)
    return EVRPTWInstance(
        name=path.stem,
        depot=depot,
        stations=stations,
        customers=customers,
        config=config,
        nodes_by_id=nodes_by_id,
        distance_matrix=distance_matrix,
    )


def _extract_config_value(line: str) -> float:
    return float(line.split("/")[1])


def euclidean_distance(a: Node, b: Node) -> float:
    return float(dist((a.x, a.y), (b.x, b.y)))


def plot_instance_map(instance: EVRPTWInstance, output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        _write_svg_map(instance, output_path.with_suffix(".svg"))
        return

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(
        [instance.depot.x],
        [instance.depot.y],
        c="red",
        marker="s",
        s=90,
        label="Depot",
    )
    ax.scatter(
        [node.x for node in instance.stations],
        [node.y for node in instance.stations],
        c="blue",
        marker="^",
        s=40,
        label="Stations",
    )
    ax.scatter(
        [node.x for node in instance.customers],
        [node.y for node in instance.customers],
        c="green",
        marker="o",
        s=20,
        label="Customers",
    )
    ax.set_title(f"Benchmark Map: {instance.name}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def _write_svg_map(instance: EVRPTWInstance, output_path: Path) -> None:
    all_nodes = [instance.depot, *instance.stations, *instance.customers]
    min_x = min(node.x for node in all_nodes)
    max_x = max(node.x for node in all_nodes)
    min_y = min(node.y for node in all_nodes)
    max_y = max(node.y for node in all_nodes)
    width = 960
    height = 760
    margin = 40

    def scale_x(value: float) -> float:
        span = max(max_x - min_x, 1.0)
        return margin + ((value - min_x) / span) * (width - 2 * margin)

    def scale_y(value: float) -> float:
        span = max(max_y - min_y, 1.0)
        return height - margin - ((value - min_y) / span) * (height - 2 * margin)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white" />',
        f'<text x="{margin}" y="24" font-family="Arial" font-size="20">Benchmark Map: {instance.name}</text>',
    ]

    for station in instance.stations:
        x, y = scale_x(station.x), scale_y(station.y)
        parts.append(f'<polygon points="{x},{y-5} {x-5},{y+5} {x+5},{y+5}" fill="#2563eb" />')
    for customer in instance.customers:
        x, y = scale_x(customer.x), scale_y(customer.y)
        parts.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#16a34a" />')
    depot_x, depot_y = scale_x(instance.depot.x), scale_y(instance.depot.y)
    parts.append(
        f'<rect x="{depot_x-6}" y="{depot_y-6}" width="12" height="12" fill="#dc2626" />'
    )
    parts.append("</svg>")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts), encoding="utf-8")


def solve_instance(path: Path) -> SolverResult:
    started = time.perf_counter()
    instance = parse_instance_file(path)
    unserved = sorted(instance.customers, key=lambda node: (node.ready_time, node.due_time, node.node_id))
    routes: List[RouteResult] = []
    notes: List[str] = []

    route_id = 1
    while unserved:
        route, served = _build_route(instance, route_id, unserved)
        if not served:
            fallback_customer = unserved[0]
            route, served = _build_single_customer_route(instance, route_id, fallback_customer)
        if not served:
            notes.append(f"Unable to serve customer {unserved[0].node_id} with current heuristic.")
            break
        served_ids = {node.node_id for node in served}
        unserved = [node for node in unserved if node.node_id not in served_ids]
        routes.append(route)
        route_id += 1

    feasible = not unserved
    result = SolverResult(
        instance_name=instance.name,
        feasible=feasible,
        vehicles_used=len(routes),
        total_distance=round(sum(route.distance for route in routes), 3),
        total_energy_cost=round(sum(_route_energy_cost(route) for route in routes), 3),
        total_charging_time=round(sum(_route_charging_time(route) for route in routes), 3),
        runtime_seconds=round(time.perf_counter() - started, 4),
        routes=routes,
        unserved_customers=[node.node_id for node in unserved],
        notes=notes,
    )
    return result


def _build_route(
    instance: EVRPTWInstance,
    route_id: int,
    candidates: List[Node],
) -> Tuple[RouteResult, List[Node]]:
    route = RouteResult(route_id=route_id)
    served: List[Node] = []
    current = instance.depot
    current_time = 0.0
    current_battery = instance.config.battery_capacity
    used_load = 0.0
    route.stops.append(
        StopRecord(
            node_id=current.node_id,
            node_type="depot",
            arrival_time=0.0,
            departure_time=0.0,
            battery_after=current_battery,
            load_used=0.0,
        )
    )

    while True:
        best_plan = None
        best_customer = None
        served_ids = {node.node_id for node in served}
        for customer in candidates:
            if customer.node_id in served_ids:
                continue
            if used_load + customer.demand > instance.config.load_capacity:
                continue
            plan = _plan_move_to_customer(
                instance,
                current,
                customer,
                current_time,
                current_battery,
                used_load,
            )
            if not plan:
                continue
            score = (customer.due_time, plan["end_time"], plan["distance_added"])
            if best_plan is None or score < best_plan["score"]:
                best_plan = {**plan, "score": score}
                best_customer = customer

        if best_plan is None:
            break

        for stop in best_plan["stops"]:
            route.stops.append(stop)
        route.distance += best_plan["distance_added"]
        route.demand_served += best_customer.demand
        served.append(best_customer)
        current = best_customer
        current_time = best_plan["end_time"]
        current_battery = best_plan["end_battery"]
        used_load += best_customer.demand

    close_plan = _plan_return_to_depot(instance, current, current_time, current_battery, used_load)
    if close_plan is None:
        # If the route has no served customers, signal failure to caller.
        if not served:
            return route, []
        raise RuntimeError(f"Could not close route {route_id} back to depot.")

    for stop in close_plan["stops"]:
        route.stops.append(stop)
    route.distance += close_plan["distance_added"]
    return route, served


def _build_single_customer_route(
    instance: EVRPTWInstance,
    route_id: int,
    customer: Node,
) -> Tuple[RouteResult, List[Node]]:
    return _build_route(instance, route_id, [customer])


def _plan_move_to_customer(
    instance: EVRPTWInstance,
    current: Node,
    customer: Node,
    current_time: float,
    current_battery: float,
    used_load: float,
):
    direct = _travel_and_service(instance, current, customer, current_time, current_battery, used_load)
    if direct and _has_escape_path(instance, customer, direct["end_time"], direct["end_battery"]):
        return direct

    best = None
    for station in _reachable_stations(instance, current, current_battery):
        station_arrival = current_time + _distance(instance, current, station) / instance.config.velocity
        battery_at_station = current_battery - _energy(instance, current, station)
        for mode in CHARGER_MODES:
            plan = _charge_then_service(
                instance,
                current,
                station,
                customer,
                station_arrival,
                battery_at_station,
                current_time,
                used_load,
                mode,
            )
            if not plan:
                continue
            if not _has_escape_path(instance, customer, plan["end_time"], plan["end_battery"]):
                continue
            score = (plan["end_time"], plan["distance_added"], plan["charging_cost"])
            if best is None or score < best["score"]:
                best = {**plan, "score": score}
    return best


def _travel_and_service(
    instance: EVRPTWInstance,
    start: Node,
    customer: Node,
    start_time: float,
    start_battery: float,
    used_load: float,
):
    distance = _distance(instance, start, customer)
    energy = _energy(instance, start, customer)
    if start_battery + 1e-9 < energy:
        return None
    arrival = start_time + distance / instance.config.velocity
    if arrival > customer.due_time + 1e-9:
        return None
    service_start = max(arrival, customer.ready_time)
    departure = service_start + customer.service_time
    return {
        "distance_added": distance,
        "charging_cost": 0.0,
        "stops": [
            StopRecord(
                node_id=customer.node_id,
                node_type="customer",
                arrival_time=round(arrival, 3),
                departure_time=round(departure, 3),
                battery_after=round(start_battery - energy, 3),
                load_used=round(used_load + customer.demand, 3),
            )
        ],
        "end_time": departure,
        "end_battery": start_battery - energy,
    }


def _charge_then_service(
    instance: EVRPTWInstance,
    start: Node,
    station: Node,
    customer: Node,
    station_arrival: float,
    battery_at_station: float,
    route_start_time: float,
    used_load: float,
    mode: str,
):
    distance_to_station = _distance(instance, start, station)
    distance_to_customer = _distance(instance, station, customer)
    energy_to_customer = _energy(instance, station, customer)
    escape_reserve = _minimum_escape_energy(instance, customer)
    target_energy = energy_to_customer + escape_reserve
    charge_needed = max(0.0, target_energy - battery_at_station)
    charge_needed = min(charge_needed, instance.config.battery_capacity - battery_at_station)
    if charge_needed < 0.0:
        return None

    charging_time = charge_needed * CHARGER_MODES[mode]["time_per_unit"]
    departure_station = station_arrival + charging_time
    arrival_customer = departure_station + distance_to_customer / instance.config.velocity
    if arrival_customer > customer.due_time + 1e-9:
        return None
    service_start = max(arrival_customer, customer.ready_time)
    departure_customer = service_start + customer.service_time
    end_battery = battery_at_station + charge_needed - energy_to_customer
    if end_battery < -1e-9:
        return None

    return {
        "distance_added": distance_to_station + distance_to_customer,
        "charging_cost": charge_needed * CHARGER_MODES[mode]["cost_per_unit"],
        "stops": [
            StopRecord(
                node_id=station.node_id,
                node_type="station",
                arrival_time=round(station_arrival, 3),
                departure_time=round(departure_station, 3),
                battery_after=round(battery_at_station + charge_needed, 3),
                load_used=round(used_load, 3),
                recharge=RechargeEvent(
                    charge_added=round(charge_needed, 3),
                    charger_mode=mode,
                    charging_time=round(charging_time, 3),
                    charging_cost=round(charge_needed * CHARGER_MODES[mode]["cost_per_unit"], 3),
                ),
            ),
            StopRecord(
                node_id=customer.node_id,
                node_type="customer",
                arrival_time=round(arrival_customer, 3),
                departure_time=round(departure_customer, 3),
                battery_after=round(end_battery, 3),
                load_used=round(used_load + customer.demand, 3),
            ),
        ],
        "end_time": departure_customer,
        "end_battery": end_battery,
    }


def _plan_return_to_depot(
    instance: EVRPTWInstance,
    current: Node,
    current_time: float,
    current_battery: float,
    used_load: float,
):
    depot = instance.depot
    if current.node_id == depot.node_id:
        return {"stops": [], "distance_added": 0.0}

    path = _find_return_path(instance, current, current_battery)
    if not path:
        return None

    stops: List[StopRecord] = []
    distance_added = 0.0
    node = current
    battery = current_battery
    now = current_time

    for idx, next_node in enumerate(path):
        distance = _distance(instance, node, next_node)
        energy = _energy(instance, node, next_node)
        if battery + 1e-9 < energy:
            return None
        arrival = now + distance / instance.config.velocity
        battery -= energy
        distance_added += distance

        if next_node.node_type == "f":
            next_hop = path[idx + 1] if idx + 1 < len(path) else depot
            charge_target = _energy(instance, next_node, next_hop)
            margin = 1.0 if next_hop.node_type != "d" else 0.0
            charge_needed = max(0.0, min(instance.config.battery_capacity - battery, charge_target + margin - battery))
            mode = _best_mode_for_leg(
                instance=instance,
                station=next_node,
                arrival_time=arrival,
                charge_needed=charge_needed,
                leg_distance=charge_target,
            )
            charging_time = charge_needed * CHARGER_MODES[mode]["time_per_unit"]
            charging_cost = charge_needed * CHARGER_MODES[mode]["cost_per_unit"]
            now = arrival + charging_time
            battery += charge_needed
            stops.append(
                StopRecord(
                    node_id=next_node.node_id,
                    node_type="station",
                    arrival_time=round(arrival, 3),
                    departure_time=round(now, 3),
                    battery_after=round(battery, 3),
                    load_used=round(used_load, 3),
                    recharge=RechargeEvent(
                        charge_added=round(charge_needed, 3),
                        charger_mode=mode,
                        charging_time=round(charging_time, 3),
                        charging_cost=round(charging_cost, 3),
                    ),
                )
            )
        else:
            now = arrival
            stops.append(
                StopRecord(
                    node_id=next_node.node_id,
                    node_type="depot",
                    arrival_time=round(arrival, 3),
                    departure_time=round(arrival, 3),
                    battery_after=round(battery, 3),
                    load_used=round(used_load, 3),
                )
            )
        node = next_node
    return {"stops": stops, "distance_added": distance_added}


def _find_return_path(
    instance: EVRPTWInstance,
    current: Node,
    current_battery: float,
):
    depot = instance.depot
    if current_battery + 1e-9 >= _energy(instance, current, depot):
        return [depot]

    station_by_id = {station.node_id: station for station in instance.stations}
    queue: List[Node] = [station for station in _reachable_stations(instance, current, current_battery)]
    if not queue:
        return None
    parents: Dict[str, Optional[str]] = {station.node_id: None for station in queue}
    seen = set(parents)

    while queue:
        station = queue.pop(0)
        if instance.config.battery_capacity + 1e-9 >= _energy(instance, station, depot):
            path: List[Node] = [depot]
            cursor = station.node_id
            while cursor is not None:
                path.append(station_by_id[cursor])
                cursor = parents[cursor]
            path.reverse()
            return path
        for next_station in instance.stations:
            if next_station.node_id in seen or next_station.node_id == station.node_id:
                continue
            if instance.config.battery_capacity + 1e-9 >= _energy(instance, station, next_station):
                seen.add(next_station.node_id)
                parents[next_station.node_id] = station.node_id
                queue.append(next_station)
    return None


def _best_mode_for_leg(
    instance: EVRPTWInstance,
    station: Node,
    arrival_time: float,
    charge_needed: float,
    leg_distance: float,
) -> str:
    depot_due = instance.depot.due_time
    feasible_modes = []
    for mode, data in CHARGER_MODES.items():
        charging_time = charge_needed * data["time_per_unit"]
        if arrival_time + charging_time + leg_distance / instance.config.velocity <= depot_due + 1e-9:
            feasible_modes.append((data["cost_per_unit"], data["time_per_unit"], mode))
    if feasible_modes:
        feasible_modes.sort()
        return feasible_modes[0][2]
    return "super_fast"


def _has_escape_path(
    instance: EVRPTWInstance,
    current: Node,
    current_time: float,
    current_battery: float,
) -> bool:
    depot_energy = _energy(instance, current, instance.depot)
    if current_battery + 1e-9 >= depot_energy:
        arrival = current_time + _distance(instance, current, instance.depot) / instance.config.velocity
        return arrival <= instance.depot.due_time + 1e-9
    return any(True for _ in _reachable_stations(instance, current, current_battery))


def _minimum_escape_energy(instance: EVRPTWInstance, current: Node) -> float:
    energies = [_energy(instance, current, instance.depot)]
    energies.extend(_energy(instance, current, station) for station in instance.stations if station.node_id != current.node_id)
    return min(energies)


def _reachable_stations(instance: EVRPTWInstance, current: Node, current_battery: float) -> Iterable[Node]:
    for station in instance.stations:
        if station.node_id == current.node_id:
            continue
        if current_battery + 1e-9 >= _energy(instance, current, station):
            yield station


def _distance(instance: EVRPTWInstance, a: Node, b: Node) -> float:
    return instance.distance_matrix[(a.node_id, b.node_id)]


def _energy(instance: EVRPTWInstance, a: Node, b: Node) -> float:
    return _distance(instance, a, b) * instance.config.consumption_rate


def _route_energy_cost(route: RouteResult) -> float:
    total = 0.0
    for stop in route.stops:
        if stop.recharge:
            total += stop.recharge.charging_cost
    return total


def _route_charging_time(route: RouteResult) -> float:
    total = 0.0
    for stop in route.stops:
        if stop.recharge:
            total += stop.recharge.charging_time
    return total


def result_to_dict(result: SolverResult) -> dict:
    return asdict(result)


def write_result_json(result: SolverResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")


def run_benchmark(instance_paths: List[Path], output_csv: Path) -> List[SolverResult]:
    results = [solve_instance(path) for path in instance_paths]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8") as handle:
        handle.write(
            "instance_name,feasible,vehicles_used,total_distance,total_energy_cost,total_charging_time,runtime_seconds,unserved_count\n"
        )
        for result in results:
            handle.write(
                f"{result.instance_name},{result.feasible},{result.vehicles_used},{result.total_distance},"
                f"{result.total_energy_cost},{result.total_charging_time},{result.runtime_seconds},"
                f"{len(result.unserved_customers)}\n"
            )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple EVRPTW-FC heuristic solver")
    parser.add_argument("instance", nargs="?", help="Path to one instance file")
    parser.add_argument("--plot", action="store_true", help="Generate a benchmark map plot")
    parser.add_argument("--benchmark", nargs="*", help="Run multiple instance files and export CSV")
    args = parser.parse_args()

    if args.benchmark:
        paths = [Path(value) for value in args.benchmark]
        results = run_benchmark(paths, Path("outputs") / "benchmark_results.csv")
        for result in results:
            print(json.dumps(result_to_dict(result), indent=2))
        return

    if not args.instance:
        raise SystemExit("Provide an instance path or --benchmark paths.")

    instance_path = Path(args.instance)
    result = solve_instance(instance_path)
    if args.plot:
        instance = parse_instance_file(instance_path)
        plot_instance_map(instance, Path("outputs") / f"{instance.name}_map.png")
    print(json.dumps(result_to_dict(result), indent=2))


if __name__ == "__main__":
    main()
