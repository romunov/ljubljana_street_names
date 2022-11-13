"""
This script download the geckodriver needed for selenium.
If you already have this locally, feel free to skip this
script.
"""
import os
from pathlib import Path
import tarfile

import requests

url = "https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz"

gecko_gz = Path("driver", os.path.basename(url))
geckodriver = gecko_gz.stem

response = requests.get(url)

gecko_gz.write_bytes(data=response.content)

with tarfile.open(gecko_gz) as tar:
    tar.extractall("driver")

gecko_gz.unlink()
