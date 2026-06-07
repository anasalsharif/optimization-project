# Person 4 Handoff: UI / Demo Work

## Your role

You are **not** building the optimization logic. Person 3 owns the solver.

Your job is to build the **demo shell** that presents solver inputs and outputs clearly for the report and presentation.

## What already exists / will exist

Person 1 and Person 3 are responsible for:

- problem understanding
- benchmark instance parsing
- solver logic
- route output generation
- result exports

You should assume the solver will expose one result object per run.

## What you need to build

Build a **simple local web UI** that can later read solver output and present it cleanly.

Minimum UI pages / sections:

1. **Header**
   - project title
   - short subtitle mentioning EVRPTW-FC and Paper 14

2. **Input panel**
   - instance selector
   - `Run Solver` button
   - optional charger-mode note or dropdown placeholder

3. **Summary cards**
   - feasibility
   - vehicles used
   - total distance
   - total energy / charging cost
   - runtime

4. **Routes table**
   - route id
   - ordered stop list
   - charging stops
   - route distance
   - route demand

5. **Optional visual panel**
   - placeholder for a plotted map image or route visualization

6. **Comparison section**
   - our solver result
   - paper reference value when available
   - short note on whether our approach is simplified

## Result contract you should expect

The solver result will be JSON-serializable and should be treated as the input contract for the UI.

Expected top-level fields:

```json
{
  "instance_name": "c101_21",
  "feasible": true,
  "vehicles_used": 12,
  "total_distance": 1043.38,
  "total_energy_cost": 1043.38,
  "total_charging_time": 165.96,
  "runtime_seconds": 2.14,
  "routes": []
}
```

Expected per-route shape:

```json
{
  "route_id": 1,
  "distance": 120.5,
  "demand_served": 80.0,
  "stops": [
    {
      "node_id": "D0",
      "node_type": "depot",
      "arrival_time": 0.0,
      "departure_time": 0.0,
      "battery_after": 79.69
    },
    {
      "node_id": "S3",
      "node_type": "station",
      "arrival_time": 100.0,
      "departure_time": 115.0,
      "battery_after": 79.69,
      "charge_added": 15.0,
      "charger_mode": "fast"
    },
    {
      "node_id": "C21",
      "node_type": "customer",
      "arrival_time": 180.0,
      "departure_time": 270.0,
      "battery_after": 40.0
    }
  ]
}
```

## What you can do right now without waiting

Build the UI first with **mock data**.

Use:

- one fake instance selector
- one fake solved example
- static result cards
- static route table
- empty map placeholder

Then replace the mock data with real JSON once Person 3 hands it over.

## Design goal

Keep it simple and presentation-friendly:

- no fancy authentication
- no backend complexity
- no editing of optimization logic
- just a clean local demo that makes the solver understandable in 30 seconds

## Files in `docs/` you should read

- `docs/problem_spec.md`
- `docs/report_foundation.md`
- `docs/industrial.txt`
- `docs/Paper-14.pdf`
- `docs/TEAM29.docx`

## Important wording rule

Do **not** present the UI as if it reproduces the paper's full ALNS+CPLEX matheuristic unless Person 3 explicitly confirms that.

Safe wording:

> This interface demonstrates our software implementation for the EVRPTW-FC problem inspired by Paper 14.
