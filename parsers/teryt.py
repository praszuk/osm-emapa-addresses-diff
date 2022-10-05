import csv

from config import gettext as _


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

    raise ValueError(_('Incorrect teryt_terc!'))
