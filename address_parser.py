import csv
import logging

from typing import Any, Dict, List, Optional

from address import Address, OsmAddress, OsmType, Point


def parse_csv_row(row) -> Optional[Address]:
    try:
        raw_postcode = row['AdresCSIOZ'].split('|')[0].strip()
        postcode = raw_postcode[:2] + '-' + raw_postcode[2:]
        return Address(
            city=row['Nazwa miejscowości'].strip(),
            city_simc=row['SIMC'].strip(),
            street=row['Nazwa ulicy'].strip(),
            housenumber=row['Numer'].strip(),
            postcode=postcode,
            point=Point(
                float(row['szerokosc_geograficzna'].strip()),
                float(row['dlugosc_geograficzna'].strip())
            )
        )
    except KeyError:
        logging.warning(f'Couldn\'t parse row: {row}')
        return None


def parse_file(input_filename) -> List[Address]:
    addresses = []
    with open(input_filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')

        row_counter = 0
        for row in reader:
            row_counter += 1
            new_addr = parse_csv_row(row)
            if new_addr:
                addresses.append(new_addr)

    return addresses


def parse_from_osm_element(element: Dict[str, Any]) -> OsmAddress:
    osm_type = OsmType(element['type'])

    if osm_type == OsmType.NODE:
        point = Point(element['lat'], element['lon'])
    else:
        point = Point(element['center']['lat'], element['center']['lon'])

    return OsmAddress(
        osm_id=element['id'],
        osm_type=osm_type,
        point=point,
        city=element['tags'].get('addr:city', None),
        city_simc=element['tags'].get('addr:city:simc', None),
        street=element['tags'].get('addr:street', None),
        housenumber=element['tags'].get('addr:housenumber', None),
        postcode=element['tags'].get('addr:postcode', None),
        all_obj_tags=element['tags']
    )


def addresses_to_geojson(addresses) -> Dict[str, Any]:
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
