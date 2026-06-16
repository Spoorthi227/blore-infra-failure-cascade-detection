import pandas as pd

try:
    df = pd.read_excel('d:/urban_el/power_with_location.xlsx')
    print("Columns:", df.columns.tolist())
    print("Head:")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
