import streamlit as st
from src.app.shared import (
    get_model_by_name,
    get_selected_model,
    is_oulad_item,
    load_interactions,
    load_items,
    load_tfidf_model,
    log_click,
    log_feedback,
)
from src.explain.template import build_explanation


def render_home() -> None:
    st.markdown(
        """
        <div class="snap-section">
            <div class="app-hero">
                <div class="hero-glow"></div>
                <div class="hero-gradient"></div>
                <div class="hero-inner">
                    <div class="hero-grid">
                        <div>
                            <span class="badge">Goal-driven</span>
                            <span class="badge">Explainable</span>
                            <span class="badge">Personalized</span>
                            <h1>One app for every learning goal.</h1>
                            <p>Skillens turns intent into a focused learning path with transparent, explainable recommendations.</p>
                            <div class="hero-actions">
                                <a class="pill">No hidden models</a>
                                <a class="pill">Fast results</a>
                                <a class="pill">Clear reasoning</a>
                            </div>
                        <div style="margin-top: 20px;">
                            <div class="section-title">Start with a goal</div>
                            <div class="section-subtitle">
                                Skillens is built for learners who want clarity. Share your goal and get a shortlist of courses
                                that match the skills you want to build.
                            </div>
                            <div style="margin-top: 16px;">
                                <a class="nav-login" href="?page=explore" target="_self">Get started</a>
                            </div>
                        </div>
                        </div>
                        <div class="stack-card">
                            <div class="section-title">Your learning summary</div>
                            <p class="rec-meta">Goal → Ranked shortlist → Next steps</p>
                            <div style="margin-top: 16px;">
                                <div class="pill">Build ML foundations</div>
                                <div class="pill">Practical projects</div>
                                <div class="pill">Career-ready skills</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="content-contrast">', unsafe_allow_html=True)
    st.markdown('<div class="snap-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-header">
            <div class="section-eyebrow">WHY SKILLENS</div>
            <div class="section-title-lg">What makes Skillens feel different</div>
            <div class="section-subtitle">A premium, guided experience that removes decision fatigue and keeps you focused on your goal.</div>
            <div class="section-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="feature-grid">
            <div class="feature-card-pro">
                <div class="feature-icon">🎯</div>
                <strong>Goal-first design</strong>
                <p>We center the experience around what you want to achieve.</p>
            </div>
            <div class="feature-card-pro">
                <div class="feature-icon">🔍</div>
                <strong>Clear reasoning</strong>
                <p>Every pick includes a short explanation you can trust.</p>
            </div>
            <div class="feature-card-pro">
                <div class="feature-icon">⚡</div>
                <strong>Beautifully focused</strong>
                <p>No clutter, no toggles — just a clean path forward.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown('<div class="snap-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-header">
            <div class="section-eyebrow">FLOW</div>
            <div class="section-title-lg">Unify your learning journey</div>
            <div class="section-subtitle">Three concise steps that keep you moving from goal to outcome.</div>
            <div class="section-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="section-shell">
            <div class="feature-card">
                <strong>Pick a goal</strong>
                <p>Start with a clear outcome and the system handles the rest.</p>
            </div>
            <br />
            <div class="feature-card">
                <strong>Get curated paths</strong>
                <p>See a ranked shortlist of courses that fit your intent.</p>
            </div>
            <br />
            <div class="feature-card">
                <strong>Act with confidence</strong>
                <p>Each recommendation includes a short explanation.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown('<div class="snap-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-header">
            <div class="section-eyebrow">IMPACT</div>
            <div class="section-title-lg">Success snapshot</div>
            <div class="section-subtitle">Evidence of focus, speed, and transparent recommendations.</div>
            <div class="section-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    stats = st.columns(3)
    stats_content = [
        ("600+", "Curated courses"),
        ("Fast", "Results in seconds"),
        ("Transparent", "Explainable recommendations"),
    ]
    for col, (value, label) in zip(stats, stats_content):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <strong style="font-size: 24px;">{value}</strong>
                    <p>{label}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown("### Trusted by focused learners")
    st.markdown(
        """
        <div class="logo-row">
            <span class="pill">Data Analytics</span>
            <span class="pill">Cloud Support</span>
            <span class="pill">Product Design</span>
            <span class="pill">AI Foundations</span>
            <span class="pill">Project Management</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown("### Explore in three steps")
    step_cols = st.columns(3)
    steps = [
        ("01", "Define your goal", "Tell us what you want to achieve."),
        ("02", "Get matched", "We rank courses that fit your intent."),
        ("03", "Start learning", "Pick a course and keep moving."),
    ]
    for col, (num, title, desc) in zip(step_cols, steps):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <strong>{num}</strong>
                    <p><strong>{title}</strong></p>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown('<div class="snap-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-header">
            <div class="section-eyebrow">FEEDBACK</div>
            <div class="section-title-lg">Learner feedback</div>
            <div class="section-subtitle">Real reactions from learners exploring goal-based recommendations.</div>
            <div class="section-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    testimonials = st.columns(3)
    quotes = [
        ("“The recommendations were spot on and easy to trust.”", "Amir K."),
        ("“Clean, focused, and fast. I found my course in minutes.”", "Sofia R."),
        ("“Love the explanations — feels transparent.”", "Jordan L."),
    ]
    for col, (quote, author) in zip(testimonials, quotes):
        with col:
            st.markdown(
                f"""
                <div class="testimonial-card">
                    <p>{quote}</p>
                    <div class="rec-meta">{author}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="site-footer">
            <div class="footer-inner">
                <span>© 2026 Skillens. All rights reserved.</span>
                <div class="footer-links">
                    <a href="?page=home" target="_self">Home</a>
                    <a href="?page=explore" target="_self">Explore</a>
                    <a href="?page=login" target="_self">Login</a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendations() -> None:
    st.markdown(
        """
        <div class="app-hero app-hero--compact enterprise-hero">
            <div class="hero-glow"></div>
            <div class="hero-gradient"></div>
            <div class="hero-inner">
                <div class="hero-grid">
                    <div>
                        <span class="badge">Personalized</span>
                        <span class="badge">Fast</span>
                        <span class="badge">Transparent</span>
                        <h1>Find the right course</h1>
                        <p>Share your learning goal and we will curate a ranked shortlist.</p>
                    </div>
                <div class="stack-card stack-card--enterprise">
                        <div class="section-title">Your goal input</div>
                        <p class="rec-meta">We transform goals into ranked matches.</p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        div[data-testid="stForm"] {
            background: #f8fafc;
            border-radius: 22px;
            padding: 32px;
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 20px 40px rgba(15, 23, 42, 0.12);
        }
        div[data-testid="stForm"] label,
        div[data-testid="stForm"] p,
        div[data-testid="stForm"] .stMarkdown {
            color: #0f172a !important;
        }
        div[data-testid="stForm"] input,
        div[data-testid="stForm"] textarea {
            background: #eef2f7 !important;
            color: #0f172a !important;
        }
        div[data-testid="stForm"] input::placeholder {
            color: #0f172a !important;
            opacity: 0.9;
        }
        div[data-testid="stForm"] .stButton > button {
            background: #0f172a !important;
            color: #ffffff !important;
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    items = load_items()
    
    # Get model from session state (set in control room) or default to TF-IDF
    model_key = get_selected_model()
    
    # Load the model (cached via @st.cache_resource in shared.py)
    if model_key == "hybrid":
        interactions = load_interactions()
        model = get_model_by_name(model_key, items, interactions)
    else:
        model = get_model_by_name(model_key, items)

    st.markdown("### Enter Your Course")
    # Use searchable selectbox for better performance with large datasets
    # Only load titles when needed (lazy loading)
    if "course_titles" not in st.session_state:
        st.session_state["course_titles"] = items["title"].dropna().unique().tolist()
    
    selected_title = st.selectbox(
        "Search courses",
        options=[""] + st.session_state["course_titles"],
        index=0,
        format_func=lambda x: x if x else "Enter your course",
    )

    presets = [
        "Machine learning foundations",
        "Business analytics and dashboards",
        "Front-end web development",
        "Cloud support essentials",
    ]
    preset_choice = st.radio(
        "Quick goals",
        presets,
        horizontal=True,
    )

    k = st.slider("How many results would you like?", min_value=3, max_value=12, value=6)
    
    # Automatically show recommendations when a goal is selected
    goal = selected_title or preset_choice
    if goal and goal.strip():
        with st.spinner("Finding the best courses for you..."):
            recs = model.recommend(goal, k=k)
            results = recs.merge(items, on="item_id", how="left")
        
        # Store returned item IDs for logging
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
                        <div class="rec-card-header">
                            <h3>{row["title"]}</h3>
                            <span class="badge" style="background: #6366f1; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">OULAD</span>
                        </div>
                        <p class="rec-card-description">{row["description"]}</p>
                        <div class="rec-card-footer">
                            <div class="rec-meta">🏛️ {row["institution"]}</div>
                            <div class="rec-meta rec-score">Match: {score:.2f}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                # Internal detail view for OULAD items
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
                course_url = str(row.get("course_url", "#"))
                if course_url == "nan" or not course_url or course_url == "#":
                    course_url = "#"
                
                st.markdown(
                    f"""
                    <a href="{course_url}" target="_blank" class="rec-card-link" onclick="
                        // Note: Click tracking happens server-side when user returns
                    ">
                        <div class="rec-card rec-card--clickable">
                            <div class="rec-card-header">
                                <h3>{row["title"]}</h3>
                                <div class="rec-card-arrow">→</div>
                            </div>
                            <p class="rec-card-description">{row["description"]}</p>
                            <div class="rec-card-footer">
                                <div class="rec-meta">🏛️ {row["institution"]}</div>
                                <div class="rec-meta rec-score">Match: {score:.2f}</div>
                            </div>
                        </div>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
                
                # Track click via button (user can click to open and track)
                if st.button(f"📖 Open & Track", key=f"open_{item_id}"):
                    log_click(goal, item_id, model_key, returned_item_ids)
                    if course_url and course_url != "#":
                        st.markdown(f'<meta http-equiv="refresh" content="0;url={course_url}">', unsafe_allow_html=True)

            # Show explanation expander (for both OULAD and Coursera)
            if not is_oulad:  # OULAD items already show explanation in detail view
                with st.container():
                    with st.expander("Why this recommendation?"):
                        st.write(explanation)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    f"👍 Helpful", key=f"up_{row['item_id']}"
                ):
                    log_feedback(
                        goal,
                        row["item_id"],
                        "up",
                        model_used=model_key,
                        returned_item_ids=returned_item_ids,
                    )
                    st.success("Thanks for your feedback!")
            with col2:
                if st.button(
                    f"👎 Not for me", key=f"down_{row['item_id']}"
                ):
                    log_feedback(
                        goal,
                        row["item_id"],
                        "down",
                        model_used=model_key,
                        returned_item_ids=returned_item_ids,
                    )
                    st.info("We'll improve our recommendations.")

    st.markdown("### Popular courses")
    # Cache popular courses computation
    if "popular_courses" not in st.session_state:
        try:
            from src.models.popularity import PopularityRecommender
            # Use train split (already loaded and cached) instead of full interactions
            train_interactions = load_interactions()
            if not train_interactions.empty:
                popularity = PopularityRecommender()
                popularity.fit(train_interactions)
                top_items = popularity.recommend(k=3)["item_id"].tolist()
                st.session_state["popular_courses"] = items[items["item_id"].isin(top_items)]
            else:
                st.session_state["popular_courses"] = items.head(3)
        except Exception:
            st.session_state["popular_courses"] = items.head(3)
    
    popular_df = st.session_state["popular_courses"]

    pop_cols = st.columns(3)
    for col, (_, row) in zip(pop_cols, popular_df.iterrows()):
        with col:
            st.markdown(
                f"""
                <div class="rec-card rec-card--enterprise">
                    <h3>{row["title"]}</h3>
                    <p>{row["description"]}</p>
                    <div class="rec-meta">Institution: {row["institution"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_login() -> None:
    active_user = st.session_state.get("active_user")
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        st.markdown(
            """
            <div class="auth-header">
                <span class="auth-brand">Skillens</span>
                <a class="auth-back" href="?page=home" target="_self">← Back to Home</a>
            </div>
            <div class="auth-title auth-center">Welcome back</div>
            <div class="auth-subtitle auth-center">Sign in to keep your learning journey saved.</div>
            """,
            unsafe_allow_html=True,
        )

        if active_user:
            st.success(f"You're signed in as {active_user}.")
            if st.button("Sign out"):
                st.session_state.pop("active_user", None)
            st.markdown("</div>", unsafe_allow_html=True)
            return

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in")

        if submitted:
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                st.session_state["active_user"] = email
                st.success("You're signed in. Head to Explore to get started.")

        st.markdown(
            """
            <div style="margin-top: 18px; font-size: 14px; color: #cbd5f5;">
                Don't have an account?
                <a class="auth-link" href="?page=signup" target="_self">Create one</a>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_signup() -> None:
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
            st.session_state["active_user"] = email
            st.success("Account created. You can now explore recommendations.")

