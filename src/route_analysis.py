import pandas as pd

def compute_route_stats(df_clean):
    """
    Group by RouteID and compute statistics.
    IMPORTANT: Column names must match what's in df_clean!
    """
    route_stats = df_clean.groupby("RouteID").agg({
        "Average Speed": ["mean", "median", "std"],
        "Average Grade Adjusted Pace": "mean",
        "Elevation Gain": "mean",
        "Relative Effort": "mean",
        "Distance": ["mean", "count"]
    })
    
    # Flatten multi-level column names
    route_stats.columns = ['_'.join(col).strip() for col in route_stats.columns]
    return route_stats.reset_index()
