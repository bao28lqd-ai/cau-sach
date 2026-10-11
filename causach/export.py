"""Turn a plan into tables a coordinator can act on."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import District, Problem
from .model import Plan


def transfer_table(problem: Problem, plan: Plan) -> pd.DataFrame:
    """One row per (from school, to school, title) with copies to carry."""
    rows = [
        {
            "tu_truong": problem.schools[s],
            "den_truong": problem.schools[d],
            "dau_sach": problem.titles[t],
            "so_cuon": copies,
            "km": round(float(problem.dist[s, d]), 1),
        }
        for (s, d, t), copies in plan.flows.items()
        if s != d and copies > 0
    ]
    columns = ["tu_truong", "den_truong", "dau_sach", "so_cuon", "km"]
    return pd.DataFrame(rows, columns=columns).sort_values(["tu_truong", "den_truong", "dau_sach"], ignore_index=True)


def class_allocation(district: District, problem: Problem, plan: Plan) -> pd.DataFrame:
    """Split each school's covered pairs back over its classes.

    Copies covering no-device students go to classes in proportion to their
    no-device counts; the rest go in proportion to students who have a device.
    """
    s_index = {name: i for i, name in enumerate(problem.schools)}
    t_index = {name: j for j, name in enumerate(problem.titles)}
    sheet = district.sheet.copy()
    sheet["nhan_cho_em_khong_thiet_bi"] = 0
    sheet["nhan_cho_em_co_thiet_bi"] = 0

    for (school, title), group in sheet.groupby(["truong", "dau_sach"]):
        i, j = s_index[school], t_index[title]
        no_device = group["so_khong_thiet_bi"].to_numpy()
        with_device = (group["so_thieu_sach"] - group["so_khong_thiet_bi"]).to_numpy()
        sheet.loc[group.index, "nhan_cho_em_khong_thiet_bi"] = split_largest_remainder(int(plan.covered_c[i, j]), no_device)
        sheet.loc[group.index, "nhan_cho_em_co_thiet_bi"] = split_largest_remainder(int(plan.covered_a[i, j]), with_device)

    sheet["luong_c_con_lai"] = sheet["so_khong_thiet_bi"] - sheet["nhan_cho_em_khong_thiet_bi"]
    keep = ["truong", "lop", "dau_sach", "so_thieu_sach", "so_khong_thiet_bi",
            "nhan_cho_em_khong_thiet_bi", "nhan_cho_em_co_thiet_bi", "luong_c_con_lai"]
    return sheet.loc[sheet["so_thieu_sach"] > 0, keep].reset_index(drop=True)


def split_largest_remainder(total: int, weights) -> np.ndarray:
    """Split an integer total in proportion to integer weights, never exceeding a weight."""
    weights = np.asarray(weights, dtype=float)
    out = np.zeros(len(weights), dtype=int)
    if total <= 0 or weights.sum() == 0:
        return out
    if total > weights.sum():
        raise ValueError("total exceeds the sum of weights")
    raw = total * weights / weights.sum()
    out = np.floor(raw).astype(int)
    leftover = total - int(out.sum())
    order = np.argsort(-(raw - out), kind="stable")
    out[order[:leftover]] += 1
    return out
