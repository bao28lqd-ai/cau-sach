"""Baselines the optimizer is compared against.

no_coordination
    Status quo. Each school hands its own spare copies to whoever is missing
    the book, without knowing who has a device. No transfers.

greedy_nearest
    A careful human coordinator who handles requests in the order schools
    report them and always takes copies from the nearest school that still
    has spares. Two variants differ only in priority order (see below). Both
    already know which students have devices and how far apart schools are.
"""
from __future__ import annotations

import math
import time
from collections import defaultdict

import numpy as np

from .data import Problem
from .model import Plan, Settings, allowed_edges


def no_coordination(problem: Problem) -> Plan:
    started = time.perf_counter()
    n_schools, n_titles = problem.shape
    covered_c = np.zeros((n_schools, n_titles), dtype=int)
    covered_a = np.zeros((n_schools, n_titles), dtype=int)
    flows = {}
    for s in range(n_schools):
        for t in range(n_titles):
            c, a = int(problem.need_c[s, t]), int(problem.need_a[s, t])
            give = min(int(problem.supply[s, t]), c + a)
            if give == 0:
                continue
            # Device-blind handout: copies split in proportion to who is missing the book.
            gc = min(c, round(give * c / (c + a)))
            ga = min(a, give - gc)
            gc = min(c, give - ga)
            covered_c[s, t], covered_a[s, t] = gc, ga
            flows[(s, s, t)] = gc + ga
    return Plan("Không điều phối", covered_c, covered_a, flows, {},
                runtime_s=time.perf_counter() - started)


GREEDY_SCHOOL_FIRST = "Tham lam (trường tự lo trước)"
GREEDY_C_FIRST = "Tham lam (ưu tiên Luồng C)"


def greedy_nearest(problem: Problem, settings: Settings = Settings(), seed: int = 0,
                   c_first: bool = True) -> Plan:
    """Nearest-school greedy coordinator.

    c_first=False  each school serves all its own students first and only
                   then releases leftovers to other schools.
    c_first=True   no-device students across the whole cluster are served
                   before any student who has a device. This is the stronger
                   baseline: it already applies the Cầu Sách priority rule.
    """
    started = time.perf_counter()
    n_schools, n_titles = problem.shape
    rng = np.random.default_rng(seed)

    left = problem.supply.astype(int).copy()
    remaining = {"c": problem.need_c.astype(int).copy(), "a": problem.need_a.astype(int).copy()}
    covered = {"c": np.zeros((n_schools, n_titles), dtype=int), "a": np.zeros((n_schools, n_titles), dtype=int)}
    flows: dict[tuple[int, int, int], int] = defaultdict(int)

    senders = defaultdict(list)
    for s, d in allowed_edges(problem, settings):     # already nearest-first per receiver
        if s != d:
            senders[d].append(s)
    order = rng.permutation(n_schools)               # order in which schools report

    def serve_locally(tier: str) -> None:
        take = np.minimum(left, remaining[tier])
        left[...] -= take
        remaining[tier] -= take
        covered[tier] += take
        for s, t in zip(*np.nonzero(take)):
            flows[(int(s), int(s), int(t))] += int(take[s, t])

    def serve_remotely(tier: str) -> None:
        for d in order:
            for t in range(n_titles):
                for s in senders[d]:
                    want = remaining[tier][d, t]
                    if want == 0:
                        break
                    take = min(int(left[s, t]), int(want))
                    if take:
                        left[s, t] -= take
                        remaining[tier][d, t] -= take
                        covered[tier][d, t] += take
                        flows[(s, int(d), t)] += take

    if c_first:
        steps = [(serve_locally, "c"), (serve_remotely, "c"), (serve_locally, "a"), (serve_remotely, "a")]
    else:
        steps = [(serve_locally, "c"), (serve_locally, "a"), (serve_remotely, "c"), (serve_remotely, "a")]
    for step, tier in steps:
        step(tier)

    per_edge = defaultdict(int)
    for (s, d, _), copies in flows.items():
        if s != d:
            per_edge[(s, d)] += copies
    trips = {edge: math.ceil(copies / settings.trip_capacity) for edge, copies in per_edge.items()}

    return Plan(GREEDY_C_FIRST if c_first else GREEDY_SCHOOL_FIRST, covered["c"], covered["a"],
                dict(flows), trips, runtime_s=time.perf_counter() - started)
