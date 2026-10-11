"""Generate–verify–repair loop for Phiếu Cầu.

    draft  ->  verify  ->  (failures?)  ->  repair failed items  ->  verify  -> …

`max_rounds=0` is plain one-shot generation (still verified, so the two modes
can be compared on the same metrics). Each round's report is kept so the
evaluation can see where errors were caught and fixed.
"""
from __future__ import annotations

import copy
import re
import time
from dataclasses import dataclass, field

from .curriculum import FORMALIZE_SCHEMA, Lesson, repair_schema, worksheet_schema
from .llm import Model
from .prompts import FORMALIZE_SYSTEM, SYSTEM, draft_prompt, formalize_prompt, repair_prompt
from .verify import Report, verify


@dataclass
class GenerationResult:
    lesson: str
    model: str
    worksheet: dict
    reports: list[Report]                         # one per round, round 0 = first draft
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    log: list[str] = field(default_factory=list)
    readings: dict[str, str] = field(default_factory=dict)   # independent re-reading of each final problem
    reader_log: list[dict] = field(default_factory=list)      # raw answers of every reading call, for debugging

    @property
    def final(self) -> Report:
        return self.reports[-1]

    @property
    def rounds_used(self) -> int:
        return len(self.reports) - 1


class _Meter:
    def __init__(self, model: Model):
        self.model, self.calls, self.input_tokens, self.output_tokens = model, 0, 0, 0

    def __call__(self, system: str, user: str, schema: dict, name: str) -> dict:
        data, usage = self.model.complete_json(system, user, schema, name)
        self.calls += 1
        self.input_tokens += usage.get("input_tokens", 0)
        self.output_tokens += usage.get("output_tokens", 0)
        return data


def generate(lesson: Lesson, model: Model, max_rounds: int = 2, cross_check: bool = True,
             n_exercises: int = 6) -> GenerationResult:
    started = time.perf_counter()
    call = _Meter(model)
    log: list[str] = []

    worksheet = call(SYSTEM, draft_prompt(lesson, n_exercises), worksheet_schema(lesson), "phieu_cau")
    formal_cache: dict[str, tuple[str, str]] = {}   # id -> (problem text, independent expression)
    reports: list[Report] = []
    reader_log: list[dict] = []

    for round_no in range(max_rounds + 1):
        independent = _independent_expressions(worksheet, call, formal_cache, reader_log) if cross_check else None
        report = verify(worksheet, lesson, independent)
        reports.append(report)
        log.append(f"vòng {round_no}: {report.summary()}")
        if report.passed or round_no == max_rounds:
            break

        exercises = {ex["id"]: ex for ex in worksheet["bai_tap"]}
        # A missing reading is a failure of the reading call, not of the exercise:
        # do not ask the model to rewrite it; the next round reads it again.
        failures = [
            {**exercises[c.id], "loi": c.message}
            for c in report.items if not c.passed and c.status != "loi_doc_lai" and c.id in exercises
        ]
        # Ask for new exercises only for requirements no exercise targets at all;
        # requirements whose only exercise failed are handled by repairing it.
        targeted = {code for ex in worksheet["bai_tap"] for code in ex.get("yccd", [])}
        to_add = sorted(lesson.requirement_codes - targeted)
        if not failures and not to_add:
            if any(c.status == "loi_doc_lai" for c in report.items):
                continue   # only the reading step failed: read again next round, rewrite nothing
            break          # only structural problems the repair step cannot fix

        fixes = call(SYSTEM, repair_prompt(lesson, failures, to_add, _next_id(worksheet)), repair_schema(lesson), "sua_bai_tap")
        worksheet = _merge(worksheet, fixes.get("bai_tap", []))

    return GenerationResult(
        lesson=lesson.code, model=model.name, worksheet=worksheet, reports=reports,
        calls=call.calls, input_tokens=call.input_tokens, output_tokens=call.output_tokens,
        seconds=time.perf_counter() - started, log=log,
        readings={ex["id"]: formal_cache[ex["id"]][1] for ex in worksheet["bai_tap"]
                  if ex["id"] in formal_cache and formal_cache[ex["id"]][0] == ex["de_bai"]},
        reader_log=reader_log,
    )


def _independent_expressions(worksheet: dict, call: _Meter, cache: dict[str, tuple[str, str]],
                             reader_log: list[dict]) -> dict[str, str]:
    """Re-derive an expression from each problem text alone; reuse it while the text is unchanged.

    Problems the reading call does not answer are asked once more before
    giving up, so a single bad reading call does not fail a worksheet.
    """
    todo = [ex for ex in worksheet["bai_tap"] if cache.get(ex["id"], ("", ""))[0] != ex["de_bai"]]
    if todo:
        readings = read_problems(todo, call, reader_log)
        missing = [ex for ex in todo if ex["id"] not in readings]
        if missing:
            readings.update(read_problems(missing, call, reader_log))
        for ex in todo:
            if ex["id"] in readings:
                cache[ex["id"]] = (ex["de_bai"], readings[ex["id"]])
    return {ex["id"]: cache[ex["id"]][1] for ex in worksheet["bai_tap"]
            if ex["id"] in cache and cache[ex["id"]][0] == ex["de_bai"]}


def read_problems(items: list[dict], call, reader_log: list[dict] | None = None) -> dict[str, str]:
    """One reading call. Returns {exercise id: expression} for the problems it answered.

    Ids are matched leniently ("[B3]", "b3", "B3." all count as B3). If no id
    matches at all but there is exactly one answer per problem, answers are
    matched by position.
    """
    data = call(FORMALIZE_SYSTEM, formalize_prompt(items), FORMALIZE_SCHEMA, "bieu_thuc_doc_lap")
    rows = data.get("ket_qua", []) if isinstance(data, dict) else []
    if reader_log is not None:
        reader_log.append({"hoi": [it["id"] for it in items], "tra_loi": rows})
    wanted = {_normalize_id(it["id"]): it["id"] for it in items}
    answers: dict[str, str] = {}
    for row in rows:
        key = wanted.get(_normalize_id(str(row.get("id", ""))))
        if key and key not in answers:
            answers[key] = row.get("bieu_thuc", "")
    if not answers and rows and len(rows) == len(items):
        answers = {it["id"]: row.get("bieu_thuc", "") for it, row in zip(items, rows)}
    return answers


def _normalize_id(text: str) -> str:
    return re.sub(r"[\s\[\]().:#]", "", text).upper()


def _merge(worksheet: dict, fixed: list[dict]) -> dict:
    merged = copy.deepcopy(worksheet)
    position = {ex["id"]: i for i, ex in enumerate(merged["bai_tap"])}
    for item in fixed:
        if item.get("id") in position:
            merged["bai_tap"][position[item["id"]]] = item
        else:
            merged["bai_tap"].append(item)
            position[item["id"]] = len(merged["bai_tap"]) - 1
    return merged


def _next_id(worksheet: dict) -> int:
    numbers = [int(m.group(1)) for ex in worksheet["bai_tap"] if (m := re.fullmatch(r"B(\d+)", ex.get("id", "")))]
    return max(numbers, default=0) + 1
