"""Run with `python -m pytest` or, without pytest, `python tests/test_core.py`."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from causach import Settings, build_problem, evaluate, generate_district, greedy_nearest, no_coordination, solve
from causach.data import District, Problem, validate_inputs
from causach.export import class_allocation, split_largest_remainder, transfer_table
from causach.model import check_plan

SETTINGS = Settings()


def _toy_problem() -> Problem:
    """School 0 has 5 spare copies and needs none; school 1 lacks 3 (no device) + 4 (device)."""
    return Problem(
        schools=["A", "B"],
        titles=["Toán 6"],
        supply=np.array([[5], [0]]),
        need_c=np.array([[0], [3]]),
        need_a=np.array([[0], [4]]),
        dist=np.array([[0.0, 2.0], [2.0, 0.0]]),
    )


def test_toy_case_matches_hand_calculation():
    # Sending 5 copies covers 3 no-device + 2 device pairs: 3*5 + 2*0.5 - (3 + 0.5*2) = 12 > 0.
    plan = solve(_toy_problem(), SETTINGS)
    assert plan.covered_c[1, 0] == 3
    assert plan.covered_a[1, 0] == 2
    assert plan.trips == {(0, 1): 1}


def test_toy_case_skips_a_trip_that_is_not_worth_it():
    # One device student 2 km away: 0.5 value < 4.0 trip cost, so nothing moves.
    problem = _toy_problem()
    problem.need_c[1, 0] = 0
    problem.need_a[1, 0] = 1
    plan = solve(problem, SETTINGS)
    assert plan.trips == {}
    assert plan.covered_a.sum() == 0


def test_every_method_returns_a_valid_plan():
    for seed in range(3):
        problem = build_problem(generate_district(seed))
        for plan in (
            no_coordination(problem),
            greedy_nearest(problem, SETTINGS, seed=seed, c_first=False),
            greedy_nearest(problem, SETTINGS, seed=seed, c_first=True),
            solve(problem, SETTINGS),
        ):
            check_plan(problem, plan, SETTINGS)


def test_optimizer_is_at_least_as_good_as_greedy():
    # Any greedy plan is feasible for the integer program, so the optimum
    # cannot score lower (up to the allowed relative gap).
    for seed in range(3):
        problem = build_problem(generate_district(seed))
        best = evaluate(problem, solve(problem, SETTINGS, gap=0.005), SETTINGS)["objective"]
        for c_first in (False, True):
            greedy = evaluate(problem, greedy_nearest(problem, SETTINGS, seed=seed, c_first=c_first), SETTINGS)["objective"]
            assert best >= greedy * (1 - 0.005) - 1e-6


def test_generated_sheet_is_consistent():
    district = generate_district(1)
    validate_inputs(district.schools, district.sheet)
    assert (district.sheet["ghi_chu"] == "dữ liệu mô phỏng").all()


def test_validation_rejects_impossible_counts():
    district = generate_district(0)
    sheet = district.sheet.copy()
    sheet.loc[0, "so_khong_thiet_bi"] = sheet.loc[0, "so_thieu_sach"] + 1
    try:
        validate_inputs(district.schools, sheet)
    except ValueError:
        return
    raise AssertionError("expected a ValueError")


def test_exports_add_up():
    district = generate_district(2)
    problem = build_problem(district)
    plan = solve(problem, SETTINGS)
    by_class = class_allocation(district, problem, plan)
    assert by_class["nhan_cho_em_khong_thiet_bi"].sum() == plan.covered_c.sum()
    assert by_class["nhan_cho_em_co_thiet_bi"].sum() == plan.covered_a.sum()
    assert (by_class["luong_c_con_lai"] >= 0).all()
    moved = transfer_table(problem, plan)["so_cuon"].sum()
    assert moved == sum(c for (s, d, _), c in plan.flows.items() if s != d)


def test_split_largest_remainder():
    out = split_largest_remainder(5, [1, 2, 3])
    assert out.sum() == 5 and (out <= np.array([1, 2, 3])).all()
    assert split_largest_remainder(0, [4, 4]).sum() == 0


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    for name, fn in tests:
        fn()
        print(f"ok  {name}")
    print(f"{len(tests)} tests passed")
