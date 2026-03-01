def build_explanation(
    title: str,
    similarity_score: float | None = None,
    popularity_rank: int | None = None,
) -> str:
    parts = []

    if similarity_score is not None:
        parts.append("It closely matches your stated goal.")

    if popularity_rank is not None and popularity_rank <= 10:
        parts.append("It is popular with other learners.")

    if not parts:
        parts.append("It aligns with your learning interests.")

    return f"{title} is recommended because " + " ".join(parts)

