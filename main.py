import json
import logging
import pathlib
import sys

from argparse import ArgumentParser
from os import path
from typing import Any, Dict, List, Optional, Tuple

from analyze import (
    addr_type_distribution,
    addr_tags_distribution,
    addr_duplicates,
    addr_missing
)
from address import Address, OsmAddress
from config import Config
from config import gettext as _
from parsers.emapa import parse_emapa_file
from parsers.teryt import parse_teryt_terc_file
from exceptions import TerytNotFound, EmapaServiceNotFound
from utils.alt_street_names import (
    parse_streets_names_from_elements,
    replace_streets_with_osm_alt_names
)
from utils.emapa_downloader import download_emapa_csv
from utils.overpass import (
    download_osm_data,
    is_element,
    QUERY_ADDR,
    QUERY_STREET
)
from utils.street_names_mappings import (
    replace_streets_with_osm_names,
    STREET_NAMES_FILENAME
)


TERYT_TERC_FILE: str = path.join(Config.DATA_DIR, 'terc.csv')


def download_emapa_addresses() -> List[Address]:
    try:
        csv_filename = path.join(Config.OUTPUT_DIR, 'emapa_addresses_raw.csv')
        local_system_url = download_emapa_csv(Config.TERYT_TERC, csv_filename)

    except TerytNotFound:
        logging.error(
            _('Teryt {} not found at GUGiK website!').format(Config.TERYT_TERC)
        )
        sys.exit(2)
    except EmapaServiceNotFound:
        logging.error(
            _('Not found e-mapa service for teryt: {}').format(
                Config.TERYT_TERC
            )
        )
        sys.exit(3)
    except IOError as err:
        logging.error(_('Error with downloading/saving data: {}').format(err))
        sys.exit(4)

    emapa_addresess: List[Address] = parse_emapa_file(
        csv_filename,
        local_system_url
    )
    for addr in emapa_addresess:
        addr.source_addr = local_system_url

    logging.info(_('Parsed {} e-mapa addresses.').format(len(emapa_addresess)))
    return emapa_addresess


def download_osm_addresses() -> List[OsmAddress]:
    osm_data: Optional[Dict[str, Any]] = download_osm_data(
        Config.TERYT_TERC,
        QUERY_ADDR
    )
    if osm_data is None:
        logging.error(
            _('Error with downloading OSM (Overpass) addresses data.')
        )
        sys.exit(4)

    elements: List[Dict[str, Any]] = list(
        filter(is_element, osm_data['elements'])
    )

    logging.debug(_('Downloaded {} OSM addresses elements.').format(
        len(elements))
    )
    osm_addresses: List[OsmAddress] = list(
        map(OsmAddress.parse_from_osm_element, elements)
    )
    logging.info(_('Parsed {} OSM addresses.').format(len(osm_addresses)))

    return osm_addresses


def download_osm_alt_streets_names() -> Dict[str, str]:
    osm_data: Optional[Dict[str, Any]] = download_osm_data(
        Config.TERYT_TERC,
        QUERY_STREET
    )
    if osm_data is None:
        logging.error(
            _('Error with downloading OSM (Overpass) street names data.')
        )
        sys.exit(4)

    elements: List[Dict[str, Any]] = osm_data['elements']
    logging.debug(
        _('Downloaded {} OSM street elements.').format(len(elements))
    )

    osm_streets: Dict[str, str] = parse_streets_names_from_elements(elements)
    unique_street = set(w['tags']['name'] for w in elements)
    logging.info(
        _('Parsed {} OSM unique streets with {} alternate names.').format(
            len(unique_street),
            len(osm_streets)
        )
    )

    return osm_streets

def report_osm_type(osm_addresses: List[OsmAddress]) -> str:
    osm_type_dist = addr_type_distribution(osm_addresses).most_common()
    return _('OSM object type:') + ' \n{}'.format(
        '\n'.join(f'{k}: {v}' for k, v in osm_type_dist)
    )


def report_key_value_distribution(osm_addresses: List[OsmAddress]) -> str:
    kv_dist: List[Tuple] = addr_tags_distribution(osm_addresses).most_common()
    return _('Key-values distribution:') + '\n{}'.format(
        '\n'.join(
            f'{k}: {v} ({v * 100 / len(osm_addresses):.2f}%)'
            for k, v in kv_dist
        )
    )


def report_duplicates(
    duplicated_addresses: List[List[OsmAddress]],
    osm_address: List[OsmAddress]
) -> str:
    return _('Duplicated OSM addresses:') + ' {}/{} ({:.2f}%)'.format(
        len(duplicated_addresses),
        len(osm_address),
        len(duplicated_addresses) * 100 / len(osm_address)
    )


def save_missing_addresses(missing_emapa_addresses: List[Address]) -> None:
    geojson: Dict[str, Any] = Address.addresses_to_geojson(
        missing_emapa_addresses
    )
    filename = 'emapa_addresses_missing.geojson'
    with open(path.join(Config.OUTPUT_DIR, filename), 'w') as f:
        json.dump(geojson, f, indent=4)


