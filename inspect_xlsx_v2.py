import sys
import pandas as pd
print("Script started", flush=True)
try:
    df = pd.read_excel('d:/urban_el/power_with_location.xlsx')
    print("Columns:", df.columns.tolist(), flush=True)
    print(df.head(), flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
