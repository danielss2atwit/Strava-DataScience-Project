import pandas as pd

def clean(df):
    # Keep only running activities
    df = df[df["Activity Type"] == "Run"].copy()
    
    # Parse dates safely
    df["Activity Date"] = pd.to_datetime(df["Activity Date"], errors="coerce")

    # Keep all needed columns for GPS matching + analysis
    df_clean = df[[
        "Activity ID",
        "Filename",
        "Activity Name",
        "Activity Date",
        "Distance",
        "Moving Time",
        "Average Speed",
        "Elevation Gain",
        "Average Grade Adjusted Pace",
        "Relative Effort"
    ]].copy()

    # Remove entries missing core metrics
    df_clean = df_clean.dropna(subset=["Distance", "Average Speed"])

    # TEMPORARY RouteID (distance-based) — will be overwritten by GPS_RouteID
    df_clean["RouteID"] = df_clean["Distance"].round(2)

    return df_clean
