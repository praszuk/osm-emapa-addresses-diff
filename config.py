from logging import Formatter, getLogger, LogRecord, INFO, StreamHandler
from gettext import bindtextdomain, textdomain, translation
from locale import getdefaultlocale
from os import path
from sys import stdout
from typing import Final


class Config:
    ROOT_DIR: Final = path.dirname(path.abspath(__file__))
    TRANSLATION_DIR: Final = path.join(ROOT_DIR, 'locales')
    DATA_DIR: Final = path.join(ROOT_DIR, 'data')
    OUTPUT_BASE: Final = path.join(ROOT_DIR, 'out')

    TERYT_TERC: str = ''  # commune (gmina) id – 7 characters str
    AREA_NAME: str = ''   # area name from teryt – commune (gmina) name
    OUTPUT_DIR: str = ''  # path for all output files

    DUPLICATES_EXCLUDE_POI: bool = False
    NO_STREET_NAMES_UPDATE_CHECK: bool = False
    NO_STREET_ALT_NAMES_REPLACE: bool = False
    IGNORE_CASE_SENSITIVE_HOUSENUMBER: bool = False
    IGNORE_STREET_FEATURES: bool = False


class SimpleFormatter(Formatter):
    """
    https://stackoverflow.com/a/68154386
    https://stackoverflow.com/q/59176101
    """
    _LOGGING_DEFAULT_FMT: Final = '%(asctime)s - %(levelname)s - %(message)s'
    _LOGGING_SIMPLE_FMT: Final = '%(message)s'

    _DATE_FMT: Final = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        super().__init__()

        self.datefmt = SimpleFormatter._DATE_FMT

        # Use simple output if 'simple_fmt': True is passed using extra kwargs
        self._default_format = Formatter(SimpleFormatter._LOGGING_DEFAULT_FMT)
        self._simple_format = Formatter(SimpleFormatter._LOGGING_SIMPLE_FMT)

    def format(self, record: LogRecord) -> str:
        if getattr(record, 'simple_fmt', False):
            return self._simple_format.format(record)

        return self._default_format.format(record)


_logger_handler = StreamHandler(stream=stdout)
_logger_handler.setFormatter(SimpleFormatter())
_logger_handler.setLevel(INFO)
logger: Final = getLogger()
logger.setLevel(INFO)
logger.addHandler(_logger_handler)


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
