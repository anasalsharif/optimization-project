# Person 3 Runbook

## What Person 3 owns

Person 3 owns the solver side:

- benchmark instance acquisition
- parsing
- feasibility logic
- heuristic route construction
- benchmark execution
- machine-readable outputs for the UI and report

## Files to use

- `src/download_benchmarks.py`
- `src/evrptw_solver.py`
- `data/instances/`
- `outputs/`

## Benchmark files currently included

- `data/instances/c101C5.txt`
- `data/instances/c101_21.txt`
- `data/instances/r101_21.txt`
- `data/instances/rc103_21.txt`

## Commands

Download benchmark files:

```powershell
python src/download_benchmarks.py
```

Run one instance:

```powershell
python src/evrptw_solver.py data/instances/c101_21.txt
```

Run one instance and generate a benchmark map:

```powershell
python src/evrptw_solver.py data/instances/c101_21.txt --plot
```

Run the current benchmark set:

```powershell
python src/evrptw_solver.py --benchmark data/instances/c101C5.txt data/instances/c101_21.txt data/instances/r101_21.txt data/instances/rc103_21.txt
```

## Expected outputs

- `outputs/benchmark_results.csv`
- `outputs/c101C5.json`
- `outputs/c101_21.json`
- `outputs/r101_21.json`
- `outputs/rc103_21.json`
- `outputs/c101_21_map.svg`

## Current solver behavior

The solver is a **simplified feasible heuristic** for the EVRPTW-FC problem:

- greedy route construction
- charging-station insertion when required
- partial recharge support
- normal / fast / super-fast charging modes
- structured JSON output for UI use

It is intentionally **not** a full ALNS + CPLEX reproduction of Paper 14.

## What to mention in the presentation

- we solve the same benchmark problem family as the paper
- we preserve the key operational constraints
- we built a practical software solver, not a line-by-line copy of the paper's research algorithm
