"""Tracking-sheet schema, problem data and a synthetic district generator.

The optimizer reads the same tracking sheet that schools already fill in
(Phụ lục B of the Cầu Sách document) plus a small table of school locations.
Nothing new is asked of teachers.

Every number produced by `generate_district` is SIMULATED. The generator's
parameters are assumptions chosen to create a realistic *shape* of shortage
(some schools short, others with spare copies), not real statistics.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# Columns of the shared tracking sheet (Phụ lục B).
SHEET_COLUMNS = [
    "truong",             # school
    "lop",                # class
    "dau_sach",           # textbook title
    "si_so",              # class size
    "so_thieu_sach",      # students without this book
    "so_khong_thiet_bi",  # of those, students with no device at home
    "kenh_dang_dung",     # channels in use (free text)
    "sach_thua",          # spare copies this row can give away
    "ghi_chu",            # notes, never student names
]
SCHOOL_COLUMNS = ["truong", "x_km", "y_km"]

SUBJECTS = (
    "Toán", "Ngữ văn", "Tiếng Anh", "KHTN",
    "Lịch sử và Địa lí", "GDCD", "Tin học", "Công nghệ",
)
GRADES = (6, 7, 8, 9)
# Titles revised under Thông tư 17/2025/TT-BGDĐT (lower-secondary part).
# Old donated copies of these need the e-book alongside them.
REVISED_SUBJECTS = frozenset({"Lịch sử và Địa lí"})

# Straight-line distance is multiplied by this to approximate road distance.
ROAD_FACTOR = 1.3


def title_name(subject: str, grade: int) -> str:
    return f"{subject} {grade}"


@dataclass
class District:
    """Raw inputs: school locations and the tracking sheet."""

    schools: pd.DataFrame
    sheet: pd.DataFrame

    def to_csv(self, folder: str | Path) -> None:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        self.schools.to_csv(folder / "schools.csv", index=False)
        self.sheet.to_csv(folder / "sheet.csv", index=False)

    @classmethod
    def from_csv(cls, schools_path: str | Path, sheet_path: str | Path) -> "District":
        schools = pd.read_csv(schools_path)
        sheet = pd.read_csv(sheet_path).fillna({"kenh_dang_dung": "", "ghi_chu": ""})
        validate_inputs(schools, sheet)
        return cls(schools=schools, sheet=sheet)


def validate_inputs(schools: pd.DataFrame, sheet: pd.DataFrame) -> None:
    """Reject sheets that would make the plan meaningless."""
    missing = [c for c in SHEET_COLUMNS if c not in sheet.columns]
    if missing:
        raise ValueError(f"sheet is missing columns: {missing}")
    missing = [c for c in SCHOOL_COLUMNS if c not in schools.columns]
    if missing:
        raise ValueError(f"schools table is missing columns: {missing}")
    counts = ["si_so", "so_thieu_sach", "so_khong_thiet_bi", "sach_thua"]
    if (sheet[counts] < 0).any().any():
        raise ValueError("counts must be non-negative")
    if (sheet["so_thieu_sach"] > sheet["si_so"]).any():
        raise ValueError("so_thieu_sach cannot exceed si_so")
    if (sheet["so_khong_thiet_bi"] > sheet["so_thieu_sach"]).any():
        raise ValueError("so_khong_thiet_bi cannot exceed so_thieu_sach")
    unknown = set(sheet["truong"]) - set(schools["truong"])
    if unknown:
        raise ValueError(f"schools in sheet but not in schools table: {sorted(unknown)}")


@dataclass
class Problem:
    """Aggregated optimization input, indexed [school, title]."""

    schools: list[str]
    titles: list[str]
    supply: np.ndarray   # spare copies held by each school
    need_c: np.ndarray   # (student, subject) pairs without the book and without a device
    need_a: np.ndarray   # pairs without the book but with a device (e-book available)
    dist: np.ndarray     # road-distance estimate between schools, km

    @property
    def shape(self) -> tuple[int, int]:
        return self.supply.shape


def build_problem(district: District) -> Problem:
    sheet = district.sheet
    schools = list(district.schools["truong"])
    titles = sorted(sheet["dau_sach"].unique(), key=_title_sort_key)
    s_index = {name: i for i, name in enumerate(schools)}
    t_index = {name: j for j, name in enumerate(titles)}

    shape = (len(schools), len(titles))
    supply = np.zeros(shape, dtype=int)
    lack = np.zeros(shape, dtype=int)
    need_c = np.zeros(shape, dtype=int)
    grouped = sheet.groupby(["truong", "dau_sach"])[
        ["so_thieu_sach", "so_khong_thiet_bi", "sach_thua"]
    ].sum()
    for (school, title), row in grouped.iterrows():
        i, j = s_index[school], t_index[title]
        supply[i, j] = row["sach_thua"]
        lack[i, j] = row["so_thieu_sach"]
        need_c[i, j] = row["so_khong_thiet_bi"]

    coords = district.schools.set_index("truong").loc[schools, ["x_km", "y_km"]].to_numpy(float)
    diff = coords[:, None, :] - coords[None, :, :]
    dist = np.sqrt((diff ** 2).sum(axis=-1)) * ROAD_FACTOR

    return Problem(schools, titles, supply, need_c, lack - need_c, dist)


def _title_sort_key(title: str) -> tuple[int, str]:
    subject, _, grade = title.rpartition(" ")
    return (int(grade), subject) if grade.isdigit() else (0, title)


# ---------------------------------------------------------------------------
# Synthetic data
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class GeneratorConfig:
    """Assumptions behind the simulated district. All are tunable."""

    n_schools: int = 8
    area_km: float = 12.0
    classes_per_grade: tuple[int, int] = (3, 7)
    class_size: tuple[int, int] = (34, 45)
    # Share of schools that used a different textbook set before 2026-2027.
    switched_share: float = 0.5
    # Share of students missing a given book, drawn per school.
    shortage_switched: tuple[float, float] = (0.20, 0.45)
    shortage_kntt: tuple[float, float] = (0.02, 0.10)
    # Share of students with a usable device at home, drawn per school.
    device_rate: tuple[float, float] = (0.55, 0.90)
    # Old copies donated per enrolled student, per title.
    donation_kntt: tuple[float, float] = (0.08, 0.20)
    donation_switched: tuple[float, float] = (0.00, 0.03)
    # Spare library copies per title.
    library_copies: tuple[int, int] = (0, 6)
    # Old copies of revised titles are excluded unless this is True.
    count_revised_donations: bool = False


def generate_district(seed: int = 0, config: GeneratorConfig = GeneratorConfig()) -> District:
    rng = np.random.default_rng(seed)
    school_rows, sheet_rows = [], []

    for i in range(config.n_schools):
        name = f"THCS {_school_label(i)}"
        switched = rng.random() < config.switched_share
        shortage = rng.uniform(*(config.shortage_switched if switched else config.shortage_kntt))
        device = rng.uniform(*config.device_rate)
        donation = rng.uniform(*(config.donation_switched if switched else config.donation_kntt))
        x, y = rng.uniform(0, config.area_km, size=2)
        school_rows.append({"truong": name, "x_km": round(x, 2), "y_km": round(y, 2)})

        for grade in GRADES:
            n_classes = int(rng.integers(config.classes_per_grade[0], config.classes_per_grade[1], endpoint=True))
            sizes = rng.integers(config.class_size[0], config.class_size[1], size=n_classes, endpoint=True)
            enrolled = int(sizes.sum())
            for subject in SUBJECTS:
                p_lack = float(np.clip(shortage * rng.lognormal(0.0, 0.35), 0.0, 0.95))
                spare = int(rng.integers(config.library_copies[0], config.library_copies[1], endpoint=True))
                if config.count_revised_donations or subject not in REVISED_SUBJECTS:
                    spare += int(rng.poisson(donation * enrolled))
                spare_by_class = rng.multinomial(spare, np.full(n_classes, 1.0 / n_classes))
                for k in range(n_classes):
                    lack = int(rng.binomial(sizes[k], p_lack))
                    no_device = int(rng.binomial(lack, 1.0 - device))
                    sheet_rows.append({
                        "truong": name,
                        "lop": f"{grade}A{k + 1}",
                        "dau_sach": title_name(subject, grade),
                        "si_so": int(sizes[k]),
                        "so_thieu_sach": lack,
                        "so_khong_thiet_bi": no_device,
                        "kenh_dang_dung": "",
                        "sach_thua": int(spare_by_class[k]),
                        "ghi_chu": "dữ liệu mô phỏng",
                    })

    return District(pd.DataFrame(school_rows, columns=SCHOOL_COLUMNS),
                    pd.DataFrame(sheet_rows, columns=SHEET_COLUMNS))


def _school_label(i: int) -> str:
    letters = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        letters = chr(ord("A") + r) + letters
    return letters
