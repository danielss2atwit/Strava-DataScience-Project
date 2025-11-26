from src.load_data import load_strava
from src.clean_data import clean
from src.route_analysis import compute_route_stats
from src.plots import plot_fastest_routes, plot_hardest_routes, plot_most_consistent_routes
from src.load_gps import load_gps_from_folder, resample_track, vectorize_gps_track

import numpy as np
from sklearn.cluster import DBSCAN
import pandas as pd

# --------------------------------------------------------
# 1. Load + clean the CSV data
# --------------------------------------------------------
df = load_strava()
df_clean = clean(df)

# --------------------------------------------------------
# 2. Load and cluster GPS routes
# --------------------------------------------------------
gps_raw = load_gps_from_folder("data/activities/activities")
print("GPS files loaded:", len(gps_raw))

if len(gps_raw) == 0:
    raise ValueError("No GPS tracks found! Check the 'data/activities' folder and GPX files.")

vectors = []
ids = []

for filename, gpx in gps_raw.items():
    try:
        if not gpx.tracks:
            continue
        # Combine all points from all segments of the first track
        coords = []
        for segment in gpx.tracks[0].segments:
            coords.extend([(p.latitude, p.longitude) for p in segment.points])
        
        if len(coords) < 2:  # Skip tracks with too few points
            continue
            
        r = resample_track(coords, n_points=100)
        v = vectorize_gps_track(r)
        vectors.append(v)
        ids.append(filename)
    except Exception as e:
        print(f"⚠️ Skipping {filename} due to error: {e}")
        continue

print(f"Successfully vectorized {len(vectors)} GPS tracks")

if len(vectors) == 0:
    raise ValueError("No valid GPS tracks were vectorized!")

vectors = np.array(vectors)

# FIX: Adjusted DBSCAN parameters for better clustering
# Start with more lenient parameters to capture more routes
labels = DBSCAN(eps=0.015, min_samples=1).fit(vectors).labels_

n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise = np.sum(labels == -1)
print(f"DBSCAN found {n_clusters} clusters")
print(f"Noise points: {n_noise}")

# If too many noise points, try different parameters
if n_noise / len(labels) > 0.5:
    print("⚠️ High noise ratio detected. Retrying with more lenient parameters...")
    labels = DBSCAN(eps=0.02, min_samples=1).fit(vectors).labels_
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = np.sum(labels == -1)
    print(f"Retried: {n_clusters} clusters, {n_noise} noise points")

# Make a dictionary: filename → cluster ID
route_map = dict(zip(ids, labels))

# --------------------------------------------------------
# 3. Merge GPS cluster IDs into df_clean
# --------------------------------------------------------
# DEBUG: Check what filenames look like
print("\n--- GPS Filename Examples (first 5) ---")
for fname in list(route_map.keys())[:5]:
    print(f"  GPS: {fname}")

print("\n--- Activity ID/Filename Examples (first 5) ---")
if "Activity ID" in df_clean.columns:
    print("Using Activity ID:")
    for aid in df_clean["Activity ID"].head().values:
        print(f"  CSV: {aid}")
else:
    print("Using Filename:")
    for fname in df_clean["Filename"].head().values:
        print(f"  CSV: {fname}")

def get_route_id(key):
    if key is None or (isinstance(key, float) and np.isnan(key)):
        return np.nan
    
    key_str = str(key).strip()
    
    # Strategy 1: Try exact match (e.g., "8083971283.gpx")
    if key_str in route_map:
        rid = route_map[key_str]
        return int(rid) if isinstance(rid, (int, np.integer)) else int(rid[0])
    
    # Strategy 2: Try with .gpx extension (e.g., Activity ID "8083971283" → "8083971283.gpx")
    key_with_gpx = f"{key_str}.gpx"
    if key_with_gpx in route_map:
        rid = route_map[key_with_gpx]
        return int(rid) if isinstance(rid, (int, np.integer)) else int(rid[0])
    
    # Strategy 3: Try removing path if present (e.g., "activities/8083971283.gpx" → "8083971283.gpx")
    import os
    key_basename = os.path.basename(key_str)
    if key_basename in route_map:
        rid = route_map[key_basename]
        return int(rid) if isinstance(rid, (int, np.integer)) else int(rid[0])
    
    # Strategy 4: Search for Activity ID as substring in route_map keys
    for filename, rid in route_map.items():
        if key_str in filename:
            return int(rid) if isinstance(rid, (int, np.integer)) else int(rid[0])
    
    return np.nan

# Prefer Activity ID for matching, fall back to Filename
if "Activity ID" in df_clean.columns:
    print("\n🔍 Attempting to match using Activity ID...")
    df_clean["GPS_RouteID"] = df_clean["Activity ID"].apply(get_route_id)
else:
    print("\n🔍 Attempting to match using Filename...")
    df_clean["GPS_RouteID"] = df_clean["Filename"].apply(get_route_id)

# --------------------------------------------------------
# 4. Filter activities that did not get clustered
# --------------------------------------------------------
matched = df_clean["GPS_RouteID"].notna().sum()
print(f"\n✓ Matched activities: {matched} out of {len(df_clean)}")

if matched == 0:
    print("\n⚠️ WARNING: No activities matched GPS files!")
    print("This likely means the Activity ID/Filename format doesn't match the GPX filenames.")
    print("\nTip: Check if your CSV has 'Activity ID' or 'Filename' column")
    print("and ensure it matches the GPX filename format exactly.")

df_clustered = df_clean.dropna(subset=["GPS_RouteID"]).copy()
df_clustered["GPS_RouteID"] = df_clustered["GPS_RouteID"].astype(int)
# Remove noise points (label -1 from DBSCAN)
df_clustered = df_clustered[df_clustered["GPS_RouteID"] != -1].copy()

print(f"Activities with valid GPS clusters: {len(df_clustered)} out of {len(df_clean)}")

# --------------------------------------------------------
# 5. Recompute route stats using GPS_RouteID
# --------------------------------------------------------
if len(df_clustered) == 0:
    print("\n❌ No clustered activities to analyze. Exiting early.")
    print("Check the filename matching above.")
else:
    # Ensure RouteID is a simple integer column
    df_for_stats = df_clustered.copy()
    df_for_stats["RouteID"] = df_for_stats["GPS_RouteID"].astype(int)
    
    print(f"\nRouteID dtype: {df_for_stats['RouteID'].dtype}")
    print(f"Unique routes: {df_for_stats['RouteID'].nunique()}")
    print(f"DataFrame shape: {df_for_stats.shape}")
    print(f"Sample RouteIDs: {df_for_stats['RouteID'].head().tolist()}")

    route_stats = compute_route_stats(df_for_stats)
    print(f"\n✓ Route stats computed for {len(route_stats)} routes:")
    print(route_stats.head())

    # --------------------------------------------------------
    # 6. Plot route performance
    # --------------------------------------------------------
    plot_fastest_routes(route_stats)
    plot_hardest_routes(route_stats)
    plot_most_consistent_routes(route_stats)

    # --------------------------------------------------------
    # 7. Export cleaned + clustered data
    # --------------------------------------------------------
    df_clean.to_csv("data/cleaned_strava_with_gps.csv", index=False)
    route_stats.to_csv("data/route_stats_gps.csv", index=False)

    print("✅ Export complete!")