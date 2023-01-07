from lxml import etree

from typing import Optional, List

from address import Address, Point


ADDRESS_XML_PATH = 'wfs:member/ms:punkty_adresowe'


def _parse_gml_address_element(
    elem: etree.Element, ns: dict,
    address_source: str
) -> Optional[Address]:
    """
    :param elem: XML Punkty Adresowe Element
    :param ns: XML Namespaces
    :param address_source: source of dataset (local map system url)
    :return: created address or None
    """
    city = elem.find('ms:NAZWA_MIEJSCOWOSCI', namespaces=ns).text.strip()
    postcode = elem.find('ms:KOD_POCZTOWY', namespaces=ns).text.strip()
    housenumber = elem.find('ms:NUMER_PORZADKOWY', namespaces=ns).text.strip()
    simc = elem.find('ms:ID_MIEJSCOWOSCI', namespaces=ns).text.strip()

    raw_street = elem.findtext('ms:NAZWA_ULICY', namespaces=ns)
    if raw_street:
        street = raw_street.strip()
    else:
        street = None

    lat, lon = list(map(float, elem.find(
        'ms:msGeometry/gml:Point/gml:pos', namespaces=ns
    ).text.strip().split()))

    return Address(
        city=city,
        city_simc=simc,
        street=street,
        housenumber=housenumber,
        postcode=postcode,
        point=Point(lat, lon),
        source=address_source
    )

def parse_emapa_file(input_filename: str, source: str) -> List[Address]:
    """
    :param input_filename: gml file with addresses data
    :param source: URL to local map system from above file is downloaded
    :return: List of parsed addresses
    """
    addresses = []
    tree = etree.parse(input_filename)
    root = tree.getroot()

    for addresss_elem in root.xpath(ADDRESS_XML_PATH, namespaces=root.nsmap):
        addresses.append(_parse_gml_address_element(
            addresss_elem,
            root.nsmap,
            source
        ))

    return addresses
