# EVRPTW-FC Problem Specification for Paper 14

## What the paper is about

`Paper-14.pdf` studies the **Electric Vehicle Routing Problem with Time Windows and Fast Chargers (EVRPTW-FC)**.

The problem extends the classical vehicle routing problem by adding:

- electric vehicles with limited battery capacity
- customer time windows
- charging stations
- different charger types with different charging speeds and costs

The paper's full research method is a **matheuristic**:

- Adaptive Large Neighborhood Search (ALNS)
- periodic exact optimization for charging decisions
- benchmark evaluation against Schneider 2014 EVRPTW instances

Our course project does **not** need to reproduce that exact research implementation line by line. The course booklet explicitly asks for a **working software application** plus an **alternative or practical solution approach** for the same optimization problem.

## Problem definition

We are given:

- one depot
- a set of customers
- a set of charging stations
- vehicle battery capacity `Q`
- vehicle cargo capacity `C`
- consumption rate `r`
- average speed `v`
- customer coordinates, demand, ready time, due time, and service time

We must build routes for electric vehicles so that:

- every customer is served exactly once
- route demand does not exceed vehicle capacity
- vehicles never run out of battery
- customer service begins no later than the customer's due time
- vehicles may wait if they arrive before a customer's ready time
- vehicles may recharge at charging stations

## Objective

The paper uses a hierarchical objective:

1. minimize the number of vehicles
2. among solutions using the same number of vehicles, minimize charging-related cost / route cost

For this project implementation, we preserve the same decision intent:

1. reduce fleet size when possible
2. otherwise prefer cheaper feasible charging and shorter feasible routing choices

## Benchmark instances

The benchmark family used in the paper comes from the Schneider 2014 EVRPTW data set.

The important large-instance naming convention is:

- `c***_21.txt`
- `r***_21.txt`
- `rc***_21.txt`

The `_21` suffix means the instance includes **21 charging stations**, which is the family referenced in the paper and in `industrial.txt`.

Example instances for this project:

- `c101_21.txt`
- `r101_21.txt`
- `rc103_21.txt`

## Real instance format used in this project

The downloaded benchmark files use a tabular node list followed by configuration constants:

- `StringID`
- `Type` (`d`, `f`, `c`)
- `x`
- `y`
- `demand`
- `ReadyTime`
- `DueDate`
- `ServiceTime`

Then:

- `Q Vehicle fuel tank capacity /.../`
- `C Vehicle load capacity /.../`
- `r fuel consumption rate /.../`
- `g inverse refueling rate /.../`
- `v average Velocity /.../`

## What our implementation will do

Our implementation is a **practical heuristic solver** for the same EVRPTW-FC problem.

It will:

- parse Schneider-format instance files
- compute distances and travel times
- enforce capacity, battery, and time-window constraints
- construct feasible routes greedily
- insert charging stops when battery constraints require them
- support three charger modes inspired by the paper:
  - normal
  - fast
  - super-fast
- export route results in a stable format for the future UI

## What our implementation will not claim

We will **not** claim:

- exact reproduction of the paper's ALNS matheuristic
- exact reproduction of the CPLEX-based charging subproblem
- parity with the paper's research-grade benchmark results

Instead, the honest project wording is:

> The original paper uses an ALNS-based matheuristic with exact optimization support. In this project, we implement a simplified but fully executable heuristic solver for the same EVRPTW-FC benchmark setting as a practical decision-support prototype.

## Required report sections this spec supports

This document is the source for:

- introduction
- problem definition
- benchmark description
- methodology background
- implementation assumptions
- limitations statement
