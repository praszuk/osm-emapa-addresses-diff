from collections import Counter
from typing import Dict, List, Set, Union

from address import Address, OsmAddress


def addr_tags_distribution(addresses: List[OsmAddress]) -> Counter:
    """
    :return: tags counter distribution of usage addr* tags + source:addr
    """
    tags = Counter()
    for addr in addresses:
        for key in addr.all_obj_tags.keys():
            if key.startswith('addr:') or key == 'source:addr':
                tags[key] += 1

    return tags


def addr_type_distribution(addresses: List[OsmAddress]) -> Counter:
    """
    :return: osm type counter distribution usage
    """
    osm_type = Counter()
    for addr in addresses:
        osm_type[addr.osm_type] += 1

    return osm_type


def addr_duplicates(osm_addresses: List[OsmAddress]) -> List[List[OsmAddress]]:
    """
    :return: duplicated addresses (checks by city street and housenumber)
    """
    duplicated_osm_addr: Dict[str, List[OsmAddress]] = dict()

    for osm_addr in osm_addresses:
        osm_min_addr = f'{osm_addr.city}' \
            f'{osm_addr.street if osm_addr.street else ""}' \
            f'{osm_addr.housenumber}'
        if osm_min_addr not in duplicated_osm_addr:
            duplicated_osm_addr[osm_min_addr] = []

        duplicated_osm_addr[osm_min_addr].append(osm_addr)

    return list(filter(lambda v: len(v) > 1, duplicated_osm_addr.values()))


def addr_missing(
    addresses1: List[Address],
    addresses2: List[Address],
) -> List[Union[Address, OsmAddress]]:
    """
    :return: diff between datasets
        it returns missing addresses in addresses1 from adddress2
    """
    all_min_unique_addr1: Set[str] = set()
    for addr1 in addresses1:
        all_min_unique_addr1.add(addr1.min_unique)

    missing_addresses = []
    for addr2 in addresses2:
        if addr2.min_unique not in all_min_unique_addr1:
            missing_addresses.append(addr2)

    return missing_addresses
