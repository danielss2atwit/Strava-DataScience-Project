import pandas as pd

def load_strava(path="data/activities.csv"):
    return pd.read_csv(path)