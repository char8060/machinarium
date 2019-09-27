import unittest
from mock import mock, patch, Mock, MagicMock
import datetime
from machinarium_lambda import set_modules, \
                               get_file, \
                               get_schema, \
                               get_table, \
                               get_partition, \
                               get_metadata, \
                               get_connection, \
                               get_source, \
                               insert_into_updates


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
    def test_get_file_is_correct(self):
        self.assertEqual(get_file("some_dir/file.txt"), 'file.txt')
        self.assertEqual(get_file("file.txt"), 'file.txt')

    def test_get_file_is_raising(self):
        with self.assertRaises(Exception):
            get_file("not_correct_folder/")

    # get_schema()
    def test_get_schema_is_correct(self):
        self.assertEqual(get_schema('s3://gogo-udp-stage/CA/XDW/DIM/DIM_PRODUCT', ['XDW']), 'XDW')
        self.assertEqual(get_schema('s3://gogo-udp-stage/CA/ABS/PARSED_ABS', ['ABS']), 'ABS')
        self.assertEqual(get_schema('s3://gogo-udp-ds-stage/data/opex/dim_flight', ['opex']), 'opex')

    def test_get_schema_is_raising(self):
        object_path = ''
        schemas_list = []
        with self.assertRaises(Exception):
            get_schema(object_path, schemas_list)

    # get_table()
    def test_get_table_is_correct(self):
        object_path_xdw = 'gogo-udp-stage/CA/XDW/DIM/DIM_FLIGHT/YEAR=2019/MONTH=09/'
        schema_xdw = 'xdw'
        table_dict_xdw = {
            'xdw': ['DIM_FLIGHT']
        }
        self.assertEqual(get_table(object_path_xdw, schema_xdw, table_dict_xdw), 'DIM_FLIGHT')

        object_path_opex = 'gogo-udp-ds-stage/data/opex/dim_flight/'
        schema_opex = 'opex'
        table_dict_opex = {
            'opex': ['dim_flight']
        }
        self.assertEqual(get_table(object_path_opex, schema_opex, table_dict_opex), 'dim_flight')

    def test_get_table_is_raising(self):
        object_path = '/not_correct/'
        schema = 'not_correct'
        table_dict = {
            'schema_error': ['table']
        }
        with self.assertRaises(Exception):
            get_table(object_path, schema, table_dict)

    # get_partition()
    def test_get_partition_is_correct(self):
        object_path = 'gogo-udp-ds-stage/data/opex/dim_flight/partition_date=2018-01-01/'
        table = 'dim_flight'
        partition_dict = {
            'dim_flight': ['partition_date']
        }
        self.assertEqual(get_partition(object_path, table, partition_dict), 'partition_date=2018-01-01')

    def test_get_partition_is_correct_multiple_partitions(self):
        object_path = 'data/test/my_table/partition_date=2018-01-01/flight_source=gdw/test_file.txt'
        table = 'table'
        partition_dict = {
            'table': ['partition_date', 'flight_source']
        }
        self.assertEqual(get_partition(object_path, table, partition_dict), 'partition_date=2018-01-01/flight_source=gdw')

        object_path = 'gogo-udp-stage/CA/XDW/DIM/DIM_FLIGHT/YEAR=2019/MONTH=09/'
        table = 'DIM_FLIGHT'
        partition_dict = {
            'DIM_FLIGHT': ['YEAR', 'MONTH']
        }
        self.assertEqual(get_partition(object_path, table, partition_dict), 'YEAR=2019/MONTH=09')

    def test_get_partition_is_raising(self):
        object_path = '/not_correct/'
        table = 'not_correct'
        partition_dict = {
            'not_correct': ['not_correct']
        }
        with self.assertRaises(Exception):
            get_partition(object_path, table, partition_dict)

    # get_metadata()
    def test_get_metadata_is_correct(self):
        schemas = ['test', 'TEST', 'other', 'test.my_table']

        tables = {
            'test': ['my_table'],
            'other': ['BIG_TABLE_NAME', 'MY_TABLE'],
            'TEST': ['table_my']
        }

        partitions = {
            'BIG_TABLE_NAME': ["partition_date"],
            'test.my_table': ["partition_date", "flight_source"],
            'MY_TABLE': ["partition_date"]
        }

        s3_event_object = 'data/test/something/my_table/partition_date=2018-01-01/' \
                          'flight_source=gdw/test_file.txt'

        self.assertEqual(get_metadata(s3_event_object, schemas, tables, partitions), (
            'test',
            'my_table',
            'data/test/something/my_table/partition_date=2018-01-01/flight_source=gdw',
            'test_file.txt',
            'partition_date=2018-01-01/flight_source=gdw'))

    def test_get_metadata_real_cases(self):
        from configs.schema_metadata import SCHEMAS, TABLES, PARTITIONS

        # TODO: add cases for:
        #      - gogo-udp-uexp-prod
        #      - gogo-udp-sla-prod
        #      - gogo-udp-ds-wap-prod
        s3_event_objects = [
            ["gogoabp_catalina_raw/partition_date=2019-08-04/gogoabp-catalina_2f0fca26-904e-4071-86c4-25b6e743a72a.orc",
             "ds",
             "gogoabp_catalina_raw",
             "partition_date=2019-08-04",
             "gogo-udp-ds-catalina-prod"],
            ["source=console/partition_date=2019-09-12/part-00013-0dc66e4a-315a-43c0-a98f-648194350131.c000.snappy",
             "abs",
             "canonical_abs",
             "source=console/partition_date=2019-09-12",
             "gogo-udp-canonical-logs-prod"]
        ]
        for s3_event_object, schema, table, partition, bucket in s3_event_objects:
            source = get_source(bucket)
            result_schema, result_table, result_path, result_file, result_partition = (
                get_metadata(s3_event_object, SCHEMAS, TABLES, PARTITIONS, source)
            )
            self.assertEqual(schema, result_schema)
            self.assertEqual(table, result_table)
            self.assertEqual(partition, result_partition)

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

    def test_get_metadata_w_no_partitions(self):
        s3_event_object = 'data/test/my_table/test_file.txt'
        schemas = ['test', 'TEST', 'other', 'test.my_table']
        tables = {
            'test': ['my_table'],
            'other': ['BIG_TABLE_NAME', 'MY_TABLE'],
        }
        partitions = {
            'test.my_table': [],
            'BIG_TABLE_NAME': ["partition_date"],
            'MY_TABLE': ["partition_date"],
        }

        result = get_metadata(s3_event_object, schemas, tables, partitions)
        expected = ('test', 'my_table', 'data/test/my_table', 'test_file.txt', '')
        self.assertEqual(result, expected)

    @patch('machinarium_lambda.pymysql')
    def test_get_connection(self, mock_sql):
        conn = Mock()
        mock_sql.connect.return_value = conn
        config = {
            'host': 'db.machinarium.gogoair.com',
            'database': 'p2',
            'user': 'machinarium',
            'password': 'pass'
        }
        get_connection(config)
        mock_sql.connect.assert_called_with(**config)

    @patch('machinarium_lambda.pymysql')
    def test_insert_into_updates(self, mock_sql):
        conn = Mock()
        mock_sql.connect.return_value = conn

        cursor = MagicMock()
        mock_result = cursor

        cursor.__enter__.return_value = mock_result
        cursor.__exit__ = MagicMock()

        conn.cursor.return_value = cursor

        insert_into_updates(connection=conn,
                            table='test',
                            path='some_path',
                            file="some_file",
                            partition="some_partition",
                            time=datetime.datetime.now())

        query = '''
            INSERT INTO updates (`table_name`, `file_path`, `file_name`, `partition_name`,`event_time`,
                                 `updated_on`,`updated_by`)
            VALUES ('{table_name}', '{file_path}', '{file_name}', '{partition}', '{event_time}',
                    UTC_TIMESTAMP(), "lambda")
            ON DUPLICATE KEY UPDATE
                `file_name` = '{file_name}',
                `event_time` = '{event_time}',
                `updated_on` =  UTC_TIMESTAMP();
            '''.format(
            table_name='test',
            file_path='some_path',
            file_name='some_file',
            partition='some_partition',
            event_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        mock_result.execute.assert_called_with(query)

    # get_source()
    def test_get_source__is_return_canonical(self):
        self.assertEqual('canonical', get_source('gogo-udp-canonical-logs-'))

    def test_get_source__is_return_wap(self):
        self.assertEqual('wap', get_source('gogo-udp-ds-wap-'))

    def test_get_source__is_return_sla(self):
        self.assertEqual('sla', get_source('gogo-udp-sla-'))

    def test_get_source__is_return_uexp(self):
        self.assertEqual('uexp', get_source('gogo-udp-uexp-'))

    def test_get_source_is_none(self):
        self.assertIsNone(get_source('not_correct_input'))


if __name__ == '__main__':
    unittest.main()
