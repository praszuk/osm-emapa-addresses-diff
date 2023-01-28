import requests

from config import gettext as _, logger
from exceptions import ServiceNotFound
from typing import Optional


PUNKTYADRESOWE_URL = 'https://www.punktyadresowe.pl/' \
                     'cgi-bin/emuia/<teryt>' \
                     '?service=WFS' \
                     '&request=GetFeature' \
                     '&SRSNAME=urn:ogc:def:crs:EPSG::4326' \
                     '&typenames=ms:punkty_adresowe' \
                     '&version=2.0.0'

PUNKTYADRESOWE_SOURCE_EMAPA_URL = 'https://www.punktyadresowe.pl/' \
                                  'cgi-bin/emuia/<teryt>'


def download_emapa_gml(teryt: str, gml_filename: str) -> None:
    """
    :param teryt: commune (gmina) id number (6 characters)
    :param gml_filename: filepath to save gml file
    :raises ServiceNotFound, IOError

    Download e-mapa gml file with addresses from GUGiK site
    """
    logger.info(_('Downloading emapa gml data...'))
    url = PUNKTYADRESOWE_URL.replace('<teryt>', teryt)
    response = requests.get(url)

    if response.status_code != 200:
        raise ServiceNotFound()

    with open(gml_filename, 'wb') as f:
        f.write(response.content)


def download_punktyadresowe_metadata(teryt: str) -> Optional[str]:
    """
    :param teryt: commune (gmina) id number (6 characters)
    :raises ServiceNotFound, IOError:
    :return XML/GML metadata – capabilities content from punktyadresowe WFS
    """

    logger.info(_('Downloading punktyadresowe metadata...'))
    url = PUNKTYADRESOWE_SOURCE_EMAPA_URL.replace('<teryt>', teryt)
    response = requests.get(url)

    if response.status_code != 200:
        raise ServiceNotFound

    return response.text
