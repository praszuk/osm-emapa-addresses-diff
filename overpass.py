import requests

from time import sleep
from typing import Any, Dict, Optional

import logging


OVERPASS_API_URL = 'https://lz4.overpass-api.de/api/interpreter'
QUERY_FILE = 'query.overpassql'

TIMEOUT = 30  # seconds
RETRIES = 5


def download_osm_data() -> Optional[Dict[Any, Any]]:
    with open(QUERY_FILE, 'r') as f:
        query = f.read().strip()

    logging.info(f'Read overpass query from file: {QUERY_FILE}')
    logging.info(f'Downloading overpass data...')

    for _ in range(RETRIES):
        try:
            response = requests.get(OVERPASS_API_URL, params={'data': query})
            if response.status_code != 200:
                logging.warning(
                    f'Incorrect status code: {response.status_code}'
                )
                continue

            return response.json()

        except Exception as e:
            logging.error(f'Error with downloading/parsing data: {e}')

        sleep(TIMEOUT)


def is_element(element) -> bool:
    return 'tags' in element
