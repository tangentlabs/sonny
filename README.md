Tangent Importer
====

All the importing that needs to be done


Getting started
====

Create a virtual environment, and isntall dependencies via ``make``

```shell
mkvirtualenv tangent-importer
make
```

Usage
====

To see all jobs defined:

```shell
./list.py
```

Copy `conf/local.py-dist` to `conf/local.py`, and make sure the details for the
local DB, and Dashboard instance, are correct

To run a job, with FTP/Email/DB access, it's enough to do:

```shell
./run.py path.to.importer.package.ImporterClass
```

To test a job, which mocks most functionality with side effects (eg FTP, DB, etc):

```shell
./test.py path.to.importer.package.ImporterClass
```

In dev/production environment prepend with `IMPORT_CONF=<environment>`,

where `IMPORT_CONF` should be the appropriate environment. It defaults to
`local`.


Customising runs
====

To pass named arguments:

```shell
./run.py importer example=value demo=argument list_argument[]=first list_argument[]=second
```

To pass a boolean:

```shell
./run.py importer flag1?=True flag2?=False
```

To pass facility settings overrides:

```shell
./run.py importer importer_arg=value --FacilityName.setting_name=value
```


Useful CLI facility overrides
====

To limit the amount of logs:

```shell
./test.py importer --InMemoryLogger.log_level='INFO'
```

To selectively not mock some facilities, eg don't mock saving to/loading from DB:

```shell
./test.py importer --MockRegistry.no_mock_classes[]=DbSaver --MockRegistry.mock_classes[]=DbLoader
```

Or, to selectively mock only some facilities, eg mock only fetching:

```shell
./run.py importer --MockRegistry.mock_classes[]=FtpFetcher --MockRegistry.mock_classes[]=LocalFileDeleter
```

When testing locally, you can use the importer's scripts to setup and tear down
the DB:

```shell
./run.py importer --TemporaryDB.force_run?=True
```


Tests
====

It's enough to do:

```shell
nosetests
```


Dashboard
====

To use your local [dashboard](http://github.com/tangentlabs/tangent-importer-dashboard) , you can register the jobs available:

```shell
./run.py import_jobs.register_jobs_to_dashboard.RegisterJobsToDashboard
```
