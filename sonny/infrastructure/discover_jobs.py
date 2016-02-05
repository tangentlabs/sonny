#!/usr/bin/env python

from pydoc import locate
import pkgutil
import inspect

from sonny import utils

from sonny.import_jobs.base import Importer


def import_package(package_name):
    base_package = __import__(package_name)
    package_path_parts = package_name.split('.')

    package = base_package
    for part in package_path_parts[1:]:
        package = getattr(package, part)

    return package


def get_importers_packages(importers_packages_names=None):
    if importers_packages_names is None:
        _, config = utils.get_config_module()
        importers_packages_names = config.IMPORTERS_PACKAGES_NAMES

    return map(import_package, importers_packages_names)


def get_importers_subpackages(importers_packages_names=None):
    importers_packages = get_importers_packages(
        importers_packages_names=importers_packages_names)
    sub_packages, failures = get_subpackages(importers_packages)

    return sub_packages, failures


def get_subpackages(packages):
    subpackages = []
    failures = set()

    for package in packages:
        subpackages += list(_get_subpackages_recursive_generator(
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


def get_importer_classes(
        packages=None, importers_packages_names=None, testable_only=False):
    failures = []
    if packages is None:
        packages, failures = get_importers_subpackages(
            importers_packages_names=importers_packages_names)

    potentional_importers = [
        getattr(package, name)
        for package in packages
        for name in dir(package)
    ]
    importer_classes = set(
        potentional_importer
        for potentional_importer in potentional_importers
        if is_concrete_importer(potentional_importer)
        and ((not testable_only) or potentional_importer.is_testable)
    )

    return importer_classes, failures


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


def get_importers_names(importers_packages_names=None, testable_only=False):
    importers, failures = get_importer_classes(
        importers_packages_names=importers_packages_names,
        testable_only=testable_only,
    )
    names = get_classes_full_names(importers)

    return names, failures


def get_importers_details(importers_packages_names=None, testable_only=False):
    importers, failures = get_importer_classes(
        importers_packages_names=importers_packages_names,
        testable_only=testable_only,
    )
    details = get_importer_details(importers)

    return {
        "importers": details,
        "failures": sorted(failures),
    }
