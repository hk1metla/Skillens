"""
Load OULAD student demographics for fairness evaluation.

Loads studentInfo.csv from the OULAD dataset and provides
demographic group mappings for per-group evaluation.
"""

import os
from typing import Dict, List

import pandas as pd


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OULAD_DIR = os.path.join(BASE_DIR, "data", "raw", "oulad")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "demographics.csv")


def load_demographics() -> pd.DataFrame:
    """
    Load student demographics from OULAD studentInfo.csv.
    
    Returns:
        DataFrame with columns: user_id, gender, region, highest_education,
        imd_band, age_band, disability, final_result
    """
    student_info_path = os.path.join(OULAD_DIR, "studentInfo.csv")
    
    if not os.path.exists(student_info_path):
        return pd.DataFrame()
    
    df = pd.read_csv(student_info_path)
    
    # Create user_id from id_student (combine with module/presentation for uniqueness)
    # For interactions, we use id_student as user_id, so we need to handle
    # the case where a student appears in multiple modules
    df["user_id"] = df["id_student"].astype(str)
    
    # Select relevant demographic columns
    demographics = df[[
        "user_id",
        "gender",
        "region",
        "highest_education",
        "imd_band",
        "age_band",
        "disability",
        "final_result",
        "num_of_prev_attempts",
        "studied_credits",
    ]].copy()
    
    # Handle missing values
    demographics = demographics.fillna("unknown")

    # Deduplicate by user_id (per PDF E.1: "Deduplicate demographics by user id")
    # Keep first occurrence so we have one row per student
    demographics = demographics.drop_duplicates(subset=["user_id"], keep="first")
    
    # Save processed demographics
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    demographics.to_csv(OUTPUT_PATH, index=False)
    
    return demographics


def get_demographic_groups(demographics: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Group users by demographic attributes for fairness evaluation.
    
    Returns:
        Dict mapping group name to list of user_ids
    """
    groups = {}
    
    if demographics.empty:
        return groups
    
    # Group by gender
    if "gender" in demographics.columns:
        for gender in demographics["gender"].unique():
            if pd.notna(gender) and gender != "unknown":
                groups[f"gender_{gender}"] = demographics[
                    demographics["gender"] == gender
                ]["user_id"].tolist()
    
    # Group by age band
    if "age_band" in demographics.columns:
        for age in demographics["age_band"].unique():
            if pd.notna(age) and age != "unknown":
                groups[f"age_{age}"] = demographics[
                    demographics["age_band"] == age
                ]["user_id"].tolist()
    
    # Group by highest education
    if "highest_education" in demographics.columns:
        for edu in demographics["highest_education"].unique():
            if pd.notna(edu) and edu != "unknown":
                # Clean education labels for group names
                edu_clean = edu.replace(" ", "_").lower()
                groups[f"education_{edu_clean}"] = demographics[
                    demographics["highest_education"] == edu
                ]["user_id"].tolist()
    
    # Group by disability status
    if "disability" in demographics.columns:
        for disability in demographics["disability"].unique():
            if pd.notna(disability) and disability != "unknown":
                groups[f"disability_{disability}"] = demographics[
                    demographics["disability"] == disability
                ]["user_id"].tolist()
    
    # Group by final result (outcome-based)
    if "final_result" in demographics.columns:
        for result in demographics["final_result"].unique():
            if pd.notna(result) and result != "unknown":
                groups[f"outcome_{result.lower()}"] = demographics[
                    demographics["final_result"] == result
                ]["user_id"].tolist()
    
    return groups


if __name__ == "__main__":
    demographics = load_demographics()
    if not demographics.empty:
        print(f"Loaded {len(demographics)} student demographic records")
        print(f"Columns: {demographics.columns.tolist()}")
        groups = get_demographic_groups(demographics)
        print(f"Created {len(groups)} demographic groups")
    else:
        print("No OULAD demographics found. Using Coursera fallback data.")
