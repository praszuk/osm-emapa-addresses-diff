from dataclasses import dataclass
from typing import Dict


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
        addr['source:addr'] = 'e-mapa.net'

        return addr
