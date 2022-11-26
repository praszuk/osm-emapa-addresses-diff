import logging

from datetime import datetime
from csv import DictReader
from os import path
from typing import Dict, List, Optional

from address import Address
from config import Config
from config import gettext as _
from utils.github import (
    download_file,
    get_file_commits,
    get_latest_commit_dt
)


STREET_NAMES_DT_FILENAME = 'street_names_dt.txt'
STREET_NAMES_FILENAME = 'street_names_mappings.csv'


def _get_remote_file_dt() -> datetime:
    commits_data = get_file_commits(
        'openstreetmap-polska',
        'gugik2osm',
        f'processing/sql/data/{STREET_NAMES_FILENAME}'
    )
    return get_latest_commit_dt(commits_data)


def _load_current_file_dt() -> Optional[datetime]:
    filename = path.join(Config.DATA_DIR, STREET_NAMES_DT_FILENAME)
    try:
        with open(filename, 'r') as dt_file:
            return datetime.fromisoformat(dt_file.read().strip())

    except (IOError, ValueError):
        logging.exception(_(
            'Couldn\'t read local datetime of street names mappings data'
            ' from file: {}'
        ).format(filename))
        return None


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


def _update_street_names_data(remote_dt: datetime) -> None:
    filename_data = path.join(Config.DATA_DIR, STREET_NAMES_FILENAME)
    filename_dt = path.join(Config.DATA_DIR, STREET_NAMES_DT_FILENAME)
    csv_data = download_file(
        'openstreetmap-polska',
        'gugik2osm',
        f'main/processing/sql/data/{STREET_NAMES_FILENAME}'
    )
    if not csv_data:
        raise ValueError(
            _('Couldn\'t download street names mappings data update')
        )

    with open(filename_data, 'w') as f:
        f.write(csv_data)

    with open(filename_dt, 'w') as f:
        f.write(remote_dt.isoformat())

    logging.info(
        _('Updated street names mappings files using data from {}').format(
            filename_data,
            filename_dt,
            remote_dt
        )
    )


def _street_names_autoupdate():
    """
    :raise ValueError: if downloaded data is None
    """
    local_dt = _load_current_file_dt()
    remote_dt = _get_remote_file_dt()

    if local_dt == remote_dt:
        logging.debug('No autoupdate of street names mappings needed.')
        return

    logging.warning(
        _('New update for the {} file is available!').format(
            STREET_NAMES_FILENAME
        )
    )

    # Autoupdating
    _update_street_names_data(remote_dt)


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
    if not Config.NO_STREET_NAMES_UPDATE_CHECK:
        try:
            _street_names_autoupdate()
        except ValueError:
            logging.exception('Couldn\'t autoupdate street names mappigns!')

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
