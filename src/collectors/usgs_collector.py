# Collects earthquake data from USGS API
from datetime import datetime, timedelta

import requests

end_date = datetime.now()
start_date = end_date - timedelta(days=30)

start_date = start_date.strftime("%Y-%m-%d")
end_date = end_date.strftime("%Y-%m-%d")

params = {
    "format": "csv",
    "starttime": start_date,
    "endtime": end_date,
    "minlatitude": 24,
    "maxlatitude": 46,
    "minlongitude": 123,
    "maxlongitude": 146,
    "minmagnitude": 1,
}
res = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query", params=params)

with open("./data/raw/usgs.csv", "w", encoding="utf-8") as file:
    file.write(res.text)
