import csv
import os
import shutil
import time
from datetime import UTC, datetime, timedelta

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

MIN_LAT = 24
MAX_LAT = 46
MIN_LON = 123
MAX_LON = 146
MIN_MAG = 1

END_DATE = datetime.now(UTC)
START_DATE = END_DATE - timedelta(days=30)

BASE_URL = "https://www.emsc.eu/Earthquake_information/"
OUTPUT_FILE = "data/raw/emsc.csv"


def build_driver(headless: bool = True):
    options = Options()
    if headless:
        options.add_argument("-headless")
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    )

    driver_path = os.environ.get("GECKODRIVER_PATH") or shutil.which("geckodriver")
    if driver_path:
        driver = webdriver.Firefox(
            service=Service(executable_path=driver_path), options=options
        )
    else:
        driver = webdriver.Firefox(options=options)

    driver.set_page_load_timeout(60)
    return driver


def open_search_panel(driver, wait):
    toggle = wait.until(
        ec.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'Search earthquakes')]")
        )
    )
    toggle.click()
    time.sleep(1)


def set_field(driver, possible_name_parts, value):
    for part in possible_name_parts:
        for attr in ("name", "id"):
            try:
                el = driver.find_element(
                    By.XPATH, f"//input[contains(@{attr}, '{part}')]"
                )
                driver.execute_script(
                    "arguments[0].value = arguments[1];"
                    "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                    "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                    el,
                    str(value),
                )
                return True
            except NoSuchElementException:
                continue
    return False


def debug_list_inputs(driver):
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"Found {len(inputs)} <input> elements on the page:")
    for el in inputs:
        try:
            print(
                "  name={!r} id={!r} type={!r} placeholder={!r}".format(
                    el.get_attribute("name"),
                    el.get_attribute("id"),
                    el.get_attribute("type"),
                    el.get_attribute("placeholder"),
                )
            )
        except Exception:
            continue


def fill_search_form(driver, wait):
    date_ok_start = set_field(driver, ["datemin"], START_DATE.strftime("%Y-%m-%d"))
    date_ok_end = set_field(driver, ["datemax"], END_DATE.strftime("%Y-%m-%d"))
    if not (date_ok_start and date_ok_end):
        print(
            "WARNING: date range field not found; please inspect the page and update the field names."
        )
        debug_list_inputs(driver)

    set_field(driver, ["latmin"], MIN_LAT)
    set_field(driver, ["latmax"], MAX_LAT)
    set_field(driver, ["lonmin"], MIN_LON)
    set_field(driver, ["lonmax"], MAX_LON)
    set_field(driver, ["magmin"], MIN_MAG)

    try:
        submit_btn = driver.find_element(
            By.XPATH,
            "//input[@type='submit'] | //button[contains(text(),'Search') "
            "or contains(text(),'Filter') or contains(text(),'Send')]",
        )
        driver.execute_script("arguments[0].click();", submit_btn)
    except NoSuchElementException:
        print(
            "WARNING: submit button not found; the filter may apply automatically on change."
        )

    time.sleep(2)


def wait_for_results_table(driver, wait):
    table = wait.until(
        ec.presence_of_element_located(
            (By.XPATH, "//table[.//th[contains(text(),'Date')]]")
        )
    )
    wait.until(lambda d: len(table.find_elements(By.XPATH, ".//tbody/tr")) > 0)
    return table


def parse_rows(table):
    rows_data = []
    header_cells = table.find_elements(By.XPATH, ".//thead//th")
    headers = [h.text.strip() for h in header_cells] if header_cells else None

    rows = table.find_elements(By.XPATH, ".//tbody/tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        texts = [c.text.strip() for c in cells]
        rows_data.append(texts)

    return headers, rows_data


def get_page_data(driver, wait, max_attempts=5):
    for attempt in range(1, max_attempts + 1):
        try:
            table = wait_for_results_table(driver, wait)
            return parse_rows(table)
        except StaleElementReferenceException:
            print(
                f"Table changed while reading (attempt {attempt}/{max_attempts}); retrying..."
            )
            time.sleep(1)
    raise StaleElementReferenceException(
        "Table kept changing while reading; gave up after max attempts."
    )


def go_to_next_page(driver, next_page_number):
    xpaths = [
        f"//div[contains(concat(' ', normalize-space(@class), ' '), ' pag ')]"
        f"[not(contains(@class,'selview'))][normalize-space(text())='{next_page_number}']",
        f"//*[not(ancestor::table)][normalize-space(text())='{next_page_number}']",
    ]
    for xpath in xpaths:
        for el in driver.find_elements(By.XPATH, xpath):
            try:
                if not el.is_displayed():
                    continue
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", el
                )
                driver.execute_script("arguments[0].click();", el)
                time.sleep(2)
                return True
            except StaleElementReferenceException:
                continue
    return False


def scrape():
    driver = build_driver(headless=True)
    wait = WebDriverWait(driver, 20)
    all_rows = []
    headers = None

    try:
        driver.get(BASE_URL)
        open_search_panel(driver, wait)
        fill_search_form(driver, wait)

        page = 1
        while True:
            print(f"Extracting page {page} ...")
            try:
                page_headers, page_rows = get_page_data(driver, wait)
            except TimeoutException:
                print("Results table not found; stopping.")
                break
            except StaleElementReferenceException as e:
                print(f"Giving up on page {page}: {e}")
                break

            if headers is None:
                headers = page_headers

            all_rows.extend(page_rows)
            print(
                f"  -> {len(page_rows)} rows on this page (running total: {len(all_rows)})"
            )

            if not go_to_next_page(driver, page + 1):
                print(f"No page {page + 1} found; assuming this was the last page.")
                break
            page += 1

    finally:
        driver.quit()

    return headers, all_rows


def save_to_csv(headers, rows, filename=OUTPUT_FILE):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
    print(f"Saved {len(rows)} raw records to {filename}")


if __name__ == "__main__":
    headers, data = scrape()
    save_to_csv(headers, data)
