"""Settings, plan structure and checks shared by every allocation method."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .data import Problem


@dataclass(frozen=True)
class Settings:
    """Policy and logistics parameters.

    The weights are policy choices, not technical ones: they say how much a
    printed book is worth to a student with no device (Luồng C) compared with
    a student who can already read the e-book, and how much one transfer trip
    costs, all in the same unit ("weighted student-subject pairs").
    """

    weight_c: float = 5.0        # value of covering a no-device pair
    weight_a: float = 0.5        # value of covering a pair that has a device
    trip_fixed: float = 3.0      # fixed cost of one transfer trip
    trip_per_km: float = 0.5     # extra cost per km of that trip
    trip_capacity: int = 400     # copies one trip can carry
    max_km: float = 15.0         # schools farther apart do not exchange books
    neighbors: int | None = 6    # each school receives from at most this many nearest schools

    def trip_cost(self, km: float) -> float:
        return self.trip_fixed + self.trip_per_km * km


@dataclass
class Plan:
    method: str
    covered_c: np.ndarray                      # [school, title]
    covered_a: np.ndarray                      # [school, title]
    flows: dict[tuple[int, int, int], int]     # (sender, receiver, title) -> copies; sender == receiver is local use
    trips: dict[tuple[int, int], int]          # (sender, receiver) -> number of trips, sender != receiver
    runtime_s: float = 0.0
    status: str = "ok"
    extra: dict = field(default_factory=dict)


def allowed_edges(problem: Problem, settings: Settings) -> list[tuple[int, int]]:
    """(sender, receiver) pairs that may move books, local use included.

    For each receiver, senders are sorted nearest first, so methods that
    walk this list visit the closest school first.
    """
    n = len(problem.schools)
    edges: list[tuple[int, int]] = []
    for d in range(n):
        order = np.argsort(problem.dist[:, d], kind="stable")
        senders = [int(s) for s in order if s != d and problem.dist[s, d] <= settings.max_km]
        if settings.neighbors is not None:
            senders = senders[: settings.neighbors]
        edges.append((d, d))
        edges.extend((s, d) for s in senders)
    return edges


def check_plan(problem: Problem, plan: Plan, settings: Settings) -> None:
    """Raise AssertionError if the plan breaks any physical or policy limit."""
    n_schools, n_titles = problem.shape
    allowed = set(allowed_edges(problem, settings))
    sent = np.zeros((n_schools, n_titles), dtype=int)
    received = np.zeros((n_schools, n_titles), dtype=int)
    per_edge: dict[tuple[int, int], int] = {}

    for (s, d, t), copies in plan.flows.items():
        assert copies >= 0, "negative flow"
        assert (s, d) in allowed, f"transfer {s}->{d} is not allowed"
        sent[s, t] += copies
        received[d, t] += copies
        if s != d:
            per_edge[(s, d)] = per_edge.get((s, d), 0) + copies

    assert (sent <= problem.supply).all(), "a school sends more copies than it has"
    assert (plan.covered_c >= 0).all() and (plan.covered_a >= 0).all(), "negative coverage"
    assert (plan.covered_c <= problem.need_c).all(), "covers more no-device pairs than exist"
    assert (plan.covered_a <= problem.need_a).all(), "covers more device pairs than exist"
    assert (plan.covered_c + plan.covered_a <= received).all(), "covers more pairs than copies received"
    for edge, copies in per_edge.items():
        trips = plan.trips.get(edge, 0)
        assert copies <= trips * settings.trip_capacity, f"edge {edge} carries {copies} copies on {trips} trips"
