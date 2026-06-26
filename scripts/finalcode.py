import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from pathlib import Path

#paths

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

#styles
title_style = dict(fontsize=16, 
                   family="Helvetica", 
                   fontweight="bold", 
                   color="#0b1c36")
label_style = dict(fontsize=12, 
                   family="Helvetica", 
                   fontweight="bold", 
                   color="#0b1c36")
line_style  = dict(marker="*", 
                   markersize=12, 
                   linestyle="dotted", 
                   linewidth=2)

BAR_FILL, BAR_EDGE, TICK_COLOR = "#a0cedb", "#a0cedb", "#0b1c36"

def simplify_crime_type(data):
    data = str(data).lower()
    if "theft" in data or "burglary" in data or "robbery" in data or "stolen" in data:
        return "Theft/Robbery"
    elif "assault" in data:
        return "Assault"
    elif "homicide" in data:
        return "Homicide"
    elif "rape" in data or "sex" in data or "prostitution" in data:
        return "Sex Offense"
    else:
        return "Other"

def load_data(data_dir):
    files = list(Path(data_dir).glob("crime_*.csv"))
    frames = [pd.read_csv(f, low_memory=False) for f in files]
    return pd.concat(frames, ignore_index=True)

def clean_data(df):
    df["dispatch_date_time"] = pd.to_datetime(df["dispatch_date_time"])
    df = df.dropna(subset=["dispatch_date_time", "text_general_code"])
    df["year"]      = df["dispatch_date_time"].dt.year
    df["month"]     = df["dispatch_date_time"].dt.month
    df["hour"]      = df["dispatch_date_time"].dt.hour
    df["dayofweek"] = df["dispatch_date_time"].dt.dayofweek
    df["crime_category"] = df["text_general_code"].apply(simplify_crime_type)
    return df


def build_dashboard(df, output_path):
    yearly_by_type = df.groupby(["year", "crime_category"]).size().unstack()
    by_district = df.groupby("dc_dist").size().sort_values(ascending=False)
    monthly = df.groupby("month").size()
    pivot = df.pivot_table(index="dayofweek", 
                           columns="hour",
                           values="crime_category", 
                           aggfunc="count")

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))

    #top left- yearly trends
    for category in yearly_by_type.columns: 
        axes[0,0].plot(yearly_by_type.index, yearly_by_type[category],
                   label = category, **line_style)
    
    axes[0,0].set_title("Crime by Category Over Time", **title_style)
    axes[0,0].tick_params(axis = "both", colors = TICK_COLOR)
    axes[0,0].legend()

    #top right- by district
    axes[0,1].bar(by_district.index.astype(str), by_district.values,
                color = BAR_FILL, edgecolor = BAR_EDGE, linewidth = 1.5)
    axes[0,1].set_title("Incidents by District", **title_style)
    axes[0,1].tick_params(axis = "both", colors = TICK_COLOR)

    #bottom left- seasonal
    axes[1,0].bar(monthly.index, monthly.values,
                color = BAR_FILL, edgecolor = BAR_EDGE, linewidth = 2)
    axes[1,0].set_title("Seasonal Pattern", **title_style)
    axes[1,0].tick_params(axis = "both", colors = TICK_COLOR)

    #bottom right- heatmap
    sns.heatmap(pivot, cmap= "YlOrRd", ax = axes[1, 1])
    axes[1,1].set_title("Hour x Day Heatmap", **title_style)
    axes[1,1].tick_params(axis = "both", colors = TICK_COLOR)

    fig.suptitle("Philadelphia Crime Dashboard",
                 family = "Helvetica", fontsize = 30, fontweight = "bold", color = "#0b1c36")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 150)
    plt.close(fig)


if __name__ == "__main__":
    df = load_data(DATA_DIR)
    df = clean_data(df)
    build_dashboard(df, OUTPUT_DIR / "dashboard.png")
    print("Dashboard saved to", OUTPUT_DIR / "dashboard.png")