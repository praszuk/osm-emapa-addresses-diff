import requests
import logging

from os import path
from time import sleep
from typing import Any, Dict, Optional

from config import ROOT_DIR

OVERPASS_API_URL = 'https://lz4.overpass-api.de/api/interpreter'
QUERY_FILE = path.join(ROOT_DIR, 'utils', 'query.overpassql')

TIMEOUT = 30  # seconds
RETRIES = 5


def download_osm_data(teryt_terc: str) -> Optional[Dict[Any, Any]]:
    """
    :param teryt_terc: commune (gmina) id
    all query will use administrative boundary from given value
    :return: Raw OSM Overpass data JSON (as dict) or None
    """
    with open(QUERY_FILE, 'r') as f:
        query = f.read().strip().replace('<teryt_terc>', teryt_terc)

    logging.info(f'Read overpass query from file: {QUERY_FILE}')
    logging.info(f'Downloading overpass data for {teryt_terc} area...')

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
