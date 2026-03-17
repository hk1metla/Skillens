import os
import pandas as pd


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DATA_PATH = os.path.join(BASE_DIR, "Coursera_courses.csv")
OULAD_DIR = os.path.join(BASE_DIR, "data", "raw", "oulad")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "items.csv")

# Module code to subject mapping (based on OULAD dataset context)
MODULE_SUBJECTS = {
    "AAA": "Arts and Humanities",
    "BBB": "Business and Management",
    "CCC": "Computing and IT",
    "DDD": "Design and Innovation",
    "EEE": "Engineering and Technology",
    "FFF": "Health and Social Care",
    "GGG": "Science and Mathematics",
}


def _build_description(row: pd.Series) -> str:
    title = row["name"].strip()
    institution = row["institution"].strip()
    # Short, human-readable description since the source file has no text field.
    return (
        f"{title} by {institution}. "
        "A curated course designed to build practical skills and confidence."
    )


def _ingest_oulad() -> pd.DataFrame:
    """
    Ingest OULAD dataset and create module-level items (not individual VLE activities).
    This makes the items more understandable as "courses" rather than technical VLE resources.
    """
    vle_path = os.path.join(OULAD_DIR, "vle.csv")
    courses_path = os.path.join(OULAD_DIR, "courses.csv")

    if not os.path.exists(vle_path) or not os.path.exists(courses_path):
        return pd.DataFrame()

    vle = pd.read_csv(vle_path)
    courses = pd.read_csv(courses_path)

    # Aggregate VLE activities by module+presentation to create module-level items
    # This is more meaningful than individual VLE activities
    module_items = courses.copy()
    
    # Count activity types per module for description
    activity_counts = vle.groupby(["code_module", "code_presentation", "activity_type"]).size().reset_index(name="count")
    activity_summary = activity_counts.groupby(["code_module", "code_presentation"]).apply(
        lambda x: ", ".join([f"{row['activity_type']} ({row['count']})" for _, row in x.iterrows()]),
        include_groups=False,
    ).reset_index(name="activity_summary")
    
    module_items = module_items.merge(activity_summary, on=["code_module", "code_presentation"], how="left")
    
    # Create meaningful item_id (module + presentation)
    module_items["item_id"] = (
        "oulad_" + module_items["code_module"].astype(str) + "_" + 
        module_items["code_presentation"].astype(str)
    )
    
    # Create human-readable titles
    module_items["subject"] = module_items["code_module"].map(MODULE_SUBJECTS).fillna("General Studies")
    module_items["title"] = (
        module_items["subject"] + " - Module " + 
        module_items["code_module"].astype(str) + 
        " (" + module_items["code_presentation"].astype(str) + ")"
    )
    
    # Create meaningful descriptions
    module_items["description"] = (
        "Open University module in " + module_items["subject"] + ". "
        "Course duration: " + module_items["module_presentation_length"].astype(str) + " days. "
        "This module includes various learning resources and activities including: " +
        module_items["activity_summary"].fillna("online resources, content, and assessments") + "."
    )
    
    module_items["institution"] = "Open University"
    module_items["course_url"] = ""
    
    # Select final columns
    items = module_items[
        ["item_id", "title", "description", "institution", "course_url"]
    ].drop_duplicates(subset=["item_id"])
    
    return items


def _ingest_coursera() -> pd.DataFrame:
    """Ingest Coursera courses dataset."""
    if not os.path.exists(RAW_DATA_PATH):
        return pd.DataFrame()
    
    df = pd.read_csv(RAW_DATA_PATH)
    
    items = pd.DataFrame(
        {
            "item_id": "coursera_" + df["course_id"].astype(str),
            "title": df["name"],
            "description": df.apply(_build_description, axis=1),
            "institution": df["institution"],
            "course_url": df["course_url"],
        }
    )
    
    return items


def ingest() -> pd.DataFrame:
    """
    Ingest both OULAD and Coursera datasets and combine them.
    
    DUAL-DATASET STRATEGY:
    - OULAD (PRIMARY): Used for all evaluation, metrics, fairness analysis, ablations
      - Item IDs prefixed with "oulad_"
      - No external URLs (anonymized dataset)
      - Provides real interaction data, demographics, temporal structure
    - Coursera (SECONDARY): Used for demo UI only (screenshots/video with clickable links)
      - Item IDs prefixed with "coursera_"
      - Includes external course URLs
      - Not used in any quantitative evaluation
    
    The evaluation pipeline automatically filters to OULAD-only data.
    """
    all_items = []
    
    # Ingest OULAD
    oulad_items = _ingest_oulad()
    if not oulad_items.empty:
        all_items.append(oulad_items)
        print(f"Loaded {len(oulad_items)} items from OULAD dataset")
    
    # Ingest Coursera
    coursera_items = _ingest_coursera()
    if not coursera_items.empty:
        all_items.append(coursera_items)
        print(f"Loaded {len(coursera_items)} items from Coursera dataset")
    
    # Combine both datasets
    if all_items:
        combined_items = pd.concat(all_items, ignore_index=True)
        combined_items.to_csv(OUTPUT_PATH, index=False)
        print(f"Total items: {len(combined_items)} (OULAD: {len(oulad_items) if not oulad_items.empty else 0}, Coursera: {len(coursera_items) if not coursera_items.empty else 0})")
        return combined_items
    else:
        raise ValueError("No data sources found. Please ensure either OULAD or Coursera data is available.")


if __name__ == "__main__":
    ingest()

