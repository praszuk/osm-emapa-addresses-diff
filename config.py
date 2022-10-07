from gettext import translation
from locale import getdefaultlocale
from os import path
from typing import Final


class Config:
    ROOT_DIR: Final = path.dirname(path.abspath(__file__))
    OUTPUT_BASE: Final = path.join(ROOT_DIR, 'out')

    _lang_translations: Final = translation(
        'base',
        localedir=path.join(ROOT_DIR, 'locales'),
        languages=[getdefaultlocale()[0]]
    )
    _lang_translations.install()
    gettext: Final = _lang_translations.gettext

    TERYT_TERC: str = ''  # commune (gmina) id – 7 characters str
    AREA_NAME: str = ''   # area name from teryt – commune (gmina) name
    OUTPUT_DIR: str = ''  # path for all output files
