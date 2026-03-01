import streamlit as st

from src.app.shared import (
    get_model_by_name,
    get_selected_model,
    is_oulad_item,
    load_interactions,
    load_items,
    log_feedback,
)
from src.app.ui import inject_css, render_nav
from src.explain.template import build_explanation


def main() -> None:

    inject_css()
    render_nav()

    st.markdown(
        """
        <div class="app-hero">
            <div class="hero-glow"></div>
            <span class="badge">Personalized</span>
            <span class="badge">Fast</span>
            <span class="badge">Transparent</span>
            <h1>Find the right course</h1>
            <p>Share your learning goal and we will curate a ranked shortlist.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    items = load_items()

    # Get model from session state (set in control room) or default to TF-IDF
    model_key = get_selected_model()
    if model_key == "hybrid":
        interactions = load_interactions()
        model = get_model_by_name(model_key, items, interactions)
    else:
        model = get_model_by_name(model_key, items)

    st.markdown("### Your goal")
    goal = st.text_input(
        "What do you want to learn?",
        placeholder="e.g., build ML foundations, improve data storytelling, learn cloud support",
        label_visibility="collapsed",
    )

    quick_goals = st.columns(4)
    presets = [
        "Machine learning foundations",
        "Business analytics and dashboards",
        "Front-end web development",
        "Cloud support essentials",
    ]
    for col, preset in zip(quick_goals, presets):
        with col:
            if st.button(preset, use_container_width=True):
                goal = preset
                st.session_state["goal_override"] = preset

    if "goal_override" in st.session_state:
        goal = st.session_state.pop("goal_override")

    k = st.slider("How many results would you like?", min_value=3, max_value=12, value=6)

    if st.button("Show recommendations", use_container_width=True):
        if not goal.strip():
            st.warning("Please enter a learning goal to get recommendations.")
            st.stop()

        recs = model.recommend(goal, k=k)
        results = recs.merge(items, on="item_id", how="left")
        returned_item_ids = results["item_id"].tolist()

        st.markdown("### Top matches for you")
        for idx, row in results.iterrows():
            score = float(row["score"])
            explanation = build_explanation(row["title"], similarity_score=score)
            item_id = row["item_id"]
            is_oulad = is_oulad_item(item_id)
            
            # DUAL-DATASET STRATEGY:
            # - OULAD items: Show internal detail view (no external URLs - anonymized dataset)
            # - Coursera items: Show clickable external links (for demo UI)
            if is_oulad:
                # OULAD item: Render internal detail view
                st.markdown(
                    f"""
                    <div class="rec-card">
                        <h3>{row["title"]} <span style="background: #6366f1; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">OULAD</span></h3>
                        <p>{row["description"]}</p>
                        <div class="rec-meta">Institution: {row["institution"]}</div>
                        <div class="rec-meta">Match strength: {score:.3f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                with st.expander("📚 View Course Details", expanded=False):
                    st.markdown(f"**{row['title']}**")
                    st.markdown(f"*{row['description']}*")
                    st.markdown("---")
                    st.markdown("**About this course:**")
                    st.info(
                        "This is an Open University module from the OULAD dataset. "
                        "OULAD is anonymized for privacy protection and does not include URLs to original content. "
                        "In a real deployment, this would link to the internal Learning Management System."
                    )
                    st.markdown("**Why this recommendation?**")
                    st.write(explanation)
            else:
                # Coursera item: Show clickable external link (for demo UI)
                st.markdown(
                    f"""
                    <div class="rec-card">
                        <h3>{row["title"]}</h3>
                        <p>{row["description"]}</p>
                        <div class="rec-meta">Institution: {row["institution"]}</div>
                        <div class="rec-meta">Match strength: {score:.3f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander("Why this recommendation?"):
                    st.write(explanation)
                    course_url = row.get('course_url', '#')
                    if course_url and course_url != 'nan' and course_url != '#':
                        st.write(f"[Open course page]({course_url})")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    f"👍 Helpful ({row['item_id']})", key=f"up_{row['item_id']}"
                ):
                    log_feedback(
                        goal,
                        row["item_id"],
                        "up",
                        model_used=model_key,
                        returned_item_ids=returned_item_ids,
                    )
            with col2:
                if st.button(
                    f"👎 Not for me ({row['item_id']})", key=f"down_{row['item_id']}"
                ):
                    log_feedback(
                        goal,
                        row["item_id"],
                        "down",
                        model_used=model_key,
                        returned_item_ids=returned_item_ids,
                    )


if __name__ == "__main__":
    main()

