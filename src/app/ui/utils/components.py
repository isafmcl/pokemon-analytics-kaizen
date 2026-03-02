from __future__ import annotations
from pathlib import Path
import streamlit as st

_CURRENT_FILE = Path(__file__).resolve()
_APP_ROOT = _CURRENT_FILE.parents[2]


def inject_theme() -> None:
    css_path = _APP_ROOT / "ui" / "dashboard_theme.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
