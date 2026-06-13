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
