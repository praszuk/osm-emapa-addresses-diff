import json
import logging
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


def main():
    teryt_terc = argv[1]
    try:
        area_name = parse_teryt_terc_file(TERYT_TERC_FILE, teryt_terc)
        logging.info(f'Parsed teryt_terc ({teryt_terc}) as: {area_name}')
    except (ValueError, IOError):
        logging.error('Cannot parse teryt terc parameter!')
        sys.exit(1)

    try:
        csv_filename, local_system_url = download_emapa_csv(
            teryt_terc,
            OUTPUT_DIR
        )
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

    replace_streets_with_osm_names(emapa_addresess)

    osm_data: Optional[Dict[str, Any]] = download_osm_data(teryt_terc)
    elements: List[Dict[str, Any]] = list(
        filter(is_element, osm_data['elements'])
    )

    logging.debug(f'Downloaded {len(elements)} OSM elements.')
    osm_addresses: List[OsmAddress] = list(
        map(OsmAddress.parse_from_osm_element, elements)
    )
    total_osm_addr = len(osm_addresses)
    logging.info(f'Parsed {total_osm_addr} OSM addresses.')

    print('\nOsm type:')
    osm_type_dist = addr_type_distribution(osm_addresses).most_common()
    print('\n'.join(f'{k}: {v}' for k, v in osm_type_dist))

    print('\nKey-values distribution:')
    kv_dist: List[Tuple] = addr_tags_distribution(osm_addresses).most_common()
    print('\n'.join(
        f'{k}: {v} ({v*100/len(osm_addresses):.2f}%)' for k, v in kv_dist)
    )

    duplicated_addr = addr_duplicates(osm_addresses)
    print(
        f'\nDuplicated OSM addresses: {len(duplicated_addr)}/{total_osm_addr}'
        f' ({len(duplicated_addr)*100/total_osm_addr:.2f}%)'
    )

    missing_emapa_addresses = addr_missing(osm_addresses, emapa_addresess)
    print(
        f'Missing OSM addresses which exist in the emapa: '
        f'{len(missing_emapa_addresses)}'
    )

    geojson: Dict[str, Any] = Address.addresses_to_geojson(
        missing_emapa_addresses
    )
    filename = f'emapa_addresses_{area_name}_missing.geojson'
    with open(path.join(OUTPUT_DIR, filename), 'w') as f:
        json.dump(geojson, f, indent=4)

    excess_osm_addresses: List[OsmAddress] = addr_missing(
        emapa_addresess,
        osm_addresses
    )
    print(
        f'Excess OSM addresses which does not exist in the emapa: '
        f'{len(excess_osm_addresses)}'
    )
    assert type(excess_osm_addresses[0]) == OsmAddress

    shorten_osm_obj_sequence = ','.join([
        addr.shorten_osm_obj for addr in excess_osm_addresses
    ])
    filename = f'osm_addresses_{area_name}_excess.txt'
    with open(path.join(OUTPUT_DIR, filename), 'w') as f:
        f.write(
            '# You can load it in the JOSM '
            'using "Download object" function (CTRL + SHIFT + O).\n'
        )
        f.write(shorten_osm_obj_sequence)

    geojson: Dict[str, Any] = Address.addresses_to_geojson(emapa_addresess)
    filename = f'emapa_addresses_{area_name}_all.geojson'
    with open(path.join(OUTPUT_DIR, filename), 'w') as f:
        json.dump(geojson, f, indent=4)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main()
