# Cleans/transforms USGS data

import pandas as pd

data_usgs = pd.read_csv("./data/raw/usgs.csv")

data_usgs = data_usgs[
    [
        "time",
        "latitude",
        "longitude",
        "depth",
        "mag",
        "place",
    ]
]

data_usgs["source"] = "USGS"
data_usgs.dropna(inplace=True)
data_usgs.drop_duplicates(inplace=True)
data_usgs.to_csv("./data/processed/JAPAN_USGS.csv", index=False)
