import streamlit as st

from src.app.shared import set_active_user
from src.app.ui import inject_css, render_nav


def main() -> None:
    inject_css()
    render_nav()

    st.markdown("## Create your Skillens account")
    st.caption("Start tracking your learning goals and feedback.")

    with st.form("signup_form"):
        name = st.text_input("Full name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Create account")

    if submitted:
        if not name or not email or not password:
            st.warning("Please complete all fields.")
        else:
            # Demo-only account creation. Replace with real auth later.
            set_active_user(email)
            st.success("Account created. You can now explore recommendations.")


if __name__ == "__main__":
    main()

