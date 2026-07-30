from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup


def extract_raw() -> pd.DataFrame:
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

    rows = []

    while True:
        response = requests.get(url, params=params, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        event_selector = "a[href*='event.php?id=']"
        events = soup.select(event_selector)

        for event in events:
            try:
                magnitude_selector = "span[class='magbox']"
                magnitude_element = event.select_one(magnitude_selector)

                if magnitude_element is None:
                    raise ValueError("Magnitude element not found.")

                magnitude = magnitude_element.text.strip()

                info_selector = "div[class='col-xs-12']"
                info = event.select(info_selector)

                title = str(info[0]["title"])

                coordinate = title.split(",")

                longitude = coordinate[0].strip()
                latitude = coordinate[1].strip()

                place = info[0].text.strip()

                time = str(info[1].contents[0])

                time = time.strip()

                depth_selector = "span[class='pull-right']"
                depth_element = info[1].select_one(depth_selector)

                if depth_element is None:
                    raise ValueError("Depth element not found.")

                depth = depth_element.text.strip()

                rows.append(
                    {
                        "time": time,
                        "latitude": latitude,
                        "longitude": longitude,
                        "depth": depth,
                        "mag": magnitude,
                        "place": place,
                    }
                )

            except Exception as error:
                print(f"Error parsing one event: {error}")
                continue

        link = soup.select_one("span.pull-left a")
        if not link:
            break
        url = "https://geofon.gfz.de/eqinfo/" + str(link["href"])
        params = {}

    return pd.DataFrame(rows)


def export_raw() -> None:
    file_path = "data/raw/geofon.csv"
    df = extract_raw()
    df.to_csv(file_path, index=False, encoding="utf-8")


def load_raw() -> pd.DataFrame:
    file_path = "data/raw/geofon.csv"

    try:
        return pd.read_csv(file_path, encoding="utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Dataset file not found: '{file_path}'.") from e
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"Dataset file is empty: '{file_path}'.") from e
    except pd.errors.ParserError as e:
        raise ValueError(
            f"Dataset file could not be parsed as CSV: '{file_path}'."
        ) from e
