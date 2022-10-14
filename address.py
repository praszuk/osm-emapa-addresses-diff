from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List

from config import Config


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

    @property
    def min_unique(self) -> str:
        """
        :return: minimal unique string for each address which contains
            city, street (optionally), housenumber
        """
        street = self.street if self.street else ''

        housenumber = self.housenumber
        if Config.IGNORE_CASE_SENSITIVE_HOUSENUMBER:
            housenumber = housenumber.lower()

        return f'{self.city}{street}{housenumber}'

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

    @staticmethod
    def addresses_to_geojson(addresses: List[Address]) -> Dict[str, Any]:
        geojson = {
            'type': 'FeatureCollection',
            'features': []
        }
        for addr in addresses:
            geojson['features'].append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [addr.point.lon, addr.point.lat],
                },
                'properties': addr.to_osm_tags()
            })

        return geojson


@dataclass
class OsmAddress(Address):
    osm_id: int
    osm_type: OsmType
    all_obj_tags: Dict[str, Any]

    @property
    def shorten_osm_obj(self) -> str:
        """
        :return: shorten object identifier which can be load in the JOSM
            node – n, way – w, relation – r
            example: n123
        """
        return {
            OsmType.NODE: 'n',
            OsmType.WAY: 'w',
            OsmType.RELATION: 'r'
        }[self.osm_type] + str(self.osm_id)

    @staticmethod
    def parse_from_osm_element(element: Dict[str, Any]) -> OsmAddress:
        osm_type = OsmType(element['type'])

        if osm_type == OsmType.NODE:
            point = Point(element['lat'], element['lon'])
        else:
            point = Point(element['center']['lat'], element['center']['lon'])

        if 'addr:street' in element['tags']:
            city = element['tags'].get('addr:city', None)
        else:
            city = element['tags'].get('addr:place', None)

        return OsmAddress(
            osm_id=element['id'],
            osm_type=osm_type,
            point=point,
            city=city,
            city_simc=element['tags'].get('addr:city:simc', None),
            street=element['tags'].get('addr:street', None),
            housenumber=element['tags'].get('addr:housenumber', None),
            postcode=element['tags'].get('addr:postcode', None),
            source=element['tags'].get('source:addr', None),
            all_obj_tags=element['tags']
        )
