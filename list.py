#!/usr/bin/env python

from pydoc import locate
import pkgutil

import import_jobs
from import_jobs.base import BaseImporter


def get_subpackages_recursive(package, is_package=True):
    if not is_package:
        return []

    return sum([
        [locate(modname)] + get_subpackages_recursive(locate(modname), sub_package_is_package)
        for _, modname, sub_package_is_package
        in pkgutil.iter_modules(package.__path__, package.__name__ + '.')
    ], [])


def get_importer_classes(packages):
    potentional_importers = [
        getattr(package, name)
        for package in packages
        for name in dir(package)
    ]
    return set(
        potentional_importer
        for potentional_importer in potentional_importers
        if type(potentional_importer) == type(BaseImporter)
        and issubclass(potentional_importer, BaseImporter)
        and potentional_importer != BaseImporter
    )


def get_classes_full_names(classes):
    return [
        '%s.%s' % (_class.__module__, _class.__name__)
        for _class in classes
    ]


def list_importers():
    sub_packages = get_subpackages_recursive(import_jobs)
    importers = get_importer_classes(sub_packages)
    names = get_classes_full_names(importers)

    print '\n'.join(sorted(names))


def main():
    list_importers()


if __name__ == '__main__':
    main()
