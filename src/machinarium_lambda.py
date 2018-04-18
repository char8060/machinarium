from datetime import datetime
from os.path import split
import urllib
import logging
import pymysql
from importlib import import_module
from configs.schema_metadata import SCHEMAS, TABLES, PARTITIONS


# DevOps configs data
ACCOUNTS = {
    '623692085147': 'sandbox',
    '222572804561': 'dev',
    '169442230877': 'stage',
    '549963816193': 'prod'
}

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Lambda was triggered")


def set_modules(env_name):
    """
    Returns a module with necessary configs.
    Otherwise raises an error.

    :param env_name: Environment variable. Type = String
    :return: Module object.
    """

    try:
        return import_module('configs' + '.' + env_name)
    except Exception:
        logger.error('Module could not be imported!')
        raise Exception('{}: Module could not be imported!'.format(Exception))


def get_connection(metalayer_config):
    """
    Returns an pymysql connection object.
    Otherwise raises an error.

    :return: conn; Object to interact with MySQL server.
    """
    try:
        logger.info("Getting connection to to RDS instance")
        conn = pymysql.connect(**metalayer_config)
        logger.info("Connected to RDS instance")
        return conn
    except Exception as err:
        logger.error("{exception}. "
                     "Could not connect to the RDS instance. "
                     "Host: {host}, Database: {db}, User: {user}, Port: {port}, Connection timeout: {con_tout}"
                     .format(exception=err,
                             host=metalayer_config['host'],
                             db=metalayer_config['database'],
                             user=metalayer_config['user'],
                             port=metalayer_config['port'],
                             con_tout=metalayer_config['connect_timeout']))
        raise Exception


