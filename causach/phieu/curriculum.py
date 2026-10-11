"""Curriculum data and the JSON schemas used for structured model output."""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "data"

ANSWER_KINDS = ["gia_tri", "so_nguyen", "phan_so_toi_gian", "mot_luy_thua", "phan_tich_nguyen_to"]


@dataclass(frozen=True)
class Requirement:
    code: str
    text: str


@dataclass(frozen=True)
class Lesson:
    code: str
    topic: str
    title: str
    requirements: tuple[Requirement, ...]

    @property
    def requirement_codes(self) -> set[str]:
        return {r.code for r in self.requirements}


@lru_cache(maxsize=None)
def load_lessons(name: str = "toan6") -> dict[str, Lesson]:
    raw = json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
    lessons = {}
    for item in raw["bai"]:
        reqs = tuple(Requirement(r["ma"], r["noi_dung"]) for r in item["yccd"])
        lessons[item["ma"]] = Lesson(item["ma"], item["chu_de"], item["ten"], reqs)
    return lessons


def get_lesson(code: str) -> Lesson:
    lessons = load_lessons()
    if code not in lessons:
        raise KeyError(f"unknown lesson {code}; available: {', '.join(lessons)}")
    return lessons[code]


# ---------------------------------------------------------------------------
# Strict JSON schemas (every property required, no extra properties).
# ---------------------------------------------------------------------------
_EXERCISE = {
    "type": "object",
    "additionalProperties": False,
    "required": ["id", "yccd", "de_bai", "loi_giai", "kieu", "bieu_thuc", "dap_an"],
    "properties": {
        "id": {"type": "string"},
        "yccd": {"type": "array", "items": {"type": "string"}},
        "de_bai": {"type": "string"},
        "loi_giai": {"type": "string"},
        "kieu": {"type": "string", "enum": ANSWER_KINDS},
        "bieu_thuc": {"type": "string"},
        "dap_an": {"type": "string"},
    },
}

WORKSHEET_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["tieu_de", "muc_tieu", "kien_thuc_cot_loi", "vi_du", "bai_tap"],
    "properties": {
        "tieu_de": {"type": "string"},
        "muc_tieu": {"type": "array", "items": {"type": "string"}},
        "kien_thuc_cot_loi": {"type": "array", "items": {"type": "string"}},
        "vi_du": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["de_bai", "loi_giai"],
                "properties": {"de_bai": {"type": "string"}, "loi_giai": {"type": "string"}},
            },
        },
        "bai_tap": {"type": "array", "items": _EXERCISE},
    },
}

REPAIR_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["bai_tap"],
    "properties": {"bai_tap": {"type": "array", "items": _EXERCISE}},
}

FORMALIZE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["ket_qua"],
    "properties": {
        "ket_qua": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "bieu_thuc"],
                "properties": {"id": {"type": "string"}, "bieu_thuc": {"type": "string"}},
            },
        }
    },
}


def _with_requirement_codes(schema: dict, lesson: Lesson) -> dict:
    """Restrict the yccd field to this lesson's real codes.

    With strict Structured Outputs the model cannot return anything outside the
    enum. Added after 4 of 20 evaluation worksheets came back with invented
    codes such as "cộng_phân_số" instead of "T6-09.1".
    """
    schema = copy.deepcopy(schema)
    exercise = schema["properties"]["bai_tap"]["items"]
    exercise["properties"]["yccd"] = {
        "type": "array",
        "items": {"type": "string", "enum": sorted(lesson.requirement_codes)},
    }
    return schema


def worksheet_schema(lesson: Lesson) -> dict:
    return _with_requirement_codes(WORKSHEET_SCHEMA, lesson)


def repair_schema(lesson: Lesson) -> dict:
    return _with_requirement_codes(REPAIR_SCHEMA, lesson)
