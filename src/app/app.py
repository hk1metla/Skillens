import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

from src.app.ui import inject_css, render_nav
from src.app.views import render_home, render_login, render_recommendations, render_signup
from src.app.control_room import render_control_room



def main() -> None:
    st.set_page_config(
        page_title="Skillens | Personalized Learning",
        page_icon="✨",
        layout="wide",
    )

    inject_css()

    # Safely get route from query params (handles browser extension conflicts)
    try:
        route = st.query_params.get("page", "home")
        if isinstance(route, list):
            route = route[0] if route else "home"
    except (AttributeError, TypeError, KeyError):
        # Fallback if query_params has issues (e.g., browser extension conflicts)
        route = "home"

    if route == "explore":
        render_nav(route)
        render_recommendations()
    elif route == "login":
        render_login()
    elif route == "signup":
        render_nav(route)
        render_signup()
    elif route == "control":
        # Control room - hidden from navbar
        render_control_room()
    else:
        render_nav(route)
        render_home()

if __name__ == "__main__":
    main()

