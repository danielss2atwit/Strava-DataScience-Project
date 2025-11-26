# ---- src/load_gps.py (FIXED) ----
import os
import gpxpy
import numpy as np

def load_gps_from_folder(folder_path):
    """
    Loads all GPX files in a folder and returns a dictionary:
    {filename: gpxpy object}
    Skips files that fail to parse.
    """
    gps_data = {}

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".gpx"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    gpx = gpxpy.parse(f)
                    gps_data[filename] = gpx
            except Exception as e:
                print(f"⚠️ Skipping file {filename} due to parse error: {e}")

    print(f"✅ Loaded {len(gps_data)} GPX files from {folder_path}")
    return gps_data

def resample_track(coords, n_points=100):
    """
    Resample a GPS track to a fixed number of points.
    coords: list of (lat, lon) tuples
    """
    coords = np.array(coords)
    if len(coords) < 2:
        return coords
    idx = np.linspace(0, len(coords) - 1, n_points).astype(int)
    return coords[idx]

def vectorize_gps_track(coords):
    """
    Flatten the resampled coordinates to a vector for clustering.
    """
    return np.array(coords).flatten()