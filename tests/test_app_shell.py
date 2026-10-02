"""Tests for app/main.py (R13)."""

import pathlib

from streamlit.testing.v1 import AppTest

APP_MAIN = pathlib.Path(__file__).resolve().parents[1] / "app" / "main.py"


def test_app_shell_renders():
    """R13: the Streamlit app shell renders without error."""
    at = AppTest.from_file(str(APP_MAIN))
    at.run()
    assert not at.exception