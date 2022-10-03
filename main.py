import json
import logging
import pathlib
import sys

from os import path
from sys import argv
from typing import Any, Dict, List, Optional, Tuple

from analyze import (
    addr_type_distribution,
    addr_tags_distribution,
    addr_duplicates,
    addr_missing
)
from address import Address, OsmAddress
from parsers.emapa import parse_emapa_file
from parsers.teryt import parse_teryt_terc_file
from exceptions import TerytNotFound, EmapaServiceNotFound
from utils.emapa_downloader import download_emapa_csv
from utils.overpass import download_osm_data, is_element
from config import ROOT_DIR
from utils.street_names_mappings import replace_streets_with_osm_names


OUTPUT_DIR: str = path.join(ROOT_DIR, 'out')
TERYT_TERC_FILE: str = path.join(ROOT_DIR, 'data', 'terc.csv')


def download_emapa_addresses(teryt_terc: str) -> List[Address]:
    try:
        csv_filename = path.join(
            OUTPUT_DIR,
            teryt_terc,
            'emapa_addresses_raw.csv'
        )
        local_system_url = download_emapa_csv(teryt_terc, csv_filename)

    except TerytNotFound:
        logging.error(f'Teryt {teryt_terc} not found at GUGiK website!')
        sys.exit(2)
    except EmapaServiceNotFound:
        logging.error(f'Not found e-mapa service for teryt: {teryt_terc}')
        sys.exit(3)
    except IOError as e:
        logging.error(f'Error with downloading/saving data: {e}')
        sys.exit(4)

    emapa_addresess: List[Address] = parse_emapa_file(
        csv_filename,
        local_system_url
    )
    for addr in emapa_addresess:
        addr.source_addr = local_system_url

    logging.info(f'Parsed {len(emapa_addresess)} emapa addresses.')
    return emapa_addresess


def download_osm_addresses(teryt_terc: str) -> List[OsmAddress]:
    osm_data: Optional[Dict[str, Any]] = download_osm_data(teryt_terc)
    if osm_data is None:
        logging.error(f'Error with downloading OSM (Overpass) data.')
        sys.exit(4)

    elements: List[Dict[str, Any]] = list(
        filter(is_element, osm_data['elements'])
    )

    logging.debug(f'Downloaded {len(elements)} OSM elements.')
    osm_addresses: List[OsmAddress] = list(
        map(OsmAddress.parse_from_osm_element, elements)
    )
    logging.info(f'Parsed {len(osm_addresses)} OSM addresses.')

    return osm_addresses


def report_osm_type(osm_addresses: List[OsmAddress]) -> str:
    osm_type_dist = addr_type_distribution(osm_addresses).most_common()
    return '\nOsm Type: \n{}'.format(
        '\n'.join(f'{k}: {v}' for k, v in osm_type_dist)
    )


def report_key_value_distribution(osm_addresses: List[OsmAddress]) -> str:
    kv_dist: List[Tuple] = addr_tags_distribution(osm_addresses).most_common()
    return '\nKey-values distribution: \n{}'.format(
        '\n'.join(
            f'{k}: {v} ({v * 100 / len(osm_addresses):.2f}%)'
            for k, v in kv_dist
        )
    )


def report_duplicates(
    duplicated_addresses: List[List[OsmAddress]],
    osm_address: List[OsmAddress]
) -> str:
    return '\nDuplicated OSM addresses: {}/{} ({:.2f})'.format(
        len(duplicated_addresses),
        len(osm_address),
        len(duplicated_addresses) * 100 / len(osm_address)
    )


def save_missing_addresses(
    missing_emapa_addresses: List[Address],
    teryt_terc: str
) -> None:
    geojson: Dict[str, Any] = Address.addresses_to_geojson(
        missing_emapa_addresses
    )
    filename = f'emapa_addresses_missing.geojson'
    with open(path.join(OUTPUT_DIR, teryt_terc, filename), 'w') as f:
        json.dump(geojson, f, indent=4)


def save_excess_addresses(
    excess_osm_addresses: List[OsmAddress],
    teryt_terc: str
) -> None:
    assert type(excess_osm_addresses[0]) == OsmAddress

    shorten_osm_obj_sequence = ','.join([
        addr.shorten_osm_obj for addr in excess_osm_addresses
    ])
    filename = f'osm_addresses_excess.txt'
    with open(path.join(OUTPUT_DIR, teryt_terc, filename), 'w') as f:
        f.write(
            '# You can load it in the JOSM '
            'using "Download object" function (CTRL + SHIFT + O).\n'
        )
        f.write(shorten_osm_obj_sequence)


def save_all_emapa_addresses(
    emapa_addresses: List[Address],
    teryt_terc: str
) -> None:
    geojson: Dict[str, Any] = Address.addresses_to_geojson(emapa_addresses)
    filename = f'emapa_addresses_all.geojson'
    with open(path.join(OUTPUT_DIR, teryt_terc, filename), 'w') as f:
        json.dump(geojson, f, indent=4)


def main():
    # Parse and check teryt_terc
    teryt_terc = argv[1]
    try:
        area_name = parse_teryt_terc_file(TERYT_TERC_FILE, teryt_terc)
        logging.info(f'Parsed teryt_terc ({teryt_terc}) as: {area_name}')
    except (ValueError, IOError):
        logging.error('Cannot parse teryt terc parameter!')
        sys.exit(1)

    # Create teryt_terc output directory if not exists
    pathlib.Path(path.join(OUTPUT_DIR, teryt_terc)).mkdir(
        parents=True,
        exist_ok=True
    )
    # Download e-mapa and OSM adddresses
    emapa_addresses: List[Address] = download_emapa_addresses(teryt_terc)
    replace_streets_with_osm_names(emapa_addresses)
    osm_addresses: List[OsmAddress] = download_osm_addresses(teryt_terc)

    # Analysis reports
    print(report_osm_type(osm_addresses))
    print(report_key_value_distribution(osm_addresses))

    duplicated_addr = addr_duplicates(osm_addresses)
    print(report_duplicates(duplicated_addr, osm_addresses))

    missing_emapa_addresses = addr_missing(osm_addresses, emapa_addresses)
    print(
        'Missing OSM addresses which exist in the emapa: ',
        len(missing_emapa_addresses)
    )
    excess_osm_addresses: List[OsmAddress] = addr_missing(
        emapa_addresses,
        osm_addresses
    )
    print(
        'Excess OSM addresses which do not exist in the emapa: ',
        len(excess_osm_addresses)
    )

    # Save data to files
    save_missing_addresses(missing_emapa_addresses, teryt_terc)
    save_excess_addresses(excess_osm_addresses, teryt_terc)
    save_all_emapa_addresses(emapa_addresses, teryt_terc)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main()
