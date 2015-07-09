Wolseley Importing
====

All the importing that needs to be done for Wolseley


Usage
====

It's enough to do:

``IMPORT_CONF=live ./run.py path.to.importer.package.ImporterClass``

where ``IMPORT_CONF`` should be the appropriate environment. It defaults to ``local``.

To pass named arguments:

``./run.py path.to.importer.package.ImporterClass example=value demo=argument list_argument[]=first list_argument[]=second``

To test a job:

``./test.py path.to.importer.package.ImporterClass``


Tests
====

It's enough to do:

``nosetests``
