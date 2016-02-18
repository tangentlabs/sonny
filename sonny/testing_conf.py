from sonny.conf.default import * # noqa

environment = 'testing'

db_registry = {
    "test_mysql": {
        "host": "127.0.0.1",
        "port": 3306,
        "username": "root",
        "password": "password",
        "is_disposable": True,
        "database": "test",
        "connector_name": "MySql",
    },
    "test_postgres": {
        "host": "127.0.0.1",
        "port": 5432,
        "username": "postgres",
        "password": " ",
        "is_disposable": True,
        "database": "test",
        "connector_name": "Postgres",
    },
}

ftp_registry = {
}

email_registry = {
}

DASHBOARD_URL = None
