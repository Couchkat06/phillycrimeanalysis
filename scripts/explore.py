import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns

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


# %%
df = pd.read_csv(DATA_DIR / "crime_2024.csv")
print(df.shape) # outlines rows, columns
print(df.head()) #shows first 5 columns and rows
print(df.columns.tolist()) #shows all column names

# %%
#prints counts of all types of crime under text_general_code column
print(df["text_general_code"].value_counts())

import glob 

files = list(DATA_DIR.glob("crime_*.csv"))
frames = [] #empty frames list

for file in files: #add each data file into frames list, low memory mode is set to false for accuracy 
    frames.append(pd.read_csv(file, low_memory= False))
df = pd.concat(frames, ignore_index = True) #stacks into one df

print(df.shape)

#parsing dates

#converting column to datetime type
df["dispatch_date_time"] = pd.to_datetime(df["dispatch_date_time"])


df["year"] = df["dispatch_date_time"].dt.year
df["month"] = df["dispatch_date_time"].dt.month
df["hour"] = df["dispatch_date_time"].dt.hour
df["dayofweek"] = df["dispatch_date_time"].dt.dayofweek

print(df.isna().sum()) #count of missing values per column

df.dropna(subset = ["dispatch_date_time"]) #drops rows without datetime
df.dropna(subset = ["text_general_code"]) #drops rows without crime type

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

#analysis & visualization

yearly = df.groupby("year").size()
print(yearly)

yearly_by_type = df.groupby("year", "crime_category").size().unstack()
print(yearly_by_type)

#plotting

fig, ax = plt.subplots(figsize = (10,6))

for category in yearly_by_type.columns:
    ax.plot(yearly_by_type.index, 
            yearly_by_type[category],
            label = category,
            **line_style)
ax.set_title("Philadelphia Crime by Category, 2018-2025")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Incidents")
plt.tight_layout()
plt.savefig("../output/yearly_trends.png", dip = 150)
plt.show()


pivot = df.pivot_table(index = "dayofweek",
                       columns = "hour",
                       values = "crime_category",
                       aggfunc = "count")

fig, ax = plt.subplots(figsize = (14, 6))
sns.heatmap(pivot, cmap = "Y10rRd", ax = ax)
ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], rotation = 0)
ax.set_title("Crime Frequency by Hour and Day of the Week")
ax.set_xlabel("Hour of Day")
plt.tight_layout()
plt.savefig("../output/heatmap.png", dpi = 150)

by_district = df.groupby("dc_dist").size().sort_values(ascending = False)

fig, ax = plt.subplots(figsize = (12, 6))
by_district.plot(kind = "bar", ax = ax)
ax.set_title("Total Incidents by Police District, 2018-2025")
ax.set_xlabel("Districts")
