Tangent Importing
==

All the importing that needs to be done


Usage
====

To see all jobs defined:

``./list.py``

To run a job it's enough to do:

``IMPORT_CONF=live ./run.py path.to.importer.package.ImporterClass``

where ``IMPORT_CONF`` should be the appropriate environment. It defaults to ``local``.

To pass named arguments:

``./run.py path.to.importer.package.ImporterClass example=value demo=argument list_argument[]=first list_argument[]=second``

To pass facility settings overrides:

``./run.py path.to.impoerter.package.ImporterClass importer_arg=value --FacilityName.setting_name=value``

To test a job, which mocks most functionality with side effects (eg FTP, DB, etc):

``./test.py path.to.importer.package.ImporterClass``


Tests
====

It's enough to do:

``nosetests``