def insert_into_updates(connection, table, path, file, partition, time):
    """
    Executes insert query to store metadata about table update.

    :param connection: pymysql.connect() connection.
    :param table: table name, where file was updated/created.
    :param path: path to the new file. Type = String
    :param file: file name. Type = String
    :param partition: partition where file was updated/created. Type = String
    :param time: updated time. Datetime object.
    """
    query = ''' 
            INSERT INTO updates (`table_name`, `file_path`, `file_name`, `partition_name`,`updated_on`,`updated_by`) 
            VALUES ('{table_name}', '{file_path}', '{file_name}', '{partition}', '{updated_on}', "lambda")
            ON DUPLICATE KEY UPDATE
                `file_name` = '{file_name}',
                `updated_on` = '{updated_on}';
            '''.format(
                table_name=table,
                file_path=path,
                file_name=file,
                partition=partition,
                updated_on=time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        with connection.cursor() as cur:
            cur.execute(query)
            connection.commit()
    except Exception as err:
        logger.error("{exception}. "
                     "Can not execute {query}.".format(exception=err, query=query))
        raise Exception


def get_file(object_path):
    """
    Returns a file name if exists.
    Otherwise raises an exception.

    :param object_path: String with file name and path to this file. Type = String
    :return: file. Type = String
    """
    path, file = split(object_path)
    if file != '':
        return file
    else:
        warning = "There is no file to update table"
        logger.warning(warning)
        raise Exception(warning)


def get_schema(object_path, schemas_list):
    """
    Returns a schema name if there is valid example in `object_path`.
    Otherwise raises an exception.

    :param object_path: String with file name and path to this file. Type = String
    :param schemas_list: List of schemas in config file. Type = List
    :return: schema. Type = String
    """
    schema = None

    # Check if there is a schema we track
    collect_list = list()
    for element in schemas_list:
        if "/{}/".format(element) in object_path:
            # We are taking the first schema we meet in event string
            schema, index = element, object_path.index("/{}/".format(element))
            collect_list.append((index, schema))

    if schema is not None:
        temp = dict(collect_list)
        return temp[min(temp.keys())]
    else:
        warning = "{event} doesn't consist a schema from  this list: {schemas}".format(event=object_path,
                                                                                       schemas=schemas_list)
        logger.warning(warning)
        raise Exception(warning)


def get_table(object_path, schema, tables_dict):
    """
    Returns a table name from a tables list if it exists in `object_path`.
    Otherwise raises an exception.

    :param object_path: tring with file name and path to this file. Type = String
    :param schema: Schema name to get a list of tables from config file. Type = String
    :param tables_dict: A dictionary. Type = Dictionary. Key: schema name
                                                         Value: list of tables.
    :return: table. Type = String
    """
    table = None
    schema_tables = tables_dict[schema]
    for element in schema_tables:
        if "/{}/".format(element) in object_path:
            table = element
            # We assume there is only one table name
            break

    if table is not None:
        return table
    else:
        warning = "{event} doesn't match with configs structure. " \
                  "For [{schema}] schema a table from the list is expected. " \
                  "List: {tables}".format(event=object_path, schema=schema, tables=schema_tables)
        logger.warning(warning)
        raise Exception(warning)


def get_partition(object_path, table, partitions_dict):
    """
    Returns partition part of the `object_path`.
    Raise am exception if there is a mismatching with configs.

    :param object_path: tring with file name and path to this file. Type = String
    :param table: Table name to get a list of partitions from config file. Type = String
    :param partitions_dict: A dictionary. Type = Dictionary. Key: schema.table string.
                                                             Value: list of partitions.
    :return: partition. Type = String ( can be a sequence like 'year=.../month=...')
    """
    partition = ''

    partitions_from_event_object = []
    partitions_check_list = []

    table_partitions = partitions_dict[table]

    for element in split(object_path)[0].split('/'):
        if '=' in element:
            partitions_from_event_object.append(element)
            partitions_check_list.append(element.split('=')[0])

    # Mismatching partitions
    symmetric_set_difference = set(partitions_check_list).symmetric_difference(set(table_partitions))
    if ((len(partitions_check_list) != len(table_partitions)) |
            (len(symmetric_set_difference) != 0)):

        warning = "{event} doesn't match with configs structure. " \
                  "For {table} the next partitions are expected: {p1} " \
                  "Gotten partitions: {p2}".format(event=object_path,
                                                   table=table,
                                                   p1=table_partitions,
                                                   p2=partitions_check_list)
        logger.warning(warning)
        raise Exception(warning)

    for element in partitions_from_event_object:
        partition += '/' + element

    # Inconsistency
    if partition not in object_path:
        warning = "Structure is broken. " \
                  "There is no {tbl_and_prt} in {s3_metadata}".format(tbl_and_prt=partition,
                                                                      s3_metadata=object_path)
        logger.warning(warning)
        raise Exception(warning)

    # Remove '/' on the beginning and return partition part of the path
    return partition[1:]


def get_metadata(object_path, schemas_list, tables_dict, partitions_dict):
    """
    Returns parsed metadata from object_path.

    :param object_path: String with file name and path to this file. Type = String
    :param schemas_list: List of schemas in config file. Type = List
    :param tables_dict: List of tables for particular schema in config file. Type = List
    :param partitions_dict: List of partitions for particular schema in config file. Type = List
    :return: schema, table, path, file, partition. Type = String (for all values)
    """
    file = get_file(object_path)
    schema = get_schema(object_path, schemas_list)
    table = get_table(object_path, schema, tables_dict)
    partition = get_partition(object_path, (schema + '.' + table).lower(), partitions_dict)

    # Inconsistency
    if table + '/' + partition not in object_path:
        warning = "There is no {tbl_and_prt} in {object_path}".format(tbl_and_prt=table + '/' + partition,
                                                                      object_path=object_path)
        logger.warning(warning)
        raise Exception(warning)

    path = split(object_path)[0]
    return schema, table, path, file, partition


def lambda_handler(event, context):
    """
    Entry point for AWS Lambada function.
    More details are here: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
    About "context":  https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    :param event: S3 metadata in JSON like format. Type = String
    :param context: runtime information; object.
    """
    env = ACCOUNTS[context.invoked_function_arn.split(":")[4]].lower()

    env_config = set_modules(env)
    metalayer_configs = env_config.metalayer_config

    logger.info("Event: {}".format(event))
    bucket = urllib.unquote_plus(event['Records'][0]['s3']['bucket']['name'].encode('utf8'))
    logger.info("S3 bucket: {}".format(bucket))
    object_path = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    logger.info("S3 object: {}".format(object_path))

    schema, table, path, file, partition = get_metadata(object_path, SCHEMAS, TABLES, PARTITIONS)

    table = "{schema}.{table}".format(schema=schema.lower(), table=table.lower())

    event_time = datetime.strptime(event['Records'][0]['eventTime'], "%Y-%m-%dT%H:%M:%S.%fZ")

    logger.info("Table: {}".format(table))
    logger.info("File path on S3: {bucket}/{path}".format(bucket=bucket, path=path))
    logger.info("File:{}".format(file))
    logger.info("Partition(s): {}".format(partition))
    logger.info("Updated time: {}".format(event_time))

    conn = get_connection(metalayer_configs)
    insert_into_updates(connection=conn, table=table, path=path, file=file, partition=partition, time=event_time)

    conn.close()
    logger.info("Done. Table is updated")
