#!/bin/sh

cd sonny

IMPORT_CONF=sonny.testing_conf nosetests "$@"  --ignore-files="test_temporary_.+\.py"

