import streamlit as st

from src.app.shared import clear_active_user, get_active_user, set_active_user
from src.app.ui import inject_css, render_nav


def main() -> None:
    inject_css()
    render_nav()

    st.markdown("## Welcome back")
    st.caption("Sign in to save your progress and personalized history.")

    active_user = get_active_user()
    if active_user:
        st.success(f"You're signed in as {active_user}.")
        if st.button("Sign out"):
            clear_active_user()
        return

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            # This is a placeholder sign-in for the demo.
            set_active_user(email)
            st.success("You're signed in. Head to Explore to get started.")


if __name__ == "__main__":
    main()

