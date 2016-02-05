#!/bin/sh

cd sonny

IMPORT_CONF=sonny.testing_conf nosetests "$@"

