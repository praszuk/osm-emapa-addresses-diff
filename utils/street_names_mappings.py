import logging

from csv import DictReader
from os import path
from typing import Dict, List

from address import Address
from config import Config
from config import gettext as _
from utils.github import get_file_commits, get_latest_commit_date


# Should be updated together with street_names_mappings data file
_LATEST_COMMIT_DATE = '2022-09-14T18:03:52Z'
STREET_NAMES_FILENAME = 'street_names_mappings.csv'


def _is_update_aviailable() -> bool:
    try:
        commits_data = get_file_commits(
            'openstreetmap-polska',
            'gugik2osm',
            f'processing/sql/data/{STREET_NAMES_FILENAME}'
        )
        commit_date = get_latest_commit_date(commits_data)

        return commit_date != _LATEST_COMMIT_DATE

    except (IOError, KeyError):
        logging.exception(_(
            'Couldn\'t check for the {} file data update!'
        ).format(STREET_NAMES_FILENAME))

    return False


def _load_mappings_data() -> Dict[str, Dict[str, str]]:
    """
    :return: dictionary with city_simc, teryr_street_name and osm_street_name
    Dict[city_simc, Dict[origin_name, osm_name]]

    """
    street_names: Dict[str, Dict[str, str]] = dict()

    filename = path.join(Config.DATA_DIR, STREET_NAMES_FILENAME)
    with open(filename, 'r') as csv_file:
        reader = DictReader(csv_file, delimiter=',')
        for row in reader:
            simc = row['teryt_simc_code']
            # sym_ul = row['teryt_ulic_code']
            # lower – to avoid divergence between PRG and local e-mapa datasets
            origin_name = row['teryt_street_name'].lower()
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

    :param emapa_addresses: address to find and optionally match and replace
    street_names
    """
    if not Config.NO_STREET_NAMES_UPDATE_CHECK and _is_update_aviailable():
        logging.warning(
            _('New update for the {} file is available!').format(
                STREET_NAMES_FILENAME
            )
        )

    street_names: Dict[str, Dict[str, str]] = _load_mappings_data()
    matched_streets = set()

    for addr in emapa_addresses:
        if not addr.street:
            continue

        if addr.city_simc not in street_names:
            continue

        if addr.street.lower() not in street_names[addr.city_simc]:
            continue

        new_street_name = street_names[addr.city_simc][addr.street.lower()]
        addr.street = new_street_name
        matched_streets.add(new_street_name)

    logging.info(
        _(
            'Matched and replaced {} '
            'streets to existing OSM street names'
        ).format(len(matched_streets))
    )
