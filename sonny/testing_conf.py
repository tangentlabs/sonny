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

push_notification_registry = {
    "default": {
        "url": "https://notify.tangentlabs.co.uk",
        "system": "wlshub",
        "subSystem": 1,
        "title": "Importer job completed",
        "body": "Job '%s' completed with %s errors!",
        "icon": "https://www.tangent.co.uk/static/favicon-2.jpg",
        "link": "https://www.tangent.co.uk",
        "highPriority": False,
        "ttl": 5,
    }
}


DASHBOARD_URL = None
