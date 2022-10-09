from address import OsmAddress

# Subjective list of keys based on
# https://wiki.openstreetmap.org/wiki/Map_features
POI_KEYS = {
    'amenity',
    'craft',
    'emergency',
    'healthcare',
    'leisure',
    'man_made',
    'office',
    'shop',
    'tourism'
}


def is_poi(address: OsmAddress) -> bool:
    return any(key in POI_KEYS for key in address.all_obj_tags.keys())
