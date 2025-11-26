import pandas as pd

def compute_route_stats(df_clean):
    """
    Group by RouteID and compute statistics.
    Converts Average Speed (m/s) to pace (min/mile).
    """
    # Convert Average Speed from m/s to pace (min/mile)
    # 1 m/s = 2.237 mph
    # pace (min/mile) = 60 / speed (mph)
    df_clean_copy = df_clean.copy()
    df_clean_copy["Pace_min_per_mile"] = (60 / (df_clean_copy["Average Speed"] * 2.237)).round(2)
    
    route_stats = df_clean_copy.groupby("RouteID").agg({
        "Pace_min_per_mile": ["mean", "median", "std"],
        "Average Grade Adjusted Pace": "mean",
        "Elevation Gain": "mean",
        "Relative Effort": "mean",
        "Distance": ["mean", "count"]
    })
    
    # Flatten multi-level column names
    route_stats.columns = ['_'.join(col).strip() for col in route_stats.columns]
    return route_stats.reset_index()
