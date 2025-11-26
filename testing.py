"""
Diagnostic tool to figure out how Strava exported your GPX files.
Run this to understand the naming pattern.
"""

import os
import pandas as pd
from pathlib import Path

# Load your CSV
df = pd.read_csv("data/activities.csv")  # Adjust path if needed

print("=" * 70)
print("STRAVA GPS MATCHING DIAGNOSTIC")
print("=" * 70)

# Get Activity IDs from CSV
activity_ids = df["Activity ID"].head(20).astype(str).tolist()
print(f"\n📋 Sample Activity IDs from CSV (first 20):")
for aid in activity_ids:
    print(f"  {aid}")

# Get GPX filenames
gpx_folder = "data/activities/activities"
gpx_files = [f for f in os.listdir(gpx_folder) if f.lower().endswith(".gpx")]
print(f"\n📁 Total GPX files found: {len(gpx_files)}")
print(f"\n📋 Sample GPX filenames (first 20):")
for gpx in gpx_files[:20]:
    print(f"  {gpx}")

# Test matching strategies
print("\n" + "=" * 70)
print("TESTING MATCH STRATEGIES")
print("=" * 70)

# Strategy 1: Exact match (e.g., 8083971283.gpx)
print("\n[Strategy 1] Exact Activity ID match")
matches_exact = 0
for aid in activity_ids:
    if f"{aid}.gpx" in gpx_files or f"{aid}.GPX" in gpx_files:
        matches_exact += 1
        print(f"  ✓ Found: {aid}.gpx")
print(f"  Total matches: {matches_exact}/{len(activity_ids)}")

# Strategy 2: Activity ID as substring
print("\n[Strategy 2] Activity ID as substring in filename")
matches_substring = 0
sample_matches = []
for aid in activity_ids:
    for gpx in gpx_files:
        if aid in gpx:
            matches_substring += 1
            if len(sample_matches) < 5:
                sample_matches.append((aid, gpx))
            break
if sample_matches:
    for aid, gpx in sample_matches:
        print(f"  ✓ {aid} → {gpx}")
print(f"  Total matches: {matches_substring}/{len(activity_ids)}")

# Strategy 3: Check if GPX filenames match any column in CSV
print("\n[Strategy 3] Checking all CSV columns for GPX filename matches")
for col in df.columns:
    if col not in ["Activity ID"]:
        matches = 0
        sample = None
        df_sample = df[col].head(20).astype(str)
        for val in df_sample:
            for gpx in gpx_files:
                if val in gpx or gpx.replace(".gpx", "") in val:
                    matches += 1
                    if sample is None:
                        sample = (val, gpx)
                    break
        if matches > 0:
            print(f"  ✓ Column '{col}': {matches} matches")
            if sample:
                print(f"    Example: {sample[0]} → {sample[1]}")

# Strategy 4: Match by Activity Name + Date + Distance
print("\n[Strategy 4] Fuzzy matching by Date + Distance")
if "Activity Date" in df.columns and "Distance" in df.columns:
    df["Activity Date"] = pd.to_datetime(df["Activity Date"], errors="coerce")
    df["Date_str"] = df["Activity Date"].dt.strftime("%Y%m%d")
    df["Distance_rounded"] = df["Distance"].round(1)
    
    matches = 0
    for _, row in df.head(10).iterrows():
        date_str = row["Date_str"]
        dist = row["Distance_rounded"]
        for gpx in gpx_files:
            if date_str in gpx:
                matches += 1
                print(f"  ✓ {date_str} ({dist}km) → {gpx}")
                break
    print(f"  Total matches by date: {matches}/10")

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("""
If Strategy 1 worked: Your GPX files are named correctly. 
  → The matching code should work with small fixes.

If Strategy 2 worked: Activity IDs appear as substrings.
  → Update the matching to use substring logic.

If Strategy 3 found matches: A different CSV column contains the GPX names.
  → Use that column instead of Activity ID for matching.

If none worked: Your GPX files may not be from Strava export,
  or they were exported with a different naming convention.
  → Check your export settings or re-export from Strava.
""")