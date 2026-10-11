"""Metrics used to compare allocation plans."""
from __future__ import annotations

from .data import Problem
from .model import Plan, Settings, check_plan


def evaluate(problem: Problem, plan: Plan, settings: Settings = Settings()) -> dict:
    """Score a plan. Every plan is validated first, so a broken plan fails loudly."""
    check_plan(problem, plan, settings)

    need_c = int(problem.need_c.sum())
    need_a = int(problem.need_a.sum())
    covered_c = int(plan.covered_c.sum())
    covered_a = int(plan.covered_a.sum())
    trips = sum(plan.trips.values())
    km = sum(n * float(problem.dist[s, d]) for (s, d), n in plan.trips.items())
    trip_cost = sum(n * settings.trip_cost(float(problem.dist[s, d])) for (s, d), n in plan.trips.items())
    moved = sum(c for (s, d, _), c in plan.flows.items() if s != d)

    return {
        "method": plan.method,
        "need_c": need_c,                      # no-device pairs missing a book
        "covered_c": covered_c,
        "coverage_c": covered_c / need_c if need_c else 1.0,
        "luong_c_left": need_c - covered_c,    # still need a printed worksheet or a licensed temporary print
        "need_a": need_a,
        "covered_a": covered_a,
        "books_moved": moved,
        "trips": trips,
        "km": round(km, 2),
        "objective": settings.weight_c * covered_c + settings.weight_a * covered_a - trip_cost,
        "runtime_s": plan.runtime_s,
    }
