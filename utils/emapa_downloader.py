import logging
import requests

from os import path
from typing import Optional, Tuple
from lxml import etree

from exceptions import TerytNotFound, EmapaServiceNotFound


EMAPA_ADDRESSES_URL = 'https://integracja.gugik.gov.pl/daneadresowe/'
COLUMN_LEN = 7


def _parse_response(
    teryt_terc: str,
    response: str
) -> Optional[Tuple[str, str]]:
    """
    :param teryt_terc: commune (gmina) id number
    :param response: html response text
    :raise TerytNotFound: if teryt_terc is not matched with any table row
    :return: Tuple with CSV URI and Local system URI if matched teryt_terc
    else None
    """
    # Service use 6 char teryt
    # last character (in 7 char) is commune (gmina) type
    teryt = teryt_terc[:-1] if len(teryt_terc) == 7 else teryt_terc

    table = etree.HTML(response).find('.//table[2]')

    matched_csv_uri = None
    matched_local_system_url = None
    rows = table[0].xpath('.//tr')
    for row in rows[1:]:
        col_elements = row.xpath('.//td')
        """
        It should contain 7 columns:
         col[0]: column index (from 1)
         col[1]: teryt
         col[2]: commune (gmina) name
         col[3]: SHP URI
         col[4]: GML URI
         col[5]: CSV URI
         col[6]: Local map system to display addresses URL
        """
        assert len(col_elements) == COLUMN_LEN
        _, elem_teryt, _, _, _, elem_csv, elem_system_url = col_elements

        c_teryt = elem_teryt.text
        c_csv = next(iter(elem_csv.xpath('.//a/@href')), None)
        c_local_system_url = next(iter(
            elem_system_url.xpath('.//a/text()')),
            None
        )

        if c_teryt == teryt:
            logging.debug('Parsed columns: {} {} {}'.format(
                c_teryt, c_csv, c_local_system_url
            ))
            logging.debug('Raw: {} {} {}'.format(
                etree.tostring(elem_teryt),
                etree.tostring(elem_csv),
                etree.tostring(elem_system_url)
            ))
            matched_csv_uri = c_csv
            matched_local_system_url = c_local_system_url
            break

    if not matched_csv_uri:
        raise TerytNotFound()

    return matched_csv_uri, matched_local_system_url


def download_emapa_csv(teryt_terc: str, output_dir: str) -> Tuple[str, str]:
    """
    :param teryt_terc: commune (gmina) id number
    :param output_dir: directory to save emapa csv file
    :raises TerytNotFound, EmapaSeriveNotFound, IOError:
    :return: filepath (including output_dir) and local system url (e-mapa)

    Download emapa csv file with addresses from GUGiK site
    """
    logging.info("Downloading emapa csv data...")
    response = requests.get(EMAPA_ADDRESSES_URL)
    csv_uri, local_system_url = _parse_response(teryt_terc, response.text)

    if 'e-mapa' not in local_system_url:
        raise EmapaServiceNotFound()

    csv_filename = path.join(output_dir, local_system_url + '.csv')
    with open(csv_filename, 'wb') as f:
        r = requests.get(csv_uri)
        f.write(r.content)

    return csv_filename, local_system_url
    