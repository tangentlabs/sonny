#!/usr/bin/env python

from pydoc import locate
import pkgutil
import inspect

import import_jobs
from import_jobs.base import Importer


def get_subpackages(package):
    failures = set()
    subpackages = list(_get_subpackages_recursive_generator(
        package, failures=failures))

    return subpackages, failures


def _get_subpackages_recursive_generator(package, is_package=True, failures=None):
    if not is_package:
        return

    if failures is None:
        failures = set()

    modules = pkgutil.iter_modules(package.__path__, package.__name__ + '.')
    for _, modname, sub_package_is_package in modules:
        try:
            this_subpackage = locate(modname)
        except Exception:
            failures.add(modname)
        else:
            yield this_subpackage

        try:
            subpackages_recursive = _get_subpackages_recursive_generator(
                locate(modname), is_package=sub_package_is_package,
                failures=failures)
        except Exception:
            failures.add(modname)
        else:
            for subpackage in subpackages_recursive:
                yield subpackage


def get_importer_classes(packages):
    potentional_importers = [
        getattr(package, name)
        for package in packages
        for name in dir(package)
    ]
    return set(
        potentional_importer
        for potentional_importer in potentional_importers
        if is_concrete_importer(potentional_importer)
    )


def is_concrete_importer(potentional_importer):
    if not issubclass(type(potentional_importer), type):
        return False
    if inspect.isabstract(potentional_importer):
        return False
    if not issubclass(potentional_importer, Importer):
        return False

    return True


def get_classes_full_names(classes):
    return [
        '%s.%s' % (_class.__module__, _class.__name__)
        for _class in classes
    ]


def get_importer_details(classes):
    return [
        {
            "name": _class.get_name(),
            "uuid": _class.uuid,
        }
        for _class in classes
    ]


def get_importers_names():
    sub_packages, failures = get_subpackages(import_jobs)
    importers = get_importer_classes(sub_packages)
    names = get_classes_full_names(importers)

    return names, failures


def get_importers_details():
    sub_packages, failures = get_subpackages(import_jobs)
    importers = get_importer_classes(sub_packages)
    details = get_importer_details(importers)

    return {
        "importers": details,
        "failures": sorted(failures),
    }
