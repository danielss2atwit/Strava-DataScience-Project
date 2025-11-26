import matplotlib.pyplot as plt
import pandas as pd

def plot_fastest_routes(route_stats, top_n=10):
    if len(route_stats) == 0:
        print("⚠️ No route stats to plot!")
        return
    
    # Sort by lowest pace (fastest = lowest min/mile)
    df_plot = route_stats.sort_values("Pace_min_per_mile_mean", ascending=True).head(top_n)
    
    # Create meaningful labels: show distance and count
    labels = [f"Route {int(row['RouteID'])}\n({row['Distance_mean']:.1f}mi, {int(row['Distance_count'])} runs)" 
              for _, row in df_plot.iterrows()]

    plt.figure(figsize=(12, 6))
    plt.bar(range(len(df_plot)), df_plot["Pace_min_per_mile_mean"], color='skyblue')
    plt.xlabel("Route")
    plt.ylabel("Pace (min/mile)")
    plt.title(f"Top {top_n} Fastest Routes (by GPS similarity)")
    
    # Scale y-axis to start near the minimum value to see differences better
    min_pace = df_plot["Pace_min_per_mile_mean"].min()
    max_pace = df_plot["Pace_min_per_mile_mean"].max()
    y_margin = (max_pace - min_pace) * 0.1  # Add 10% margin
    plt.ylim(min_pace - y_margin, max_pace + y_margin)
    
    # Format y-axis as MM:SS (e.g., 7:45, 9:15)
    def pace_formatter(x, pos):
        minutes = int(x)
        seconds = int((x - minutes) * 60)
        return f"{minutes}:{seconds:02d}"
    
    from matplotlib.ticker import FuncFormatter
    plt.gca().yaxis.set_major_formatter(FuncFormatter(pace_formatter))
    
    plt.xticks(range(len(df_plot)), labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def plot_hardest_routes(route_stats, top_n=10):
    if len(route_stats) == 0:
        print("⚠️ No route stats to plot!")
        return
    
    # Sort by elevation gain descending
    df_plot = route_stats.sort_values("Elevation Gain_mean", ascending=False).head(top_n)
    
    # Create meaningful labels: show distance and count
    labels = [f"Route {int(row['RouteID'])}\n({row['Distance_mean']:.1f}mi, {int(row['Distance_count'])} runs)" 
              for _, row in df_plot.iterrows()]

    plt.figure(figsize=(12, 6))
    plt.bar(range(len(df_plot)), df_plot["Elevation Gain_mean"], color='salmon')
    plt.xlabel("Route")
    plt.ylabel("Elevation Gain (meters)")
    plt.title(f"Top {top_n} Hardest Routes (by GPS similarity)")
    plt.xticks(range(len(df_plot)), labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def plot_most_consistent_routes(route_stats, top_n=10):
    if len(route_stats) == 0:
        print("⚠️ No route stats to plot!")
        return
    
    df_plot = route_stats.sort_values("Pace_min_per_mile_std", ascending=True).head(top_n)
    
    # Create meaningful labels: show distance and count
    labels = [f"Route {int(row['RouteID'])}\n({row['Distance_mean']:.1f}mi, {int(row['Distance_count'])} runs)" 
              for _, row in df_plot.iterrows()]

    plt.figure(figsize=(12, 6))
    plt.bar(range(len(df_plot)), df_plot["Pace_min_per_mile_std"], color='lightgreen')
    plt.xlabel("Route")
    plt.ylabel("Pace Variability (std dev in min/mile)")
    plt.title(f"Top {top_n} Most Consistent Routes (by GPS similarity)")
    plt.xticks(range(len(df_plot)), labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.show()