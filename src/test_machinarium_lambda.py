import unittest
import pymysql
from mock import mock, patch, MagicMock, call, Mock
import db_module
from db_module import db_mysql

from machinarium_lambda import set_modules, \
                               get_connection, \
                               insert_into_updates, \
                               get_file, \
                               get_schema, \
                               get_table, \
                               get_partition, \
                               get_metadata


class TestLambda(unittest.TestCase):

    # set_modules()
    def test_set_modules_stage(self):
        self.assertIsNotNone(set_modules("stage"))

    def test_set_modules_prod(self):
        self.assertIsNotNone(set_modules("prod"))

    def test_set_modules_is_raising(self):
        with self.assertRaises(Exception):
            set_modules("not_correct_env_name")

    # get_file()
    def test_get_file_is_not_none(self):
        self.assertIsNotNone(get_file("some_dir/file.txt"))

    def test_get_file_is_raising(self):
        with self.assertRaises(Exception):
            get_file("not_correct_folder/")

    # get_schema()
    def test_get_schema_is_true(self):
        object_path = '/abs/'
        schemas_list = ['abs']
        self.assertTrue(get_schema(object_path, schemas_list))

    def test_get_schema_is_raising(self):
        object_path = ''
        schemas_list = []
        with self.assertRaises(Exception):
            get_schema(object_path, schemas_list)

    # get_table()
    def test_get_table_is_true(self):
        object_path = '/abs/table_name/'
        schema = 'abs'
        table_dict = {
            'abs': ['table_name']
        }
        self.assertTrue(get_table(object_path, schema, table_dict))

    def test_get_table_is_raising(self):
        object_path = '/not_correct/'
        schema = 'not_correct'
        table_dict = {
            'schema_error': ['table']
        }
        with self.assertRaises(Exception):
            get_table(object_path, schema, table_dict)

    # get_partition()
    def test_get_partition_is_true(self):
        object_path = '/dir1/partition_name=/dir3/'
        table = 'table'
        partition_dict = {
            'table': ['partition_name']
        }
        self.assertTrue(get_partition(object_path, table, partition_dict))

    def test_get_partition_is_raising(self):
        object_path = '/not_correct/'
        table = 'not_correct'
        partition_dict = {
            'not_correct': ['not_correct']
        }
        with self.assertRaises(Exception):
            get_partition(object_path, table, partition_dict)

    # get_metadata()
    # docstring in get_metadata is not correct.
    def test_get_metadata_is_true(self):
        object_path = 'schema/abs/table/p1=/p2=/file.txt'
        schemas_list = ['abs']
        tables_dict = {
            'abs': ['table']
        }
        partitions_dict = {
            'abs.table': ['p1', 'p2']
        }
        self.assertTrue(get_metadata(object_path, schemas_list, tables_dict, partitions_dict))

    def test_get_metadata_is_raising(self):
        object_path = 'not_correct'
        schemas_list = ['not_correct']
        tables_dict = {
            'not_correct': ['not_correct']
        }
        partitions_dict = {
            'not_correct': ['not_correct', 'not_correct']
        }
        with self.assertRaises(Exception):
            get_metadata(object_path, schemas_list, tables_dict, partitions_dict)

    @patch('db_module.pymysql')
    def test_get_connection(self, mock_sql):
        self.assertIs(db_module.pymysql, mock_sql)
        conn = Mock()
        mock_sql.connect.return_value = conn
        config = {
            'host': 'db.machinarium.stage.gogoair.com',
            'database': 'p2',
            'user': 'machinarium',
            'password': 'mc#Ku1P'
        }
        db_mysql.get_connection(config)
        mock_sql.connect.assert_called_with(**config)


if __name__ == '__main__':
    unittest.main()