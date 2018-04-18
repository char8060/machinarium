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
    Execute insert query to store metadata about table update.

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


def get_file(s3_event_object):
    """
    Returns a file name if exists.
    Otherwise raises an exception.

    :param s3_event_object: String with file name and path to this file. Type = String
    :return: file. Type = String
    """
    path, file = split(s3_event_object)
    if file != '':
        return file
    else:
        warning = "There is no file to update table"
        logger.warning(warning)
        raise Exception(warning)


def get_schema(s3_event_object, schemas_list):
    """
    Returns a schema name if there is valid example in `s3_event_object`.
    Otherwise raises an exception.

    :param s3_event_object: String with file name and path to this file. Type = String
    :param schemas_list: List of schemas in config file. Type = List
    :return: schema. Type = String
    """
    schema = None

    # Check if there is a schema we track
    collect_list = list()
    for element in schemas_list:
        if "/{}/".format(element) in s3_event_object:
            # We are taking the first schema we meet in event string
            schema, index = element, s3_event_object.index("/{}/".format(element))
            collect_list.append((index, schema))

    if schema is not None:
        temp = dict(collect_list)
        return temp[min(temp.keys())]
    else:
        warning = "{event} doesn't consist a schema from  this list: {schs}".format(event=s3_event_object,
                                                                                    schs=schemas_list)
        logger.warning(warning)
        raise Exception(warning)


def get_table(s3_event_object, schema, tables_dict):
    """
    Returns a table name if there is valid example in `s3_event_object`.
    Otherwise raises an exception.

    :param s3_event_object: tring with file name and path to this file. Type = String
    :param schema: Schema name to get a list of tables from config file. Type = String
    :param tables_dict: A dictionary. Type = Dictionary. Key: schema name
                                                         Value: list of tables.
    :return: table. Type = String
    """
    table = None
    schema_tables = tables_dict[schema]
    for element in schema_tables:
        if "/{}/".format(element) in s3_event_object:
            table = element
            # We assume there is only one table name
            break

    if table is not None:
        return table
    else:
        warning = "{event} doesn't match with configs structure. " \
                  "For [{schema}] schema a table from the list is expected. List: {tbls}".format(event=s3_event_object,
                                                                                                 schema=schema,
                                                                                                 tbls=schema_tables)
        logger.warning(warning)
        raise Exception(warning)


def get_partition(s3_event_object, table, partitions_dict):
    """
    Returns partition part of the `s3_event_object`.
    Raise am exception if there is a mismatching with configs.

    :param s3_event_object: tring with file name and path to this file. Type = String
    :param table: Table name to get a list of partitions from config file. Type = String
    :param partitions_dict: A dictionary. Type = Dictionary. Key: schema.table string.
                                                             Value: list of partitions.
    :return: partition. Type = String ( can be a sequence like 'year=.../month=...')
    """
    partition = ''

    partitions_from_event_object = []
    partitions_check_list = []

    table_partitions = partitions_dict[table]

    for element in split(s3_event_object)[0].split('/'):
        if '=' in element:
            partitions_from_event_object.append(element)
            partitions_check_list.append(element.split('=')[0])

    # Mismatching partitions
    symmetric_set_difference = set(partitions_check_list).symmetric_difference(set(table_partitions))
    if ((len(partitions_check_list) != len(table_partitions)) |
            (len(symmetric_set_difference) != 0)):

        warning = "{event} doesn't match with configs structure. " \
                  "For {table} the next partitions are expected: {p1} " \
                  "Gotten partitions: {p2}".format(event=s3_event_object,
                                                   table=table,
                                                   p1=table_partitions,
                                                   p2=partitions_check_list)
        logger.warning(warning)
        raise Exception(warning)

    for element in partitions_from_event_object:
        partition += '/' + element

    # Inconsistency
    if partition not in s3_event_object:
        warning = "Structure is broken. " \
                  "There is no {tbl_and_prt} in {s3_metadata}".format(tbl_and_prt=partition,
                                                                      s3_metadata=s3_event_object)
        logger.warning(warning)
        raise Exception(warning)

    # Remove '/' on the beginning and return partition part of the path
    return partition[1:]


def get_metadata(s3_event_object, schemas_list, tables_dict, partitions_dict):
    """
    Returns parsed metadata from s3_event_object.

    :param s3_event_object: String with file name and path to this file. Type = String
    :param schemas_list: List of schemas in config file. Type = List
    :param tables_dict: List of tables for particular schema in config file. Type = List
    :param partitions_dict: List of partitions for particular schema in config file. Type = List
    :return: schema, table, path, file, partition. Type = String (for all values)
    """
    file = get_file(s3_event_object)
    schema = get_schema(s3_event_object, schemas_list)
    table = get_table(s3_event_object, schema, tables_dict)
    partition = get_partition(s3_event_object, (schema + '.' + table).lower(), partitions_dict)

    # Inconsistency
    if table + '/' + partition not in s3_event_object:
        warning = "There is no {tbl_and_prt} in {s3_metadata}".format(tbl_and_prt=table + '/' + partition,
                                                                      s3_metadata=s3_event_object)
        logger.warning(warning)
        raise Exception(warning)

    path = split(s3_event_object)[0]
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
    s3_event_object = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    logger.info("S3 object: {}".format(s3_event_object))

    schema, table, path, file, partition = get_metadata(s3_event_object, SCHEMAS, TABLES, PARTITIONS)

    table = "{schm}.{tbl}".format(schm=schema.lower(), tbl=table.lower())

    event_time = datetime.strptime(event['Records'][0]['eventTime'], "%Y-%m-%dT%H:%M:%S.%fZ")

    logger.info("Table: {}".format(table))
    logger.info("File path on S3: {bkt}/{pth}".format(bkt=bucket, pth=path))
    logger.info("File:{}".format(file))
    logger.info("Partition(s): {}".format(partition))
    logger.info("Updated time: {}".format(event_time))

    conn = get_connection(metalayer_configs)
    insert_into_updates(connection=conn, table=table, path=path, file=file, partition=partition, time=event_time)

    conn.close()
    logger.info("Done. Table is updated")
