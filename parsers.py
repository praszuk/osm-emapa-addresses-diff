import csv
import logging

from typing import Any, Dict, List, Optional

from address import Address, OsmAddress, OsmType, Point


def parse_csv_address_row(row, address_source: str) -> Optional[Address]:
    """
    :param row: csv row
    :param address_source: source of dataset (local map system url)
    :return: created address or None
    """
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
            ),
            source=address_source
        )
    except KeyError:
        logging.warning(f'Couldn\'t parse row: {row}')
        return None


def parse_emapa_file(input_filename: str, source: str) -> List[Address]:
    """
    :param input_filename: csv file with addresses data
    :param source: URL to local map system from above file is downloaded
    :return: List of parsed addresses
    """
    addresses = []
    with open(input_filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')

        row_counter = 0
        for row in reader:
            row_counter += 1
            new_addr = parse_csv_address_row(row, source)
            if new_addr:
                addresses.append(new_addr)

    return addresses


def parse_teryt_terc_file(input_filename: str, teryt_terc: str) -> str:
    """
    Validates teryt_terc id if it is correct and if it is commune (gmina)
    from govenment dataset: https://eteryt.stat.gov.pl/

    :param input_filename: csv file with teryt terc ids
    :param teryt_terc: commune (gmina) id number
    :raises ValueError: if teryt_terc not found/not allowed
    :return: area name assigned to given teryt from government csv file

    """
    with open(input_filename, 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')

        for row in reader:
            terc = ''.join([row['WOJ'], row['POW'], row['GMI'], row['RODZ']])
            if terc == teryt_terc:
                return row['NAZWA']

    raise ValueError('Incorrect teryt_terc!')


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
        source=element['tags'].get('source:addr', None),
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
