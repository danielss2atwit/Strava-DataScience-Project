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

def extract_coordinates(gpx):
    """
    Extract all coordinates from a GPX file.
    Returns list of (lat, lon) tuples.
    """
    coords = []
    if gpx.tracks:
        for segment in gpx.tracks[0].segments:
            coords.extend([(p.latitude, p.longitude) for p in segment.points])
    return coords

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

def get_route_centroids(gps_data, route_ids, labels):
    """
    Calculate the center point (centroid) for each route cluster.
    
    Args:
        gps_data: dict of {filename: gpx object}
        route_ids: list of filenames that were vectorized
        labels: cluster labels from DBSCAN
    
    Returns:
        dict: {cluster_id: (center_lat, center_lon)}
    """
    route_centroids = {}
    
    # Group filenames by cluster label
    cluster_map = {}
    for filename, label in zip(route_ids, labels):
        if label == -1:  # Skip noise
            continue
        if label not in cluster_map:
            cluster_map[label] = []
        cluster_map[label].append(filename)
    
    # Calculate centroid for each cluster
    for cluster_id, filenames in cluster_map.items():
        all_coords = []
        for filename in filenames:
            if filename in gps_data:
                coords = extract_coordinates(gps_data[filename])
                all_coords.extend(coords)
        
        if all_coords:
            coords_array = np.array(all_coords)
            center_lat = coords_array[:, 0].mean()
            center_lon = coords_array[:, 1].mean()
            route_centroids[cluster_id] = (center_lat, center_lon)
    
    return route_centroids

def get_location_name(lat, lon):
    """
    Get the location name from coordinates using reverse geocoding.
    Uses geopy with OpenStreetMap (free, no API key needed).
    """
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="strava_analyzer")
        location = geolocator.reverse(f"{lat}, {lon}", language='en', timeout=5)
        
        # Extract useful parts of the address
        address_parts = location.address.split(', ')
        
        # Try to get neighborhood/area name and city
        if len(address_parts) >= 2:
            area = address_parts[1] if len(address_parts) > 1 else address_parts[0]
            city = address_parts[2] if len(address_parts) > 2 else ""
            return f"{area}, {city}".strip(", ")
        else:
            return address_parts[0] if address_parts else "Unknown Location"
    except Exception as e:
        return "Unknown Location"