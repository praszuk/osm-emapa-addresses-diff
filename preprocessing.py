import logging

from csv import DictReader
from os import path
from typing import Dict, List

from address import Address


STREET_NAMES_MAPPING_FILE = path.join('data', 'street_names_mappings.csv')

# TODO add update check from github

def _load_mappings_data() -> Dict[str, Dict[str, str]]:
    street_names: Dict[str, Dict[str, str]] = dict()

    with open(STREET_NAMES_MAPPING_FILE, 'r') as csv_file:
        reader = DictReader(csv_file, delimiter=',')
        for row in reader:
            simc = row['teryt_simc_code']
            # sym_ul = row['teryt_ulic_code']
            origin_name = row['teryt_street_name']
            osm_name = row['osm_street_name']

            if simc not in street_names:
                street_names[simc] = dict()

            street_names[simc][origin_name] = osm_name

    return street_names


def replace_streets_with_osm_names(emapa_addresses: List[Address]) -> None:
    """
    Use street_names community file to find and replace names which contains
    e.g. shortcuts to match them to OSM data.

    It uses .csv file from gugik2osm:
    https://github.com/openstreetmap-polska/gugik2osm/
    blob/main/processing/sql/data/street_names_mappings.csv
    """

    # k: simc, dict[sym_ul, Tuple[origin name, osm name]]
    street_names = _load_mappings_data()
    matched_streets = set()

    for addr in emapa_addresses:
        if not addr.street:
            continue

        if addr.city_simc not in street_names:
            continue

        if addr.street not in street_names[addr.city_simc]:
            continue

        new_street_name = street_names[addr.city_simc][addr.street]
        addr.street = new_street_name
        matched_streets.add(new_street_name)

    logging.info(
        f'Matched and replaced {len(matched_streets)} streets'
        ' to existing OSM street names'
    )
