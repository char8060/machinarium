# RDS MySQL instance
metalayer_config = {
    'host': 'db.machinarium.prod.gogoair.com',
    'database': 'p2',
    'user': 'machinarium',
    'password': '',
    'port': 3306,
    'connect_timeout': 10
}


# For instrumentation
S3 = 'gogo-udp-ds-prod'
DIR = 'logs/machinarium/instrumentation'