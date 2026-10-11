"""Runs app.py end to end against a stand-in for Streamlit.

This does not test Streamlit's rendering; it tests that every path through
our own code (buttons, edits, re-check, approval) runs without errors and
produces the expected state. Run with `python tests/test_app.py`.
"""
from __future__ import annotations

import os
import runpy
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class _State(dict):
    __getattr__ = dict.get

    def __setattr__(self, key, value):
        self[key] = value


class FakeStreamlit(types.ModuleType):
    """Just enough of the Streamlit API for app.py. Widgets return their defaults unless overridden."""

    def __init__(self):
        super().__init__("streamlit")
        self.session_state = _State()
        self.pressed: set[str] = set()
        self.values: dict = {}
        self.messages: list[tuple[str, str]] = []
        self.rerun_requested = False

    # layout -------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def tabs(self, names):
        return [self for _ in names]

    def columns(self, spec, gap=None, vertical_alignment=None):
        return [self for _ in range(spec if isinstance(spec, int) else len(spec))]

    class _ColumnConfig:
        def __getattr__(self, name):
            return lambda *a, **k: {"type": name, "args": a, **k}

    column_config = _ColumnConfig()

    def expander(self, *a, **k):
        return self

    def spinner(self, *a, **k):
        return self

    # output -------------------------------------------------------------
    def _say(kind):
        def method(self, text="", *a, **k):
            self.messages.append((kind, str(text)))
        return method

    set_page_config = title = caption = subheader = write = markdown = _say("text")
    info, warning, error, success = _say("info"), _say("warning"), _say("error"), _say("success")

    def metric(self, label, value, *a, **k):
        self.messages.append(("metric", f"{label}={value}"))

    def pyplot(self, fig, *a, **k):
        import matplotlib.pyplot as plt
        assert fig is not None
        plt.close(fig)

    def dataframe(self, data, *a, **k):
        assert len(data.columns) > 0

    def image(self, *a, **k):
        pass

    def download_button(self, label, data, *a, **k):
        assert data

    # widgets ------------------------------------------------------------
    def _value(self, key, default):
        return self.values.get(key, default)

    def radio(self, label, options, index=0, key=None, **k):
        return self._value(key, options[index])

    def selectbox(self, label, options, index=0, format_func=str, key=None, **k):
        options = list(options)
        for option in options:
            format_func(option)
        return self._value(key, options[index])

    def slider(self, label, min_value=None, max_value=None, value=None, step=None, key=None, **k):
        return self._value(key, value)

    def number_input(self, label, min_value=None, max_value=None, value=None, step=None, key=None, **k):
        return self._value(key, value)

    def select_slider(self, label, options=(), value=None, format_func=str, key=None, **k):
        for option in options:
            format_func(option)
        return self._value(key, value if value is not None else list(options)[0])

    def toggle(self, label, value=False, key=None, **k):
        return self._value(key, value)

    checkbox = toggle

    def text_input(self, label, value="", key=None, **k):
        return self._value(key, value)

    def file_uploader(self, *a, key=None, **k):
        return self._value(key, None)

    def button(self, label, key=None, disabled=False, **k):
        return (key in self.pressed) and not disabled

    def data_editor(self, data, key=None, **k):
        edit = self.values.get("data_editor")
        return edit(data.copy()) if edit else data

    def rerun(self):
        self.rerun_requested = True


def run(fake: FakeStreamlit, **values):
    fake.values.update(values)
    fake.rerun_requested = False
    runpy.run_path(str(ROOT / "app.py"), run_name="__main__")


def test_app_end_to_end():
    fake = FakeStreamlit()
    html_blocks: list[str] = []
    v1 = types.ModuleType("streamlit.components.v1")
    v1.html = lambda html, height=None, **k: html_blocks.append(html)
    components = types.ModuleType("streamlit.components")
    components.v1 = v1
    fake.components = components
    sys.modules.update({"streamlit": fake, "streamlit.components": components, "streamlit.components.v1": v1})
    with tempfile.TemporaryDirectory() as bank:
        os.environ["CAUSACH_KHO"] = bank

        run(fake)                                                     # first load: nothing computed yet
        assert fake.session_state.get("alloc") is None

        fake.pressed = {"run_alloc"}                                  # allocation with default settings
        run(fake)
        assert fake.session_state["alloc"]["plans"]["Tối ưu (MILP)"].status == "optimal"
        assert any("Phát lại" in h and '"edges"' in h for h in html_blocks)          # animated map rendered
        assert any("cs-table" in kind_text for _, kind_text in fake.messages)      # comparison table rendered

        fake.pressed = {"phieu_go"}                                   # demo worksheet
        run(fake)
        state = fake.session_state["phieu"]
        assert state["report"].passed and len(state["worksheet"]["bai_tap"]) == 6

        def edit(table):                                              # teacher drops B5 and rewords B1
            table.loc[table["Mã"] == "B5", "Giữ"] = False
            table.loc[table["Mã"] == "B1", "Đề"] = "Hãy tính 2⁵."
            return table
        fake.pressed = {"phieu_recheck"}
        run(fake, data_editor=edit)
        assert fake.rerun_requested
        state = fake.session_state["phieu"]
        assert [ex["id"] for ex in state["worksheet"]["bai_tap"]] == ["B1", "B2", "B3", "B4", "B6"]
        assert state["unread"] == {"B1"} and state["removed"] == ["B5"] and state["changed"] == ["B1"]
        assert [r["title"] for r in state["rounds"]][-1] == "Sau khi giáo viên sửa"
        assert any(i["status"] == "chua_doc_lai" for i in state["rounds"][-1]["items"])

        fake.values.pop("data_editor")
        fake.pressed = {"phieu_approve"}                              # blocked: no reviewer name yet
        run(fake)
        assert state["saved"] is None

        run(fake, phieu_reviewer="Bao", phieu_own_check=True)         # reviewer named, edits self-checked
        saved = fake.session_state["phieu"]["saved"]
        assert saved is not None and (saved / "duyet.json").exists()
        record = (saved / "duyet.json").read_text(encoding="utf-8")
        assert '"nguoi_duyet": "Bao"' in record and '"B5"' in record

        fake.pressed = set()                                          # evaluation tab renders
        run(fake)
    for name in ("streamlit", "streamlit.components", "streamlit.components.v1"):
        del sys.modules[name]


if __name__ == "__main__":
    test_app_end_to_end()
    print("ok  test_app_end_to_end\n1 tests passed")
