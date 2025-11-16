import pandas as pd

def load_dataframe(path: str) ->pd.DataFrame:
    if path.lower().endswith('.csv'):
        return pd.read_csv(path)
    else:
        return pd.read_excel(path)