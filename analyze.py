from collections import Counter
from typing import Dict, List

from address import OsmAddress


def addr_tags_distribution(addresses: List[OsmAddress]) -> Counter:
    tags = Counter()
    for addr in addresses:
        for key in addr.all_obj_tags.keys():
            if key.startswith('addr:') or key == 'source:addr':
                tags[key] += 1

    return tags


def addr_type_distribution(addresses: List[OsmAddress]) -> Counter:
    osm_type = Counter()
    for addr in addresses:
        osm_type[addr.osm_type] += 1

    return osm_type


def addr_duplicates(osm_addresses: List[OsmAddress]) -> List[List[OsmAddress]]:
    duplicated_osm_addr: Dict[str, List[OsmAddress]] = dict()

    for osm_addr in osm_addresses:
        osm_min_addr = f'{osm_addr.city}' \
            f'{osm_addr.street if osm_addr.street else ""}' \
            f'{osm_addr.housenumber}'
        if osm_min_addr not in duplicated_osm_addr:
            duplicated_osm_addr[osm_min_addr] = []

        duplicated_osm_addr[osm_min_addr].append(osm_addr)

    return list(filter(lambda v: len(v) > 1, duplicated_osm_addr.values()))
