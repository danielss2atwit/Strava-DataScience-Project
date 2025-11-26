import matplotlib.pyplot as plt
import pandas as pd

def plot_fastest_routes(route_stats, top_n=10):
    if len(route_stats) == 0:
        print("⚠️ No route stats to plot!")
        return
    
    df_plot = route_stats.sort_values("Average Speed_mean", ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.bar(df_plot["RouteID"].astype(str), df_plot["Average Speed_mean"], color='skyblue')
    plt.xlabel("Route Cluster")
    plt.ylabel("Average Speed (m/s)")
    plt.title(f"Top {top_n} Fastest Routes (GPS Clusters)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_hardest_routes(route_stats, top_n=10):
    if len(route_stats) == 0:
        print("⚠️ No route stats to plot!")
        return
    
    df_plot = route_stats.sort_values("Elevation Gain_mean", ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.bar(df_plot["RouteID"].astype(str), df_plot["Elevation Gain_mean"], color='salmon')
    plt.xlabel("Route Cluster")
    plt.ylabel("Elevation Gain (meters)")
    plt.title(f"Top {top_n} Hardest Routes (GPS Clusters)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_most_consistent_routes(route_stats, top_n=10):
    if len(route_stats) == 0:
        print("⚠️ No route stats to plot!")
        return
    
    df_plot = route_stats.sort_values("Average Speed_std", ascending=True).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.bar(df_plot["RouteID"].astype(str), df_plot["Average Speed_std"], color='lightgreen')
    plt.xlabel("Route Cluster")
    plt.ylabel("Speed Standard Deviation (m/s)")
    plt.title(f"Top {top_n} Most Consistent Routes (GPS Clusters)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
