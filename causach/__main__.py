"""Command line.

    python -m causach generate --seed 0 --schools 8 --out data/sample
    python -m causach plan --schools-csv data/sample/schools.csv --sheet data/sample/sheet.csv --out results/plan
    python -m causach compare --seeds 30 --schools 8 --out results
    python -m causach scale --out results
    python -m causach lessons
    python -m causach phieu --lesson T6-02 --out kho_phieu          (needs OPENAI_API_KEY in .env)
    python -m causach phieu --demo --out results/phieu_demo         (offline, scripted model)
    python -m causach danhgia sinh --samples 2 --out danh_gia        (evaluation, needs the key)
    python -m causach danhgia gay-loi --out danh_gia
    python -m causach danhgia mau-thu-cong --out danh_gia
    python -m causach danhgia tong-hop --out danh_gia
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd

from .baselines import GREEDY_C_FIRST, GREEDY_SCHOOL_FIRST, greedy_nearest, no_coordination
from .data import District, GeneratorConfig, build_problem, generate_district
from .export import class_allocation, transfer_table
from .metrics import evaluate
from .model import Settings
from .optimize import solve

MILP = "Tối ưu (MILP)"
METHOD_ORDER = ["Không điều phối", GREEDY_SCHOOL_FIRST, GREEDY_C_FIRST, MILP]


def cmd_generate(args) -> None:
    district = generate_district(args.seed, GeneratorConfig(n_schools=args.schools))
    district.to_csv(args.out)
    print(f"wrote {args.out}/schools.csv and {args.out}/sheet.csv ({len(district.sheet)} rows, simulated)")


def cmd_plan(args) -> None:
    district = District.from_csv(args.schools_csv, args.sheet)
    problem = build_problem(district)
    settings = Settings()
    plan = solve(problem, settings, time_limit=args.time_limit)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    transfer_table(problem, plan).to_csv(out / "dieu_chuyen.csv", index=False)
    class_allocation(district, problem, plan).to_csv(out / "phan_bo_theo_lop.csv", index=False)
    metrics = evaluate(problem, plan, settings)
    print(f"status: {plan.status}")
    for key in ("need_c", "covered_c", "luong_c_left", "books_moved", "trips", "km"):
        print(f"  {key:>14}: {metrics[key]}")
    print(f"wrote {out}/dieu_chuyen.csv and {out}/phan_bo_theo_lop.csv")


def run_methods(seed: int, n_schools: int, settings: Settings, area_km: float | None = None) -> list[dict]:
    config = GeneratorConfig(n_schools=n_schools) if area_km is None else GeneratorConfig(n_schools=n_schools, area_km=area_km)
    problem = build_problem(generate_district(seed, config))
    plans = [
        no_coordination(problem),
        greedy_nearest(problem, settings, seed=seed, c_first=False),
        greedy_nearest(problem, settings, seed=seed, c_first=True),
        solve(problem, settings),
    ]
    return [{"seed": seed, "n_schools": n_schools, **evaluate(problem, p, settings)} for p in plans]


def cmd_compare(args) -> None:
    settings = Settings()
    rows = []
    for seed in range(args.seeds):
        rows += run_methods(seed, args.schools, settings)
    df = pd.DataFrame(rows)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "per_seed.csv", index=False)

    cols = ["coverage_c", "luong_c_left", "books_moved", "trips", "km", "objective", "runtime_s"]
    summary = df.groupby("method")[cols].agg(["mean", "std"]).reindex(METHOD_ORDER)
    summary.to_csv(out / "summary.csv")

    left = df.pivot(index="seed", columns="method", values="luong_c_left")
    trips = df.pivot(index="seed", columns="method", values="trips")
    best = GREEDY_C_FIRST
    fewer_left = int((left[MILP] < left[best]).sum())
    equal_left = int((left[MILP] == left[best]).sum())
    more_left = int((left[MILP] > left[best]).sum())
    fewer_trips = int((trips[MILP] < trips[best]).sum())
    trip_cut = 1 - trips[MILP].sum() / trips[best].sum()
    paired = (left[best] - left[MILP]).mean()

    print(f"{args.seeds} simulated districts, {args.schools} schools each\n")
    print(_markdown_summary(summary))
    print(f"\nPaired against the stronger greedy ({best}), district by district:")
    print(f"  Luồng C left: MILP lower in {fewer_left}, equal in {equal_left}, higher in {more_left} "
          f"(mean difference {paired:.1f} pairs per district)")
    print(f"  trips: MILP fewer in {fewer_trips}/{args.seeds}; {trip_cut:.0%} fewer trips in total")
    _plot(df, out / "compare.png", args.seeds, args.schools)
    print(f"wrote {out}/per_seed.csv, {out}/summary.csv, {out}/compare.png")


def cmd_scale(args) -> None:
    settings = Settings()
    rows = []
    for n in args.sizes:
        area = 12.0 * math.sqrt(n / 8)            # keep school density constant
        for seed in range(args.seeds):
            for r in run_methods(seed, n, settings, area_km=area):
                if r["method"] == MILP:
                    rows.append(r)
    df = pd.DataFrame(rows)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "scale.csv", index=False)
    table = df.groupby("n_schools")["runtime_s"].agg(["mean", "max"]).round(2)
    print("MILP solve time by district size (seconds)\n")
    print(table.to_string())


def cmd_lessons(args) -> None:
    from .phieu import load_lessons
    for lesson in load_lessons().values():
        print(f"{lesson.code}  {lesson.title}")
        for req in lesson.requirements:
            print(f"    {req.code}  {req.text}")


def cmd_phieu(args) -> None:
    from .phieu import generate, get_lesson
    from .phieu.store import write_run

    if args.demo:
        from .phieu.demo import LESSON, demo_model
        if args.lesson not in (None, LESSON):
            raise SystemExit(f"--demo only has scripted answers for {LESSON}")
        lesson, model = get_lesson(LESSON), demo_model()
    else:
        if not args.lesson:
            raise SystemExit("--lesson is required; list lessons with: python -m causach lessons")
        _load_env()
        from .phieu import OpenAIModel
        try:
            lesson, model = get_lesson(args.lesson), OpenAIModel(args.model)
        except (RuntimeError, KeyError) as exc:
            raise SystemExit(f"error: {exc}") from None

    result = generate(lesson, model, max_rounds=args.rounds, cross_check=not args.no_cross_check,
                      n_exercises=args.exercises)
    out = Path(args.out) / lesson.code
    write_run(out, lesson, result, cross_check=not args.no_cross_check, max_rounds=args.rounds)

    for line in result.log:
        print(line)
    print(f"{result.calls} model calls, {result.input_tokens + result.output_tokens} tokens")
    print(f"wrote {out / 'phieu_giao_vien.md'} (and phieu_hoc_sinh.md, phieu.json, kiem_tra.json)")


def cmd_danhgia(args) -> None:
    from .phieu import danhgia, get_lesson, load_lessons
    from .phieu.store import load_runs

    root = Path(args.out)
    if args.step == "sinh":
        lessons = [get_lesson(c) for c in args.lessons] if args.lessons else list(load_lessons().values())
        if args.demo:
            from .phieu.demo import LESSON, demo_model
            lessons, factory = [get_lesson(LESSON)], demo_model
        else:
            factory = _openai_factory(args.model)
        n = len(lessons) * args.samples
        print(f"{n} phiếu; ước tính khoảng {n * 0.6:.0f} cent với gpt-5-mini (theo các lần chạy trước)")
        danhgia.run_generation(lessons, args.samples, factory, root, max_rounds=args.rounds)
    elif args.step == "gay-loi":
        runs = load_runs(root / "sinh")
        if not runs:
            raise SystemExit(f"chưa có phiếu trong {root / 'sinh'}; chạy bước sinh trước")
        (root / "gay_loi").mkdir(parents=True, exist_ok=True)
        offline = danhgia.offline_mutants(runs)
        offline.to_csv(root / "gay_loi" / "offline.csv", index=False)
        print(f"lỗi cài không cần mô hình: {len(offline)} ca")
        if not args.offline_only:
            online, usage = danhgia.online_mutants(runs, _openai_factory(args.model)())
            online.to_csv(root / "gay_loi" / "online.csv", index=False)
            (root / "gay_loi" / "online_usage.json").write_text(json.dumps(usage), encoding="utf-8")
            print(f"lỗi cài cần mô hình đọc lại: {len(online)} ca, {usage['calls']} lần gọi, "
                  f"{usage['input_tokens'] + usage['output_tokens']} token")
    elif args.step == "mau-thu-cong":
        path = root / "thu_cong.xlsx"
        if path.exists() and not args.force:
            raise SystemExit(f"{path} đã có (có thể bạn đã điền); dùng --force để ghi đè")
        count = danhgia.export_review_sheet(load_runs(root / "sinh"), path, n=args.n, seed=args.seed)
        print(f"wrote {path} ({count} bài). Mở bằng Excel, điền 1/0 vào các cột tiêu chí, lưu lại.")
    elif args.step == "tong-hop":
        print(f"wrote {danhgia.write_report(root)}")


def _openai_factory(model_name: str | None):
    _load_env()
    from .phieu import OpenAIModel
    try:
        OpenAIModel(model_name)          # fail early with a clear message
    except RuntimeError as exc:
        raise SystemExit(f"error: {exc}") from None
    return lambda: OpenAIModel(model_name)


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _markdown_summary(summary: pd.DataFrame) -> str:
    header = "| Phương án | Tỷ lệ phủ Luồng C | Luồng C còn lại | Sách điều chuyển | Số chuyến | km |\n|---|---|---|---|---|---|"
    lines = [header]
    for method, row in summary.iterrows():
        lines.append(
            f"| {method} | {row[('coverage_c', 'mean')]:.1%} | "
            f"{row[('luong_c_left', 'mean')]:.0f} ± {row[('luong_c_left', 'std')]:.0f} | "
            f"{row[('books_moved', 'mean')]:.0f} | {row[('trips', 'mean')]:.1f} | {row[('km', 'mean')]:.0f} |"
        )
    return "\n".join(lines)


def _plot(df: pd.DataFrame, path: Path, seeds: int, schools: int) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = ["#b5b5b5", "#8a8a8a", "#5a5a5a", "#1f5fbf"]
    labels = ["Không\nđiều phối", "Tham lam\n(trường trước)", "Tham lam\n(Luồng C trước)", "Tối ưu\n(MILP)"]
    data = df.assign(coverage_pct=df["coverage_c"] * 100)
    panels = [("coverage_pct", "Học sinh Luồng C được nhận sách in (%)"), ("trips", "Số chuyến chở sách mỗi cụm")]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, (col, title) in zip(axes, panels):
        stats = data.groupby("method")[col].agg(["mean", "std", "count"]).reindex(METHOD_ORDER)
        ci95 = 1.96 * stats["std"] / stats["count"] ** 0.5
        ax.bar(range(4), stats["mean"], yerr=ci95, color=colors, capsize=4)
        top = (stats["mean"] + ci95.fillna(0)).max()
        for i, (value, err) in enumerate(zip(stats["mean"], ci95.fillna(0))):
            ax.text(i, value + err + 0.02 * top, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
        ax.set_ylim(0, top * 1.12)
        ax.set_xticks(range(4), labels)
        ax.set_title(title, fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"{seeds} cụm trường mô phỏng, mỗi cụm {schools} trường. "
                 "Thanh lỗi: khoảng tin cậy 95% của giá trị trung bình.", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(prog="causach")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate", help="write a simulated district as CSV")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--schools", type=int, default=8)
    p.add_argument("--out", default="data/sample")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("plan", help="make an allocation plan from CSV files")
    p.add_argument("--schools-csv", required=True)
    p.add_argument("--sheet", required=True)
    p.add_argument("--out", default="results/plan")
    p.add_argument("--time-limit", type=float, default=60.0)
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("compare", help="compare the optimizer with the baselines")
    p.add_argument("--seeds", type=int, default=30)
    p.add_argument("--schools", type=int, default=8)
    p.add_argument("--out", default="results")
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("scale", help="time the optimizer on larger districts")
    p.add_argument("--sizes", type=int, nargs="+", default=[8, 16, 32, 64])
    p.add_argument("--seeds", type=int, default=2)
    p.add_argument("--out", default="results")
    p.set_defaults(func=cmd_scale)

    p = sub.add_parser("lessons", help="list curriculum lessons and their learning requirements")
    p.set_defaults(func=cmd_lessons)

    p = sub.add_parser("phieu", help="generate and check a Phiếu Cầu worksheet")
    p.add_argument("--lesson", help="lesson code, e.g. T6-02")
    p.add_argument("--rounds", type=int, default=2, help="repair rounds; 0 = one-shot")
    p.add_argument("--exercises", type=int, default=6)
    p.add_argument("--no-cross-check", action="store_true", help="skip the independent re-derivation")
    p.add_argument("--model", help="OpenAI model name (default: OPENAI_MODEL or gpt-5-mini)")
    p.add_argument("--demo", action="store_true", help="offline demo with a scripted model (lesson T6-02)")
    p.add_argument("--out", default="kho_phieu")
    p.set_defaults(func=cmd_phieu)

    p = sub.add_parser("danhgia", help="evaluate the worksheet generator and its checker")
    p.add_argument("step", choices=["sinh", "gay-loi", "mau-thu-cong", "tong-hop"])
    p.add_argument("--out", default="danh_gia")
    p.add_argument("--lessons", nargs="+", help="lesson codes (default: all)")
    p.add_argument("--samples", type=int, default=2, help="worksheets per lesson")
    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--model")
    p.add_argument("--demo", action="store_true", help="scripted model, lesson T6-02 only")
    p.add_argument("--offline-only", action="store_true", help="gay-loi: skip the checks that call the model")
    p.add_argument("--n", type=int, default=20, help="mau-thu-cong: exercises to sample")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_danhgia)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
