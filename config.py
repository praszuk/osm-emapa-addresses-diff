from gettext import translation
from locale import getdefaultlocale
from os import path


ROOT_DIR = path.dirname(path.abspath(__file__))

_lang, _codeset = getdefaultlocale()
_lang_translations = translation(
    'base',
    localedir=path.join(ROOT_DIR, 'locales'),
    languages=[_lang]
)
_lang_translations.install()
gettext = _lang_translations.gettext
