#!/bin/sh

cd sonny
# The `test_temporary_*.py` files contain tests which require database backends to be installed.
# For this reason we ignore them here, but you can run them if you install MySQL and Postgres

IMPORT_CONF=sonny.testing_conf nosetests "$@"  --ignore-files="test_temporary_.+\.py"

