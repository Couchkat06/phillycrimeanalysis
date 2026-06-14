import pandas as pd
import numpy as np

from pathlib import Path

# directs to scripts folder
SCRIPT_DIR = Path(__file__).resolve().parent 

# directs to main folder and reroutes to data folder, creating a path
DATA_DIR = SCRIPT_DIR.parent / "data"

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

