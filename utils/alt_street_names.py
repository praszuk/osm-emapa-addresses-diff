from typing import Any, Dict, List


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
    """
    streets = dict()
    for element in elements:
        assert element['tags']['name']
        for alt_name_key in ALT_NAME_KEYS:
            alt_value = element['tags'].get(alt_name_key, None)
            if alt_value:
                streets[alt_value] = element['tags']['name']

    return streets
