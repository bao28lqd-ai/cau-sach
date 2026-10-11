"""Integer program for allocating spare textbooks across schools.

Variables
    x[e, t]  copies of title t moved along edge e = (sender s, receiver d);
             s == d means the school uses its own spare copies
    yc[d, t] no-device pairs at school d covered for title t
    ya[d, t] device pairs at school d covered for title t
    z[e]     number of transfer trips on edge e (s != d)

Maximize
    sum  weight_c * yc + weight_a * ya  -  sum  trip_cost(dist[e]) * z[e]

Subject to
    sum_{e out of s} x[e, t] <= supply[s, t]          (cannot give what you do not have)
    yc[d, t] + ya[d, t] <= sum_{e into d} x[e, t]     (coverage needs a physical copy)
    sum_t x[e, t] <= trip_capacity * z[e]             (copies travel on trips)
    x[e, t] <= U[e, t] * z[e]                         (same idea per title; tightens the relaxation)
    0 <= yc <= need_c,  0 <= ya <= need_a,  all variables integer

Solved with HiGHS through scipy.optimize.milp.
"""
from __future__ import annotations

import math
import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from .data import Problem
from .model import Plan, Settings, allowed_edges

# Tiny cost per copy-km: among equally good plans, prefer nearer senders.
TIE_BREAK_PER_KM = 1e-4


def solve(problem: Problem, settings: Settings = Settings(), time_limit: float = 60.0,
          gap: float = 0.005) -> Plan:
    """Return a plan proven to be within `gap` (relative) of the best possible
    objective, or the best plan found when `time_limit` seconds run out."""
    started = time.perf_counter()
    n_schools, n_titles = problem.shape
    edges = allowed_edges(problem, settings)
    remote = [e for e, (s, d) in enumerate(edges) if s != d]

    # ---- variable layout --------------------------------------------------
    n_x = len(edges) * n_titles
    yc0 = n_x
    ya0 = yc0 + n_schools * n_titles
    z0 = ya0 + n_schools * n_titles
    z_index = {e: z0 + k for k, e in enumerate(remote)}
    n_vars = z0 + len(remote)

    def xi(e: int, t: int) -> int:
        return e * n_titles + t

    def yci(d: int, t: int) -> int:
        return yc0 + d * n_titles + t

    def yai(d: int, t: int) -> int:
        return ya0 + d * n_titles + t

    cost = np.zeros(n_vars)
    upper = np.zeros(n_vars)

    for e, (s, d) in enumerate(edges):
        for t in range(n_titles):
            upper[xi(e, t)] = min(problem.supply[s, t], problem.need_c[d, t] + problem.need_a[d, t])
            cost[xi(e, t)] = TIE_BREAK_PER_KM * problem.dist[s, d]
    for d in range(n_schools):
        for t in range(n_titles):
            cost[yci(d, t)] = -settings.weight_c
            upper[yci(d, t)] = problem.need_c[d, t]
            cost[yai(d, t)] = -settings.weight_a
            upper[yai(d, t)] = problem.need_a[d, t]
    for e in remote:
        s, d = edges[e]
        cost[z_index[e]] = settings.trip_cost(problem.dist[s, d])
        movable = sum(upper[xi(e, t)] for t in range(n_titles))
        upper[z_index[e]] = math.ceil(movable / settings.trip_capacity)

    # ---- constraints ------------------------------------------------------
    rows, cols, vals, rhs = [], [], [], []
    r = 0

    out_edges = {s: [] for s in range(n_schools)}
    in_edges = {d: [] for d in range(n_schools)}
    for e, (s, d) in enumerate(edges):
        out_edges[s].append(e)
        in_edges[d].append(e)

    for s in range(n_schools):                      # supply
        for t in range(n_titles):
            for e in out_edges[s]:
                rows.append(r); cols.append(xi(e, t)); vals.append(1.0)
            rhs.append(problem.supply[s, t]); r += 1

    for d in range(n_schools):                      # coverage needs copies
        for t in range(n_titles):
            rows += [r, r]; cols += [yci(d, t), yai(d, t)]; vals += [1.0, 1.0]
            for e in in_edges[d]:
                rows.append(r); cols.append(xi(e, t)); vals.append(-1.0)
            rhs.append(0.0); r += 1

    for e in remote:                                # trip capacity
        for t in range(n_titles):
            rows.append(r); cols.append(xi(e, t)); vals.append(1.0)
        rows.append(r); cols.append(z_index[e]); vals.append(-float(settings.trip_capacity))
        rhs.append(0.0); r += 1

    # No copies move on an edge without a trip: x[e, t] <= U[e, t] * z[e].
    # Implied by the capacity rows for integer z, but stating it per title
    # tightens the LP relaxation a lot and makes HiGHS much faster.
    for e in remote:
        for t in range(n_titles):
            if upper[xi(e, t)] > 0:
                rows += [r, r]; cols += [xi(e, t), z_index[e]]; vals += [1.0, -float(upper[xi(e, t)])]
                rhs.append(0.0); r += 1

    a_matrix = coo_matrix((vals, (rows, cols)), shape=(r, n_vars)).tocsr()
    result = milp(
        c=cost,
        constraints=LinearConstraint(a_matrix, -np.inf, np.asarray(rhs, dtype=float)),
        integrality=np.ones(n_vars),
        bounds=Bounds(np.zeros(n_vars), upper),
        options={"time_limit": time_limit, "mip_rel_gap": gap, "disp": False},
    )
    if result.x is None:
        raise RuntimeError(f"solver found no feasible plan: {result.message}")

    sol = np.rint(result.x).astype(int)
    flows = {}
    for e, (s, d) in enumerate(edges):
        for t in range(n_titles):
            if sol[xi(e, t)] > 0:
                flows[(s, d, t)] = int(sol[xi(e, t)])
    trips = {edges[e]: int(sol[z_index[e]]) for e in remote if sol[z_index[e]] > 0}
    covered_c = sol[yc0:ya0].reshape(n_schools, n_titles)
    covered_a = sol[ya0:z0].reshape(n_schools, n_titles)

    return Plan(
        method="Tối ưu (MILP)",
        covered_c=covered_c.copy(),
        covered_a=covered_a.copy(),
        flows=flows,
        trips=trips,
        runtime_s=time.perf_counter() - started,
        status="optimal" if result.status == 0 else f"stopped: {result.message}",
        extra={"mip_gap": getattr(result, "mip_gap", None), "n_vars": n_vars, "n_constraints": r},
    )
