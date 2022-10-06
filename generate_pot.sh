#!/bin/bash
# Generate trasnlation .pot file – locales/base.pot
find . -iname "*.py" | xargs xgettext --from-code=utf-8 -d base -o locales/base.pot