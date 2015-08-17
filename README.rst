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

To selectively not mock some facilities, eg don't mock saving to DB:

``./test.py path.to.importer.package.ImporterClass --MockRegistry.no_mock_classes[]=DbSaver --MockRegistry.mock_classes[]=DbLoader``

Or, to selectively mock only some facilities, eg mock only fetching:

``./run.py path.to.importer.package.ImporterClass --MockRegistry.mock_classes[]=FtpFetcher --MockRegistry.mock_classes[]=LocalFileDeleter``


Tests
====

It's enough to do:

``nosetests``
