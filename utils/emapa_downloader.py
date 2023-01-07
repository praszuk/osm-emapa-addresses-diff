import requests
from config import gettext as _, logger
from exceptions import ServiceNotFound


PUNKTYADRESOWE_URL = 'https://www.punktyadresowe.pl/' \
                     'cgi-bin/emuia/<teryt>' \
                     '?service=WFS' \
                     '&request=GetFeature' \
                     '&SRSNAME=urn:ogc:def:crs:EPSG::4326' \
                     '&typenames=ms:punkty_adresowe' \
                     '&version=2.0.0'


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
