from collections import Counter
from typing import List

from address import OsmAddress


def addr_tags_distribution(addresses: List[OsmAddress]) -> Counter:
    tags = Counter()
    for addr in addresses:
        for key in addr.all_obj_tags.keys():
            if key.startswith('addr:') or key == 'source:addr':
                tags[key] += 1

    return tags
