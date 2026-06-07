# Optimization Project

Course project implementation based on `Paper-14.pdf` for the EVRPTW-FC problem.

## What is in this repo

- `docs/`
  - assignment materials
  - problem specification
  - report foundation
  - Person 3 runbook
  - Person 4 UI handoff
- `src/`
  - benchmark downloader
  - EVRPTW heuristic solver
- `data/instances/`
  - Schneider benchmark instances used by the solver
- `outputs/`
  - benchmark CSV results
  - JSON solver outputs
  - benchmark map artifact

## Current status

Implemented and verified:

- benchmark parsing for Schneider EVRPTW instance files
- feasible heuristic solver with charging stops
- structured JSON output for the UI
- benchmark result export to CSV
- report-ready project docs

## Quick start

Run the solver on one instance:

```powershell
python src/evrptw_solver.py data/instances/c101_21.txt
```

Run the current benchmark set:

```powershell
python src/evrptw_solver.py --benchmark data/instances/c101C5.txt data/instances/c101_21.txt data/instances/r101_21.txt data/instances/rc103_21.txt
```

Download the benchmark files again if needed:

```powershell
python src/download_benchmarks.py
```

## Important note

This implementation is a practical course-project heuristic for the same EVRPTW-FC problem studied in Paper 14. It is not a claim of full reproduction of the paper's original ALNS + exact optimization method.
