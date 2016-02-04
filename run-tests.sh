#!/bin/sh

cd tangent_importer

IMPORT_CONF=tangent_importer.testing_conf nosetests "$@"