def save_duplicated_addresses(
    duplicated_osm_addresses: List[List[OsmAddress]]
) -> None:
    assert type(duplicated_osm_addresses[0][0]) == OsmAddress

    filename = 'osm_addresses_duplicates.txt'
    with open(path.join(Config.OUTPUT_DIR, filename), 'w') as f:
        f.write(
            '# ' + _(
                'You can load it in the JOSM '
                'using "Download object" function (CTRL + SHIFT + O).'
            )
        )
        f.write('\n# ' + _('Each line is for 1 address'))

        for duplication_block in duplicated_osm_addresses:
            shorten_osm_obj_sequence = ','.join([
                addr.shorten_osm_obj for addr in duplication_block
            ])
            f.write('\n' + shorten_osm_obj_sequence)


def save_excess_addresses(excess_osm_addresses: List[OsmAddress]) -> None:
    assert type(excess_osm_addresses[0]) == OsmAddress

    shorten_osm_obj_sequence = ','.join([
        addr.shorten_osm_obj for addr in excess_osm_addresses
    ])
    filename = 'osm_addresses_excess.txt'
    with open(path.join(Config.OUTPUT_DIR, filename), 'w') as f:
        f.write(
            '# ' + _(
                'You can load it in the JOSM '
                'using "Download object" function (CTRL + SHIFT + O).'
            )
        )
        f.write('\n' + shorten_osm_obj_sequence)


def save_all_emapa_addresses(emapa_addresses: List[Address]) -> None:
    geojson: Dict[str, Any] = Address.addresses_to_geojson(emapa_addresses)

    filename = 'emapa_addresses_all.geojson'
    with open(path.join(Config.OUTPUT_DIR, filename), 'w') as f:
        json.dump(geojson, f, indent=4)


def main():
    # Create teryt_terc output directory if not exists
    pathlib.Path(Config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Download e-mapa and OSM adddresses and streets
    emapa_addresses: List[Address] = download_emapa_addresses()
    replace_streets_with_osm_names(emapa_addresses)
    osm_addresses: List[OsmAddress] = download_osm_addresses()

    osm_alt_streets_names = download_osm_alt_streets_names()
    replace_streets_with_osm_alt_names(emapa_addresses, osm_alt_streets_names)

    # Analysis reports
    print('\n')
    print(report_osm_type(osm_addresses), end='\n\n')
    print(report_key_value_distribution(osm_addresses), end='\n\n')

    duplicated_osm_addresses = addr_duplicates(osm_addresses)
    print(
        report_duplicates(duplicated_osm_addresses, osm_addresses),
        end='\n\n'
    )

    missing_emapa_addresses = addr_missing(osm_addresses, emapa_addresses)
    print(_('Missing OSM addresses which exist in the e-mapa: {}').format(
        len(missing_emapa_addresses)
    ))

    excess_osm_addresses: List[OsmAddress] = addr_missing(
        emapa_addresses,
        osm_addresses
    )
    print(
        _('Excess OSM addresses which do not exist in the e-mapa: {}').format(
            len(excess_osm_addresses)
        )
    )

    # Save data to files
    save_duplicated_addresses(duplicated_osm_addresses)
    save_missing_addresses(missing_emapa_addresses)
    save_excess_addresses(excess_osm_addresses)
    save_all_emapa_addresses(emapa_addresses)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Parse and check arguments from user input
    parser = ArgumentParser()
    parser.add_argument(
        'teryt_terc',
        help=_('id of commune (gmina) – 7 characters.'),
        type=str,
    )
    parser.add_argument(
        '--duplicates-exclude-poi',
        help=_(
            'exclude addresses on POI objects from duplicates '
            '(skipping POI with building key).'
        ),
        action='store_true',
        dest='duplicates_exclude_poi'
    )
    parser.add_argument(
        '--no-street-names-update-check',
        help=_('skip checking update for the {} file from GitHub.').format(
            STREET_NAMES_FILENAME
        ),
        action='store_true',
        dest='no_street_names_update_check'
    )
    parser.add_argument(
        '-icsh',
        '--ignore-case-sensitive-housenumber',
        help=_(
            'ignore difference between capital and lower-case letters '
            'for house numbers e.g. 12a will be processed same as 12A.'
        ),
        action='store_true',
        dest='ignore_cs_housenumber'
    )
    parser.add_argument(
        '-isf',
        '--ignore-street-features',
        help=_(
            'ignore ULIC features in street names such as "al." or "plac".'
        ),
        action='store_true',
        dest='ignore_street_features'
    )
    args = parser.parse_args()

    teryt_terc: str = args.teryt_terc
    try:
        area_name = parse_teryt_terc_file(TERYT_TERC_FILE, teryt_terc)
        logging.info(
            _('Parsed teryt_terc ({}) as: {}').format(teryt_terc, area_name)
        )
    except (ValueError, IOError) as e:
        logging.error(_('Cannot parse teryt terc parameter!') + f' {e}')
        sys.exit(1)

    Config.TERYT_TERC = teryt_terc
    Config.AREA_NAME = area_name
    Config.OUTPUT_DIR = path.join(Config.OUTPUT_BASE, teryt_terc)
    Config.DUPLICATES_EXCLUDE_POI = args.duplicates_exclude_poi
    Config.NO_STREET_NAMES_UPDATE_CHECK = args.no_street_names_update_check
    Config.IGNORE_CASE_SENSITIVE_HOUSENUMBER = args.ignore_cs_housenumber
    Config.IGNORE_STREET_FEATURES = args.ignore_street_features

    main()
