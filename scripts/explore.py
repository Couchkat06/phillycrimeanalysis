import pandas as pd
import numpy as np

from pathlib import Path

# directs to scripts folder
SCRIPT_DIR = Path(__file__).resolve().parent 

# directs to main folder and reroutes to data folder, creating a path
DATA_DIR = SCRIPT_DIR.parent / "data"


df = pd.read_csv(DATA_DIR / "crime_2024.csv")
print(df.shape) # outlines rows, columns
print(df.head()) #shows first 5 columns
print(df.columns.tolist()) #all column names

