"""Cầu Sách: ứng dụng minh họa.

Chạy:  python -m streamlit run app.py
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from causach.app_logic import MILP, apply_edits, exercise_table, recheck, run_allocation, save_approved
from causach.data import District, GeneratorConfig, generate_district
from causach.export import class_allocation, transfer_table
from causach.model import Settings
from causach.phieu import generate, load_lessons, verify
from causach.phieu.demo import LESSON as DEMO_LESSON
from causach.phieu.demo import demo_model
from causach.phieu.render import clean_display, pretty, student_markdown, teacher_markdown
from causach.ui_components import (APP_CSS, FLOW_MAP_HEIGHT, HEADER, check_board_data, check_board_height,
                                   check_board_html, comparison_table_html, flow_map_data, flow_map_html, intro,
                                   label, report_html, school_table_html, status, worksheet_html)
from causach.vn import fmt_dec, fmt_int

ROOT = Path(__file__).resolve().parent
BANK = Path(os.environ.get("CAUSACH_KHO", ROOT / "kho_phieu"))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

st.set_page_config(page_title="Cầu Sách", layout="wide")
st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(HEADER, unsafe_allow_html=True)


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def columns(spec, align="bottom"):
    """Columns aligned at the bottom when this Streamlit version supports it."""
    try:
        return st.columns(spec, vertical_alignment=align)
    except TypeError:
        return st.columns(spec)


def get_model(demo: bool):
    if demo:
        return demo_model()
    from causach.phieu import OpenAIModel
    try:
        return OpenAIModel()
    except RuntimeError as exc:
        html(status(f"Chưa dùng được OpenAI: {exc}. Thêm OPENAI_API_KEY vào tệp .env rồi chạy lại ứng dụng.", "bad"))
        return None


def board_round(title: str, report, unread=frozenset()) -> dict:
    items = []
    for item in report.items:
        if item.id in unread:
            items.append({"id": item.id, "status": "chua_doc_lai", "message": "Đề đã sửa; máy chưa đọc lại đề mới."})
        else:
            items.append({"id": item.id, "status": item.status, "message": item.message})
    return {"title": title, "items": items}


tab_alloc, tab_phieu, tab_eval = st.tabs(["Phân bổ sách", "Soạn và duyệt Phiếu Cầu", "Đánh giá"])

# ---------------------------------------------------------------------------
# 1. Book allocation
# ---------------------------------------------------------------------------
with tab_alloc:
    controls, results = st.columns([1, 2.6], gap="large")

    with controls:
        html(intro("Đọc bảng theo dõi của các trường và quyết định trường nào chuyển sách nào cho trường nào, "
                   "ưu tiên em không có sách và không có thiết bị (Luồng C)."))
        source = st.radio("Dữ liệu", ["Cụm trường mô phỏng", "Bảng theo dõi thật"], key="alloc_source")
        district = None
        if source == "Cụm trường mô phỏng":
            n_schools = st.slider("Số trường", 4, 16, 8, key="alloc_n")
            seed = st.number_input("Cụm số", 0, 999, 0, key="alloc_seed",
                                   help="Mỗi số cho một cụm trường mô phỏng khác nhau. Dữ liệu mô phỏng, không phải số liệu thật.")
            district = generate_district(int(seed), GeneratorConfig(n_schools=int(n_schools)))
        else:
            schools_file = st.file_uploader("Vị trí các trường (schools.csv)", type="csv", key="up_schools")
            sheet_file = st.file_uploader("Bảng theo dõi theo Phụ lục B (sheet.csv)", type="csv", key="up_sheet")
            if schools_file is not None and sheet_file is not None:
                try:
                    district = District.from_csv(schools_file, sheet_file)
                except (ValueError, KeyError) as exc:
                    html(status(f"Bảng chưa đúng mẫu: {exc}", "bad"))

        html(label("Chính sách", "lựa chọn của nhà quản lý"))
        ratio = st.select_slider("Ưu tiên em không có thiết bị", options=[1, 2, 3, 5, 10, 20], value=10,
                                 format_func=lambda v: f"gấp {v} lần", key="p_ratio",
                                 help="Một cuốn đến tay em không có thiết bị đáng giá gấp bao nhiêu lần một cuốn đến tay em đã đọc được sách điện tử.")
        trip = st.select_slider("Chi phí một chuyến chở sách", options=[0.0, 0.2, 0.6, 1.0, 2.0, 4.0], value=0.6,
                                format_func=lambda v: f"ngang {fmt_dec(v, 1)} cuốn", key="p_trip",
                                help="Quy ra số cuốn đến tay em Luồng C. Chuyến nào mang tới ít hơn chi phí của nó thì không đi.")
        per_km = st.select_slider("Chi phí thêm mỗi km", options=[0.0, 0.05, 0.1, 0.2, 0.4], value=0.1,
                                  format_func=lambda v: f"ngang {fmt_dec(v, 2)} cuốn", key="p_km")
        max_km = st.slider("Hai trường cách nhau tối đa", 3, 30, 15, format="%d km", key="p_maxkm")
        settings = Settings(weight_c=5.0, weight_a=5.0 / ratio, trip_fixed=5.0 * trip,
                            trip_per_km=5.0 * per_km, max_km=float(max_km))
        run_alloc = st.button("Lập kế hoạch", type="primary", key="run_alloc", disabled=district is None)

    if run_alloc and district is not None:
        with st.spinner("Đang tìm kế hoạch phân bổ tốt nhất…"):
            st.session_state["alloc"] = {"district": district, **run_allocation(district, settings)}

    with results:
        alloc = st.session_state.get("alloc")
        if alloc is None:
            html(status("Chọn dữ liệu và chính sách ở bên trái, rồi bấm Lập kế hoạch.", "quiet"))
        else:
            problem, plans, stats = alloc["problem"], alloc["plans"], alloc["stats"]
            coords = alloc["district"].schools.set_index("truong").loc[problem.schools, ["x_km", "y_km"]].to_numpy(float)
            components.html(flow_map_html(flow_map_data(problem, plans, stats, coords)), height=FLOW_MAP_HEIGHT)

            html(label("So sánh bốn cách làm", "trên cùng dữ liệu"))
            html(comparison_table_html(stats, MILP))

            html(label("Từng trường", "theo kế hoạch tối ưu, xếp theo số em còn thiếu"))
            html(school_table_html(problem, plans[MILP]))

            best = plans[MILP]
            transfers = transfer_table(problem, best)
            by_class = class_allocation(alloc["district"], problem, best)
            html(label("Tải về", "kế hoạch tối ưu, dạng CSV mở được bằng Excel"))
            d1, d2, _ = st.columns([1.3, 1.1, 1.2])
            d1.download_button(f"Danh sách điều chuyển ({fmt_int(len(transfers))} dòng)",
                               transfers.to_csv(index=False).encode("utf-8-sig"), "dieu_chuyen.csv", "text/csv",
                               key="dl_transfers")
            d2.download_button("Phân bổ theo lớp", by_class.to_csv(index=False).encode("utf-8-sig"),
                               "phan_bo_theo_lop.csv", "text/csv", key="dl_classes")


# ---------------------------------------------------------------------------
# 2. Worksheet generation and teacher review
# ---------------------------------------------------------------------------
with tab_phieu:
    lessons = load_lessons()
    controls, workspace = st.columns([1, 2.6], gap="large")

    with controls:
        html(intro("Mô hình soạn phiếu từ yêu cầu cần đạt, máy kiểm tra từng đáp án, "
                   "giáo viên duyệt câu chữ trước khi in."))
        mode = st.radio("Mô hình", ["Demo, không cần mạng", "OpenAI"], key="phieu_mode",
                        help="Bản demo chỉ có bài T6-02 và dùng một bản nháp viết tay có cài sẵn hai lỗi. "
                             "OpenAI cần khoá trong tệp .env.")
        demo = mode.startswith("Demo")
        codes = [DEMO_LESSON] if demo else list(lessons)
        code = st.selectbox("Bài", codes, format_func=lambda c: f"{c}: {lessons[c].title}", key="phieu_lesson")
        rounds = st.slider("Số vòng sửa tối đa", 0, 3, 2, key="phieu_rounds")
        cross = st.toggle("Đọc lại đề độc lập", value=True, key="phieu_cross",
                          help="Lớp kiểm tra thứ tư: một lần gọi riêng chỉ đọc đề và tự viết biểu thức.")
        with st.expander("Yêu cầu cần đạt của bài"):
            for req in lessons[code].requirements:
                st.markdown(f"**{req.code}** {req.text}")
        make = st.button("Soạn phiếu", type="primary", key="phieu_go")

    if make:
        model = get_model(demo)
        if model is not None:
            with st.spinner("Đang soạn và kiểm tra phiếu…"):
                result = generate(lessons[code], model, max_rounds=int(rounds), cross_check=bool(cross))
            st.session_state["phieu"] = {
                "lesson": code, "model": model.name, "demo": demo, "cross": bool(cross),
                "worksheet": result.worksheet, "report": result.final, "log": result.log,
                "readings": {ex["id"]: (ex["de_bai"], result.readings[ex["id"]])
                             for ex in result.worksheet["bai_tap"] if ex["id"] in result.readings},
                "unread": set(), "changed": [], "removed": [], "version": 0, "saved": None,
                "rounds": [board_round("Vòng 0: bản nháp của mô hình" if i == 0 else f"Vòng {i}: sau khi mô hình sửa", rep)
                           for i, rep in enumerate(result.reports)],
            }

    with workspace:
        state = st.session_state.get("phieu")
        if state is None:
            html(status("Chọn bài ở bên trái rồi bấm Soạn phiếu.", "quiet"))
        else:
            lesson = lessons[state["lesson"]]
            report = state["report"]
            n_ok, n_all = report.n_passed, len(report.items)
            repairs = len(state["log"]) - 1
            if report.passed and not state["unread"]:
                done = "ngay từ bản nháp" if repairs <= 0 else f"sau {repairs} vòng sửa"
                html(status(f"<b>{n_ok}/{n_all}</b> bài tập đạt cả bốn lớp kiểm tra, {done}."))
            else:
                html(status(f"<b>{n_ok}/{n_all}</b> bài tập đạt kiểm tra tự động. Xem các dòng chưa đạt bên dưới.", "bad"))

            board = check_board_data(state["rounds"],
                                     {ex["id"]: clean_display(ex["de_bai"]) for ex in state["worksheet"]["bai_tap"]},
                                     state["cross"])
            components.html(check_board_html(board), height=check_board_height(board))

            html(label("Giáo viên duyệt", "bỏ dấu ở cột Giữ để loại bài; sửa được câu chữ của đề và lời giải"))
            cc = st.column_config
            edited = st.data_editor(
                exercise_table(state["worksheet"], report, state["unread"]),
                disabled=["Mã", "YCCĐ", "Đáp án", "Kiểm tra"], hide_index=True, key=f"editor_{state['version']}",
                column_config={
                    "Giữ": cc.CheckboxColumn("Giữ", width="small"),
                    "Mã": cc.TextColumn("Mã", width="small"),
                    "YCCĐ": cc.TextColumn("YCCĐ", width="small"),
                    "Đề": cc.TextColumn("Đề", width="large"),
                    "Lời giải": cc.TextColumn("Lời giải", width="large"),
                    "Đáp án": cc.TextColumn("Đáp án", width="small"),
                    "Kiểm tra": cc.TextColumn("Máy kiểm tra", width="medium"),
                },
            )

            failing = [i.id for i in report.items if not i.passed and i.id not in state["unread"]]
            b1, b2, b3 = columns([1, 1.6, 1.4])
            recheck_clicked = b1.button("Kiểm tra lại", key="phieu_recheck")
            reviewer = b2.text_input("Tên người duyệt", key="phieu_reviewer", placeholder="Tên người duyệt",
                                     label_visibility="collapsed")
            own_check = True
            if state["unread"]:
                own_check = st.checkbox("Tôi đã tự kiểm tra các đề vừa sửa (máy chưa đọc lại"
                                        + (", bản demo không đọc lại đề mới)" if state["demo"] else ")"),
                                        key="phieu_own_check")
            can_save = bool(reviewer.strip()) and own_check and not failing
            approve = b3.button("Chấp nhận và lưu", type="primary", key="phieu_approve", disabled=not can_save)
            if failing:
                html(status(f"Chưa lưu được: {', '.join(failing)} chưa đạt kiểm tra tự động. Sửa hoặc bỏ các bài này.", "bad"))
            elif not reviewer.strip():
                html(status("Nhập tên người duyệt để lưu phiếu vào kho.", "quiet"))

            if recheck_clicked:
                worksheet, changed, removed = apply_edits(state["worksheet"], edited)
                if state["cross"]:
                    reader = None if state["demo"] else get_model(False)
                    report, readings, unread = recheck(worksheet, lesson, state["readings"], reader)
                else:
                    report, readings, unread = verify(worksheet, lesson), state["readings"], set()
                state["rounds"].append(board_round("Sau khi giáo viên sửa", report, unread))
                state.update(worksheet=worksheet, report=report, readings=readings, unread=unread,
                             changed=sorted(set(state["changed"]) | set(changed)),
                             removed=sorted(set(state["removed"]) | set(removed)),
                             version=state["version"] + 1)
                st.rerun()
            if approve:
                state["saved"] = save_approved(BANK, lesson, state["worksheet"], report, reviewer.strip(),
                                               model=state["model"], changed=state["changed"],
                                               removed=state["removed"], unread=state["unread"])
            if state["saved"]:
                html(status(f"Đã lưu phiếu vào kho: {state['saved']}"))

            student, teacher = st.tabs(["Bản học sinh", "Bản giáo viên"])
            with student:
                html(worksheet_html(state["worksheet"], lesson, clean=clean_display, pretty=pretty))
                st.download_button("Tải bản học sinh (.md)", student_markdown(state["worksheet"], lesson).encode("utf-8"),
                                   f"{lesson.code}_hoc_sinh.md", "text/markdown", key="dl_student")
            with teacher:
                html(worksheet_html(state["worksheet"], lesson, teacher=True, report=report, unread=state["unread"],
                                    clean=clean_display, pretty=pretty))
                st.download_button("Tải bản giáo viên (.md)",
                                   teacher_markdown(state["worksheet"], lesson, report, state["log"], state["model"]).encode("utf-8"),
                                   f"{lesson.code}_giao_vien.md", "text/markdown", key="dl_teacher")


# ---------------------------------------------------------------------------
# 3. Evaluation report
# ---------------------------------------------------------------------------
def describe_report(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    sheets = re.search(r"(\d+) phiếu", text)
    version = re.search(r"phiên bản câu lệnh: ([\d.\-, ]+)", text)
    when = datetime.fromtimestamp(path.stat().st_mtime).strftime("%d/%m %H:%M")
    bits = [f"{sheets.group(1)} phiếu" if sheets else None,
            f"câu lệnh {version.group(1).strip(' .')}" if version else None, f"cập nhật {when}"]
    return f"{path.parent.name}: " + ", ".join(b for b in bits if b)


with tab_eval:
    reports = sorted(ROOT.glob("*/bao_cao.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        html(status("Chưa có báo cáo. Chạy các bước đánh giá trong README "
                    "(ví dụ python -m causach danhgia sinh --out danh_gia_v5), rồi mở lại trang này.", "quiet"))
    else:
        left, _ = st.columns([1.4, 2])
        chosen = left.selectbox("Đợt đánh giá", reports, index=0, format_func=describe_report, key="eval_report")
        html(report_html(Path(chosen).read_text(encoding="utf-8")))
