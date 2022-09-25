import json
import logging

from os import path
from sys import argv
from typing import Any, Dict, List, Optional, Tuple

from address import Address
from address_parser import (
    parse_file,
    addresses_to_geojson,
    parse_from_osm_element
)
from analyze import addr_tags_distribution
from overpass import download_osm_data, is_element


OUTPUT_DIR = 'out'


def main():
    input_csv_filename = argv[1]

    emapa_addresess: List[Address] = parse_file(input_csv_filename)
    logging.info(f'Parsed {len(emapa_addresess)} emapa addresses.')

    osm_data: Optional[Dict[str, Any]] = download_osm_data()
    elements: List[Dict[str, Any]] = list(
        filter(is_element, osm_data['elements'])
    )
    logging.debug(f'Downloaded {len(elements)} OSM elements.')
    osm_addresses: List[Address] = list(map(parse_from_osm_element, elements))
    logging.info(f'Parsed {len(osm_addresses)} OSM addresses.')

    print('\nKey-values distribution:')
    kv_dist: List[Tuple] = addr_tags_distribution(osm_addresses).most_common()
    print('\n'.join(
        f'{k}: {v} ({v*100/len(osm_addresses):.2f}%)' for k, v in kv_dist)
    )

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
