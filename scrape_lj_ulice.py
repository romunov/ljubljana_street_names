from pathlib import Path
import shelve
import time

import pandas as pd

from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait


def get_street_details(street_list, shelf_file, sleep_time=1):
    empty_dump = {"ime": "NA", "leto": "NA", "obrazlozitev": "NA", "id": "NA"}

    xy = []
    total = len(streets)
    counter = 0
    for street in street_list:
        street_name, street_value = street.values()
        counter += 1

        if not street_value:
            print(f"[SKIP] {street_name} ({counter}/{total})")
            continue
        if street_value in shelf_file:
            print(f"[SHELF] {street_name} ({counter}/{total})")
            xy.append(shelf_file[street_value])
            continue
        else:
            try:
                select_ulica.select_by_value(value=street_value)
                submit_ulica.click()

                res = browser.find_element(By.ID, value="divOstalo")

                ime = res.find_element(By.ID, value="tbUime").text
                leto = res.find_element(By.ID, value="tbLimenovanja").text
                obrazlozitev = res.find_element(By.ID, value="tbOnosilca").text

                dump = {
                    "ime": ime,
                    "leto": leto,
                    "obrazlozitev": obrazlozitev,
                    "id": street_value,
                }

                shelf[street_value] = dump

                print(f"{ime} ({counter}/{total})")
            except UnexpectedAlertPresentException:
                print(f"[FAIL] {street_name} can't be found")
                dump = empty_dump
            except NoSuchElementException:
                print(f"Couldn't find divOstalo element for {street_name}")
                dump = empty_dump
            except StaleElementReferenceException:
                print(f"Page for {street_name} is messed up")
                dump = empty_dump

            xy.append(dump)

            time.sleep(sleep_time)

    return pd.DataFrame(xy)


GECKO_DRIVER = Path("driver", "geckodriver")
DATA_DIR = Path("data")
SHELVE_FILE = DATA_DIR / "shelf_street_names.shl"
FILE_STREETNAMES = DATA_DIR / "street_names.tsv"

DATA_DIR.mkdir(exist_ok=True)

opts = Options()
opts.page_load_strategy = "eager"
opts.headless = True

gecko_service = Service(executable_path=str(GECKO_DRIVER))

browser = Firefox(options=opts, service=gecko_service)
browser.implicitly_wait(time_to_wait=5)

browser.get("https://gis05.ljubljana.si/LjubljanskeUlice/")

# Get a list of streets.
dd_ulica = browser.find_element(By.ID, "ddlUlica")
select_ulica = Select(
    WebDriverWait(browser, 2).until(ec.element_to_be_clickable(dd_ulica))
)

streets = [
    {"name": x.get_attribute("text"), "value": x.get_attribute("value")}
    for x in select_ulica.options
]
streets = streets[1:]  # 1: skips the default "Izberite" input value

# Click the "Ulica dropdown menu" to select a street.
submit_ulica = browser.find_element(by=By.ID, value="imgPrikaziNaKarti")

shelf = shelve.open(filename=str(SHELVE_FILE))
street_details = get_street_details(street_list=streets, shelf_file=shelf)
shelf.close()

street_details.to_csv(path_or_buf=FILE_STREETNAMES, sep="\t", index=False)
print("Script done.")
