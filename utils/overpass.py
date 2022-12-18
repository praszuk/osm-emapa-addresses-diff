import requests
import logging

from os import path
from time import sleep
from typing import Any, Dict, Optional

from config import Config
from config import gettext as _


OVERPASS_API_URL = 'https://lz4.overpass-api.de/api/interpreter'
QUERY_ADDR = path.join(Config.ROOT_DIR, 'utils', 'query_addr.overpassql')
QUERY_STREET = path.join(Config.ROOT_DIR, 'utils', 'query_street.overpassql')

TIMEOUT = 30  # seconds
RETRIES = 5


def download_osm_data(
    teryt_terc: str,
    query_filename: str
) -> Optional[Dict[Any, Any]]:
    """
    :param teryt_terc: commune (gmina) id
    all query will use administrative boundary from given value
    :param query_filename: path to query which contain '<teryt_terc>' to replace
    :return: Raw OSM Overpass data JSON (as dict) or None
    """
    with open(query_filename, 'r') as f:
        query = f.read().strip().replace('<teryt_terc>', teryt_terc)

    logging.info(
        _('Loaded Overpass query from file: {}').format(
            path.split(query_filename)[-1]
        )
    )
    logging.info(
        _('Downloading Overpass data for {} area...').format(teryt_terc)
    )

    for _retry in range(RETRIES):
        try:
            response = requests.get(OVERPASS_API_URL, params={'data': query})
            if response.status_code != 200:
                logging.warning(
                    _('Incorrect status code: {}').format(response.status_code)
                )
                continue

            return response.json()

        except Exception as e:
            logging.error(
                _('Error with downloading/parsing data: {}').format(e)
            )

        sleep(TIMEOUT)


def is_element(element) -> bool:
    return 'tags' in element
