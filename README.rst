Tangent Importing
==

All the importing that needs to be done


Usage
====

It's enough to do:

``IMPORT_CONF=live python -m path.to.importer.package``

where ``IMPORT_CONF`` should be the appropriate environment. It defaults to ``local``.

To pass arguments:

``python -m path.to.importer.package run arg1 arg2 -- param3=arg3 param4=arg4``

To test a job:

``python -m path.to.importer.package test arg1 arg2 -- param3=arg3 param4=arg4``


Tests
====

It's enough to do:

``nosetests``
