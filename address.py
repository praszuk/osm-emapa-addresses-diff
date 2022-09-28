from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional


class OsmType(Enum):
    NODE = 'node'
    WAY = 'way'
    RELATION = 'relation'


@dataclass
class Point:
    lat: float
    lon: float


@dataclass
class Address:
    point: Point

    city_simc: str
    housenumber: str
    postcode: str
    city: str    # city or place, no matters
    street: str  # if no street then None or empty str
    source: str

    def to_osm_tags(self) -> Dict[str, str]:
        addr = {}

        if not self.street:
            addr['addr:place'] = self.city
        else:
            addr['addr:city'] = self.city
            addr['addr:street'] = self.street

        addr['addr:city:simc'] = self.city_simc
        addr['addr:housenumber'] = self.housenumber
        addr['addr:postcode'] = self.postcode
        if self.source:
            addr['source:addr'] = self.source

        return addr


@dataclass
class OsmAddress(Address):
    osm_id: int
    osm_type: OsmType
    all_obj_tags: Dict[str, Any]
