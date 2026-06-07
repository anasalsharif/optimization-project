# Report Foundation for Person 1

## Introduction draft

The transition toward electric mobility has created new operational challenges for logistics and routing systems. Unlike conventional vehicle routing, electric vehicle routing must account for limited battery capacity, charging opportunities, and charging duration. When customer time windows are also present, route planning becomes significantly more constrained. Paper 14 addresses this setting through the Electric Vehicle Routing Problem with Time Windows and Fast Chargers (EVRPTW-FC), where charging may occur through multiple charger types with different speed and cost tradeoffs.

This project takes Paper 14 as its source problem and benchmark reference. Rather than reproducing the paper's exact research implementation, we develop a software application for the same EVRPTW-FC problem and evaluate it on Schneider-style benchmark instances with 21 charging stations. The goal is to provide a working computational prototype that respects the core routing, battery, charging, and time-window constraints while remaining understandable and demonstrable in a course project setting.

## Problem definition draft

The EVRPTW-FC consists of constructing delivery routes for a homogeneous fleet of electric vehicles departing from a depot and serving a set of customers. Each customer has a demand, a service time, and a time window defined by a ready time and due date. Vehicles are constrained by cargo capacity and battery capacity. Energy is consumed proportionally to traveled distance. Charging stations may be visited during the route to restore battery level, and in the fast-charger setting different charging modes may trade charging duration against charging cost.

The routing solution must satisfy the following conditions:

- each customer is visited exactly once
- total route demand cannot exceed vehicle load capacity
- battery level must remain nonnegative at all times
- customer service must begin no later than the due time
- if a vehicle arrives before the ready time, waiting is allowed
- vehicles begin and end at the depot

The paper treats fleet minimization as the primary objective and charging-related cost minimization as the secondary objective. Our implementation follows the same overall intention, while using a simpler route construction strategy.

## Methodology background draft

Paper 14 proposes a matheuristic solution approach for the EVRPTW-FC. For small benchmark instances, the authors formulate the problem as a mixed integer linear program and solve it using CPLEX. For larger instances, they develop a hybrid method combining Adaptive Large Neighborhood Search (ALNS) with an exact charging-optimization phase. The ALNS stage explores neighborhoods through destroy and repair operators, while the exact phase improves charging decisions for the customer sequence currently selected by the heuristic.

Because the full ALNS-plus-exact pipeline is substantial in both implementation effort and parameter tuning, this project focuses on a simpler yet operationally valid heuristic. The implemented solver preserves the essential decision structure of the problem: route construction under battery, capacity, and time-window constraints; charging-station insertion when battery limitations arise; and comparison across Schneider benchmark instances. This keeps the project aligned with the assigned article while remaining realistic for a student-built software prototype.

## Benchmark description draft

The implementation targets Schneider 2014 EVRPTW benchmark instances in the `_21` family, where the suffix indicates 21 charging stations. Representative cases from the clustered (`C`), random (`R`), and mixed (`RC`) families are used so that the solver can be tested under different spatial patterns. Each instance file contains node information for the depot, charging stations, and customers, followed by vehicle configuration values such as battery capacity, vehicle load capacity, fuel consumption rate, inverse refueling rate, and average velocity.

## Implementation assumptions draft

To keep the project executable end to end, the following assumptions are adopted:

- distance is Euclidean and travel time equals distance divided by average velocity
- energy consumption is proportional to traveled distance
- three charger modes are exposed in the solver: normal, fast, and super-fast
- partial recharge is allowed
- the implemented method is a constructive heuristic with lightweight improvement logic, not a full reproduction of the paper's ALNS matheuristic

## Limitation statement draft

The project is intentionally positioned as a practical software implementation for the same optimization problem studied in Paper 14, not as a line-by-line reproduction of the paper's full research algorithm. The original article combines ALNS with exact optimization support and extensive parameterized search behavior. Our software instead implements a simpler feasible heuristic that preserves the main EVRPTW-FC constraints and benchmark setting. This distinction is important for accurately describing the contribution and for avoiding unsupported claims about algorithmic equivalence.

## Findings template

Use the following structure after experiments are run:

1. State which Schneider `_21` instances were tested.
2. Report feasibility success or failure for each instance.
3. Report vehicles used, total distance, charging cost, and runtime.
4. Compare results against paper-reported values where directly available.
5. Explain where the simplified heuristic behaves worse or better.
