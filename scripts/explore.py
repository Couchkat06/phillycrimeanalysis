import sys
print(sys.executable)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob 
from pathlib import Path

# directs to scripts folder
SCRIPT_DIR = Path(__file__).resolve().parent 

# directs to main folder and reroutes to data folder, creating a path
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

#text styling
title_style = dict(fontsize = 25,
                   family = "Arial",
                   fontweight = "bold",
                   color = "#2d4cfc")

label_style = dict(fontsize = 20,
                   family = "Arial",
                   fontweight = "bold",
                   color = "#2dbefc")

TICK_COLOR = "#2dbefc"

#line styling 
line_style = dict(marker = "*", 
                  markersize = 12, 
                  linestyle = "dotted",
                  linewidth = 2)

#bar styling
BAR_FILL = "#1cd3fc"
BAR_EDGE = "#1c5bfc"


# %%
df = pd.read_csv(DATA_DIR / "crime_2024.csv")
print(df.shape) # outlines rows, columns
print(df.head()) #shows first 5 columns and rows
print(df.columns.tolist()) #shows all column names

# %%
#prints counts of all types of crime under text_general_code column
print(df["text_general_code"].value_counts())

# %%
files = list(DATA_DIR.glob("crime_*.csv"))
frames = [] #empty frames list

for file in files: #add each data file into frames list, low memory mode is set to false for accuracy 
    frames.append(pd.read_csv(file, low_memory= False))
df = pd.concat(frames, ignore_index = True) #stacks into one df

print(df.shape)

# %%
#parsing dates

#converting column to datetime type
df["dispatch_date_time"] = pd.to_datetime(df["dispatch_date_time"])


df["year"] = df["dispatch_date_time"].dt.year
df["month"] = df["dispatch_date_time"].dt.month
df["hour"] = df["dispatch_date_time"].dt.hour
df["dayofweek"] = df["dispatch_date_time"].dt.dayofweek

# %%
print(df.isna().sum()) #count of missing values per column

df.dropna(subset = ["dispatch_date_time"]) #drops rows without datetime
df.dropna(subset = ["text_general_code"]) #drops rows without crime type

# %%
#simplifying crime categories

print(df["text_general_code"].value_counts())

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
    
df["crime_category"] = df["text_general_code"].apply(simplify_crime_type)
print(df["crime_category"].value_counts())

# %% 
#analysis & visualization

yearly = df.groupby("year").size()
print(yearly)

yearly_by_type = df.groupby(["year", "crime_category"]).size().unstack()
print(yearly_by_type)

#plotting

# %% 
#yearly trends line chart

fig, ax = plt.subplots(figsize = (10,6))

for category in yearly_by_type.columns:
    ax.plot(yearly_by_type.index, 
            yearly_by_type[category],
            label = category,
            **line_style)
ax.set_title("Philadelphia Crime by Category, 2018-2025", **title_style)
ax.set_xlabel("Year", **label_style)
ax.set_ylabel("Number of Incidents", **label_style)
ax.tick_params(axis = "both", colors = TICK_COLOR)
ax.set_xticks(yearly_by_type.index)
ax.legend()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "yearly_trends.png", dpi = 150)
plt.show()

# %%
#Hour x Day crime heatmap

pivot = df.pivot_table(index = "dayofweek",
                       columns = "hour",
                       values = "crime_category",
                       aggfunc = "count")

fig, ax = plt.subplots(figsize = (14, 6))
sns.heatmap(pivot, cmap = "Yl0rRd", ax = ax)
ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], rotation = 0)
ax.set_title("Crime Frequency by Hour and Day of the Week", **title_style)
ax.set_xlabel("Hour of Day", **label_style)
ax.set_ylabel("Day of Week", **label_style)
ax.tick_params(axis = "both", colors = TICK_COLOR)

plt.tight_layout()
plt.savefig("../output/heatmap.png", dpi = 150)
plt.show()

# %% 

by_district = df.groupby("dc_dist").size().sort_values(ascending = False)

fig, ax = plt.subplots(figsize = (12, 6))
ax.bar(by_district.index.astype(str), by_district.values,
       color = BAR_FILL, edgecolor = BAR_EDGE, linewidth = 1.5)

ax.set_title("Total Incidents by Police District, 2018-2025", **title_style)
ax.set_xlabel("Districts", **label_style)
ax.set_ylabel("Number of Incidents", **label_style)
ax.tick_params(axis = "both", colors = TICK_COLOR)

plt.tight_layout()
plt.savefig(OUTPUT_DIR/ "by_district.png", dpi = 150)
plt.show()

# %% 
first_year = df[df["year"] == 2018].groupby("dc_dist").size()
last_year = df[df["year"] == 2025].groupby("dc_dist").size()
pct_change = ((last_year - first_year)/first_year * 100).sort_values()
print(pct_change)

# %% 
monthly = df.grouby("month").size()
fig, ax = plt.subplots(figsize = (10,6))
ax.bar(monthly.index, monthly.values, 
       color = BAR_FILL, edgecolr = BAR_EDGE, linewidth = 2)

ax.set_title("Incidents by Month", **title_style)
ax.set_xlabel("Month", **label_style)
ax.set_ylabel("Number of Incidents", **label_style)
ax.tick_params(axis = "both", colors = TICK_COLOR)
ax.set_xticks(range(1, 13))

plt.tight_layout()
plt.savefig(OUTPUT_DIR/ "seasonal.png", dpi = 150)
plt.show()

# %% 
#combining dashboard

fig, axes = plt.subplots(2, 2, figsize = (18, 12))

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
axes[0,1].tickparams(axis = "both", colors = TICK_COLOR)

#bottom left- seasonal
axes[1,0].bar(monthly.index, monthly.values,
              color = BAR_FILL, edgecolor = BAR_EDGE, linewidth = 2)
axes[1,0].set_title("Seasonal Pattern", **title_style)
axes[1,0].tick_params(axis = "both", colors = TICK_COLOR)

#bottom right- heatmap
sns.heatmap(pivot, cmap= "Yl0rRd", ax = axes[1, 1])
axes[1,1].set_title("Hour x Day Heatmap", **title_style)
axes[1,1].tick_params(axis = "both", colors = TICK_COLOR)

fig.suptitle("Philadelphia Crime Dashboard (2018-2025)",
             fontsize = 30, fontweight = "bold", color = "#2d4cfc")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "dashboard.png", dpi = 150)
plt.show()

