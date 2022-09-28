import json
import logging
import sys

from os import path
from sys import argv
from typing import Any, Dict, List, Optional, Tuple

from address import Address, OsmAddress
from address_parser import (
    parse_file,
    addresses_to_geojson,
    parse_from_osm_element
)
from analyze import (
    addr_type_distribution,
    addr_tags_distribution,
    addr_duplicates,
    addr_missing
)
from exceptions import TerytNotFound, EmapaServiceNotFound
from overpass import download_osm_data, is_element
from preprocessing import replace_streets_with_osm_names
from gugik_util import download_emapa_csv


OUTPUT_DIR = 'out'


def main():
    teryr_terc = argv[1]
    try:
        csv_filename, local_system_url = download_emapa_csv(
            teryr_terc,
            OUTPUT_DIR
        )
    except TerytNotFound:
        logging.error(f'Teryt {teryr_terc} not found at GUGiK website!')
        sys.exit(1)
    except EmapaServiceNotFound:
        logging.error(f'Not found e-mapa service for teryt: {teryr_terc}')
        sys.exit(2)
    except IOError as e:
        logging.error(f'Error with downloading/saving data: {e}')
        sys.exit(3)

    emapa_addresess: List[Address] = parse_file(csv_filename, local_system_url)
    for addr in emapa_addresess:
        addr.source_addr = local_system_url
    logging.info(f'Parsed {len(emapa_addresess)} emapa addresses.')

    replace_streets_with_osm_names(emapa_addresess)

    osm_data: Optional[Dict[str, Any]] = download_osm_data()
    elements: List[Dict[str, Any]] = list(
        filter(is_element, osm_data['elements'])
    )

    logging.debug(f'Downloaded {len(elements)} OSM elements.')
    osm_addresses: List[OsmAddress] = list(
        map(parse_from_osm_element, elements)
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
    print(f'**Missing emapa addresses: {len(missing_emapa_addresses)}')

    geojson: Dict[str, Any] = addresses_to_geojson(missing_emapa_addresses)
    with open(path.join(OUTPUT_DIR, 'missing_addresses.geojson'), 'w') as f:
        json.dump(geojson, f, indent=4)

    geojson: Dict[str, Any] = addresses_to_geojson(emapa_addresess)
    with open(path.join(OUTPUT_DIR, 'all_addresses.geojson'), 'w') as f:
        json.dump(geojson, f, indent=4)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main()
