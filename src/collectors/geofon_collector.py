import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

end_date = datetime.today().date()
start_date = end_date - timedelta(days=30)

url = "https://geofon.gfz.de/eqinfo/list.php"

params = {
    "datemin": str(start_date),
    "datemax": str(end_date),
    "latmax": 46,
    "latmin": 24,
    "lonmin": 123,
    "lonmax": 146,
    "magmin": "",
    "fmt": "html",
    "nmax": "",
}

response = requests.get(url, params=params)

soup = BeautifulSoup(response.text, "html.parser")

rows = []

event_selector = "a[href*='event.php?id=']"
events = soup.select(event_selector)

for event in events:
    try:
        magnitude_selector = "span[class='magbox']"
        magnitude = event.select_one(magnitude_selector).text.strip()

        info_selector = "div[class='col-xs-12']"
        info = event.select(info_selector)

        coordinate = info[0]["title"].split(",")
        
        longitude = coordinate[0].strip()
        latitude = coordinate[1].strip()

        place = info[0].text.strip()

        time = info[1].contents[0].strip()

        depth_selector = "span[class='pull-right']"
        depth = info[1].select_one(depth_selector).text.strip()

        rows.append(
            {
                "time": time,
                "magnitude": magnitude,
                "depth": depth,
                "latitude": latitude,
                "longitude": longitude,
                "place": place,
                "source": "GEOFON",
            }
        )

    except Exception as error:
        print(f"Error parsing one event: {error}")
        continue

df = pd.DataFrame(rows)

df.to_csv("data/raw/geofon.csv", index=False, encoding="utf-8")
