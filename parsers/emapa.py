import csv
import logging
from typing import Optional, List

from address import Address, Point


def _parse_csv_address_row(row, address_source: str) -> Optional[Address]:
    """
    :param row: csv row
    :param address_source: source of dataset (local map system url)
    :return: created address or None
    """
    try:
        raw_postcode = row['AdresCSIOZ'].split('|')[0].strip()
        postcode = raw_postcode[:2] + '-' + raw_postcode[2:]
        raw_street = row['Nazwa ulicy'].strip()
        return Address(
            city=row['Nazwa miejscowości'].strip(),
            city_simc=row['SIMC'].strip(),
            street=raw_street if raw_street else None,
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
            new_addr = _parse_csv_address_row(row, source)
            if new_addr:
                addresses.append(new_addr)

    return addresses
