#!/usr/bin/env python

import sys
from pydoc import locate


def main():
    sysargs = sys.argv[1:]
    if not sysargs:
        raise Exception("First argument must be the package & class name of "
                        "the import job")

    package_and_class_name, args = sysargs[0], sysargs[1:]
    importer_class = locate(package_and_class_name)
    importer_class.run_from_command_line(args)

if __name__ == '__main__':
    main()
