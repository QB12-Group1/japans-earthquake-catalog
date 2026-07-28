import re
import pandas as pd 
from datetime import datetime


raw_rows = pd.read_csv("data/raw/geofon.csv")
raw_rows = raw_rows.to_dict("records")

processed_rows = []

for row in raw_rows:
    try:
        longitude = float(row["longitude"].replace("°E", "").strip())
        latitude = float(row["latitude"].replace("°N", "").strip())

        depth = re.search(r"\d+", row["depth"]).group()
        
        time = datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S.%f").strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        processed_rows.append({
            "time": time ,
            "mag": row["magnitude"],
            "depth": depth,
            "latitude": latitude,
            "longitude": longitude,
            "place": row["place"],
            "source": "GEOFON",
        })
    except Exception as error:
        print(f"Error processing event : {error}")
        continue

df_processed = pd.DataFrame(processed_rows)
df_processed.to_csv("data/processed/geofon.csv", index=False, encoding="utf-8")
