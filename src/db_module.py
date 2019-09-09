import pymysql
class MySQLConn:
    _conn = None
    def __init__(self):
        pass
    def get_connection(self, metalayer_config):
        """
        Returns an pymysql connection object.
        Otherwise raises an error.
        :return: conn; Object to interact with MySQL server.
        """
        conn = pymysql.connect(**metalayer_config)
        return conn
db_mysql = MySQLConn()