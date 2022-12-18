from typing import Any, Dict, List

from address import Address
from config import gettext as _, logger


ALT_NAME_KEYS = {
    'alt_name',
    'official_name',
    'short_name',
    'loc_name'
}


def parse_streets_names_from_elements(
    elements: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    :param elements: List of OSM way (street) objects
    :return: transformed dict, which contains all names
    where value is general value from "name" tag and keys are alternate names
    for given streets e.g.
    name: 'Lastname'
    alt_name: 'Firstname Lastname'
    official_name: 'Prefix1 Prefix2 Firstname Lastanme'
    then it creates 2 items alt_name: name and official_name: name
    keys are lowered
    """
    streets = dict()
    for element in elements:
        assert element['tags']['name']
        for alt_name_key in ALT_NAME_KEYS:
            alt_value = element['tags'].get(alt_name_key, None)
            if alt_value:
                streets[alt_value.lower()] = element['tags']['name']

    return streets

def replace_streets_with_osm_alt_names(
    emapa_addresses: List[Address],
    osm_alt_streets_names: Dict[str, str]
) -> None:
    """
    Use altertnate street names tags (like official_name) to find
    and replace emapa streetnames if addr:street from emapa source
    is not eq. to main "name" street tag in OSM but way contains
    e.g. "official_name" with same string.

    :param emapa_addresses: address to find and optionally match and replace
    street names
    :param osm_alt_streets_names: dicitonary with alt_names: main name
    """
    matched_streets = set()

    for addr in emapa_addresses:
        if not addr.street:
            continue

        if addr.street.lower() not in osm_alt_streets_names:
            continue

        new_street_name = osm_alt_streets_names[addr.street.lower()]
        addr.street = new_street_name
        matched_streets.add(new_street_name)

    logger.info(
        _(
            'Matched and replaced {} '
            'streets to alternate OSM streets names'
        ).format(len(matched_streets))
    )