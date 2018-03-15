from __future__ import print_function
from datetime import datetime
import sys
from os.path import split
import urllib
import logging
import pymysql
from importlib import import_module
from configs.schema_metadata import schemas, tables, partitions


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
    Need to get proper configurations for particular environment.

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
    Method to connect to MySQL server.
    Exit if couldn't connect.

    :return: conn; Object to interact with MySQL server.
    """
    try:
        conn = pymysql.connect(**metalayer_config)
        logger.info("Connected to RDS MySQL instance")
        return conn
    except:
        logger.error("Could not connect to the MySql instance")
        sys.exit()


def get_file(s3_event_object):
    """
    Method to get file name.
    Exit if there is no file (folder creating)

    :param s3_event_object: String with file name and path to this file. Type = String
    :return: file. Type = String
    """
    path, file = split(s3_event_object)
    if file == '':
        logger.error("There is no file to update table")
        sys.exit()
    else:
        return file


def get_schema(s3_event_object, schemas_list):
    """
    Method to get schema.
    Exit if there is no schema from the config list (schema_metadata.py)

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
        logger.error("There is no schema from this list: {schs}".format(schs=schemas_list))
        sys.exit()


def get_table(s3_event_object, schema_tables):
    """
    Method to get table.
    Exit if there is no table from the config list (schema_metadata.py) or there is no such schema.

    :param s3_event_object: tring with file name and path to this file. Type = String
    :param schema_tables: List of tables for particular schema in config file. Type = List
    :return: table. Type = String
    """
    table = None

    for element in schema_tables:
        if "/{}/".format(element) in s3_event_object:
            table = element
            # We assume there is only one table name
            break

    if table is not None:
        return table
    else:
        logger.error("There is tables from this list: {tbls}".format(tbls=schema_tables))
        sys.exit()


def get_partition(s3_event_object, table_partitions):
    """
    Method to get partition(s).
    Exit if there is a mismatching or an inconsistency
    between a getting partitions and config partitions.

    :param s3_event_object: tring with file name and path to this file. Type = String
    :param table_partitions: List of partitions for particular schema in config file. Type = List
    :return: partition. Type = String ( can be a sequence like 'year=.../month=...'
    """
    partition = ''

    partitions_from_event_object = []
    partition_check_list = []

    for element in split(s3_event_object)[0].split('/'):
        if '=' in element:
            partitions_from_event_object.append(element)
            #
            partition_check_list.append(element.split('=')[0])

    # Mismatching partitions
    if len(set(partition_check_list).symmetric_difference(set(table_partitions))) != 0:
        logger.error("There is a mismatching between sets of partitions. "
                     "Metadata partitions: {p1} "
                     "Gotten partitions: {p2}".format(p1=table_partitions,
                                                      p2=partition_check_list)
                     )
        sys.exit()

    for element in partitions_from_event_object:
        partition += '/' + element

    # Inconsistency
    if partition not in s3_event_object:
        logger.error("There is no {tbl_and_prt} in {s3_metadata}".format(tbl_and_prt=partition,
                                                                         s3_metadata=s3_event_object))
        sys.exit()

    return partition[1:]


def get_metadata(s3_event_object, schemas, tables, partitions):
    """
    Method which returns parsed data from s3_event_object.

    :param s3_event_object: String with file name and path to this file. Type = String
    :param schemas: List of schemas in config file. Type = List
    :param tables: List of tables for particular schema in config file. Type = List
    :param partitions: List of partitions for particular schema in config file. Type = List
    :return: schema, table, path, file, partition. Type = String (for all values)
    """
    file = get_file(s3_event_object)

    schema = get_schema(s3_event_object, schemas)

    try:
        table = get_table(s3_event_object, tables[schema])
    except LookupError:
        logger.error("There is no table data for for {schm} in schema_metadata.py".format(schm=schema))
        logger.info("Table data in schema_metadata.py: {}".format(tables))
        sys.exit()

    try:
        partition = get_partition(s3_event_object, partitions[table])
    except LookupError:
        logger.error("There is no partition data for for {tbl} in schema_metadata.py".format(tbl=table))
        logger.info("Table data in schema_metadata.py: {}".format(tables))
        sys.exit()

    # Inconsistency
    if table + '/' + partition not in s3_event_object:
        logger.error("There is no {tbl_and_prt} in {s3_metadata}".format(tbl_and_prt=table + '/' + partition,
                                                                         s3_metadata=s3_event_object))
        sys.exit()

    path = split(s3_event_object)[0]
    return schema, table, path, file, partition


def lambda_handler(event, context):
    """
    Entry point for AWS Lambada function.
    More details are here: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
    About "context":  https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    :param event: S3 metadata in JSON like format. Type = String
    :param context: runtime information; not used; object.
    :return: None
    """
    env = ACCOUNTS[context.invoked_function_arn.split(":")[4]].lower()

    metalayer_configs = set_modules(env).metalayer_config

    logger.info("Event: {}".format(event))
    bucket = urllib.unquote_plus(event['Records'][0]['s3']['bucket']['name'].encode('utf8'))
    logger.info("S3 bucket: {}".format(bucket))
    s3_event_object = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    logger.info("S3 object: {}".format(s3_event_object))

    schema, table, path, file, partition = get_metadata(s3_event_object, schemas, tables, partitions)

    table = "{schm}.{tbl}".format(schm=schema.lower(),
                                  tbl=table.lower())

    event_time = datetime.strptime(event['Records'][0]['eventTime'],
                                   "%Y-%m-%dT%H:%M:%S.%fZ")

    logger.info("Table: {}".format(table))
    logger.info("File path on S3: {bkt}/{pth}".format(bkt=bucket, pth=path))
    logger.info("File:{}".format(file))
    logger.info("Partition(s): {}".format(partition))
    logger.info("Updated time: {}".format(event_time))

    conn = get_connection(metalayer_configs)

    with conn.cursor() as cur:
        cur.execute(''' 
            INSERT INTO updates (`table_name`, `file_path`, `file_name`, `partition_name`,`updated_on`, `updated_by`) 
            VALUES              ('{table_name}', '{file_path}', '{file_name}', '{partition}', '{updated_on}', "lambda")
            ON DUPLICATE KEY UPDATE
                `file_name` = '{file_name}',
                `updated_on` = '{updated_on}';
            '''.format(
            table_name=table,
            file_path=path,
            file_name=file,
            partition=partition,
            updated_on=event_time.strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        conn.commit()

    conn.close()
    logger.info("Done. Table is updated")