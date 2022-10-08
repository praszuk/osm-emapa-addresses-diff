from gettext import bindtextdomain, textdomain, translation
from locale import getdefaultlocale
from os import path
from typing import Final


class Config:
    ROOT_DIR: Final = path.dirname(path.abspath(__file__))
    TRANSLATION_DIR: Final = path.join(ROOT_DIR, 'locales')
    DATA_DIR: Final = path.join(ROOT_DIR, 'data')
    OUTPUT_BASE: Final = path.join(ROOT_DIR, 'out')

    TERYT_TERC: str = ''  # commune (gmina) id – 7 characters str
    AREA_NAME: str = ''   # area name from teryt – commune (gmina) name
    OUTPUT_DIR: str = ''  # path for all output files


_lang_translations: Final = translation(
    'base',
    localedir=Config.TRANSLATION_DIR,
    languages=[getdefaultlocale()[0]]
)
# https://stackoverflow.com/a/35964548
bindtextdomain('argparse', Config.TRANSLATION_DIR)
textdomain('argparse')
_lang_translations.install()
gettext: Final = _lang_translations.gettext
