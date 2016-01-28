#!/usr/bin/env python

from infrastructure.discover_jobs import get_importers_names


def list_importers(*args, **kwargs):
    names, failures = get_importers_names(*args, **kwargs)

    if failures:
        print '-' * 40
        print 'Could not load the following pacakges due to errors'
        print '\n'.join(sorted(failures))
        print '-' * 40

    print '\n'.join(sorted(names))


if __name__ == '__main__':
    list_importers()
