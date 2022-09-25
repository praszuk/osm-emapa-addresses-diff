import csv
import logging

from typing import List

from address import Address, Point


def parse_csv_row(row) -> Address:
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
