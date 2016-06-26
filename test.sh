#!/bin/bash
pip install -q --upgrade $(python -c "from fantail.tests import tests_require ; print(' '.join(tests_require))")
py.test -l -v --cov=fantail --cov-report term-missing
