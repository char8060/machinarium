from typing import List, Optional, Tuple
from types import ModuleType

import os
import logging
import pymysql
from datetime import datetime
import urllib.parse
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


def set_modules(env_name: str) -> ModuleType:
    """
    Returns a module with necessary configs.
    Otherwise raises an error.

    :param env_name: Environment variable. Type = String
    :return: Module object.
    """

    try:
        return import_module(f"configs.{env_name}")
    except Exception as details:
        error_message = f"Module could not be imported :: {details}"
        logger.error(error_message)
        raise Exception(error_message)


def get_connection(metalayer_config: dict) -> pymysql.Connection:
    """
    Returns an pymysql connection object.
    Otherwise raises an error.

    :return: conn; Object to interact with MySQL server.
    """
    logger.info("Getting connection to to RDS instance")
    conn = pymysql.connect(**metalayer_config)
    logger.info("Connected to RDS instance")
    return conn


def insert_into_updates(connection: pymysql.Connection,
                        table: str,
                        path: str,
                        file: str,
                        partition: str,
                        time: datetime) -> None:
    """
    Executes insert query to store metadata about table update.

    :param connection: pymysql.connect() connection.
    :param table: table name, where file was updated/created.
    :param path: path to the new file.
    :param file: file name.
    :param partition: partition where file was updated/created.
    :param time: updated time.
    """
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
        table_name=table,
        file_path=path,
        file_name=file,
        partition=partition,
        event_time=time.strftime("%Y-%m-%d %H:%M:%S"))

    with connection.cursor() as cur:
        cur.execute(query)
        connection.commit()


def get_file(object_path: str) -> str:
    """
    Returns a file name if exists.
    Otherwise raises an exception.

    :param object_path: String with file name and path to this file
    :return: file name.
    """
    path, file = os.path.split(object_path)
    if file != '':
        return file
    else:
        warning_message = "There is no file to update table"
        logger.warning(warning_message)
        raise Exception(warning_message)


def get_schema(object_path: str, schemas_list: List[str]) -> str:
    """
    Returns a schema name if there is valid example in `object_path`.
    Otherwise raises an exception.

    :param object_path: String with file name and path to this file.
    :param schemas_list: List of schemas in config file.
    :return: schema name.
    """
    schema = None

    # Check if there is a schema we track
    collect_list = list()
    for element in schemas_list:
        if "/{}/".format(element) in object_path:
            # We are taking the first schema we meet in event string
            schema, index = element, object_path.index(f"/{element}/")
            collect_list.append((index, schema))
        elif object_path.startswith(element + "/"):
            schema, index = element, object_path.index(f"{element}/")
            collect_list.append((index, schema))

    if schema is not None:
        temp = dict(collect_list)
        return temp[min(temp.keys())]
    else:
        warning_message = f"{object_path} doesn't include a schema from this list: {schemas_list}"
        logger.warning(warning_message)
        raise Exception(warning_message)


def get_table(object_path: str, schema: str, tables_dict: dict) -> str:
    """
    Returns a table name from a tables list if it exists in `object_path`.
    Otherwise raises an exception.

    :param object_path: tring with file name and path to this file.
    :param schema: Schema name to get a list of tables from config file.
    :param tables_dict: A dictionary. Key: schema name
                                      Value: list of tables.
    :return: table name.
    """

    schema_tables = tables_dict[schema]
    for table in schema_tables:
        if (f"/{table}/" in object_path) or (object_path.startswith(table + "/")):
            # We assume there is only one table name
            return table

    warning_message = f"{object_path} doesn't match with configs structure. " \
                      f"For [{schema}] schema a table from the list is expected. " \
                      f"List: {schema_tables}"
    logger.warning(warning_message)
    raise Exception(warning_message)


def get_partition(object_path: str, table: str, partitions_dict: dict) -> str:
    """
    Returns partition part of the `object_path`.
    Raise am exception if there is a mismatching with configs.

    :param object_path: tring with file name and path to this file.
    :param table: Table name to get a list of partitions from config file.
    :param partitions_dict: A dictionary. Key: schema.table string.
                                          Value: list of partitions.
    :return: partition (can be a sequence like 'year=.../month=...').
    """
    partition = ''

    partitions_from_event_object = []
    partitions_check_list = []

    table_partitions = partitions_dict[table]

    for element in os.path.split(object_path)[0].split('/'):
        if '=' in element:
            partitions_from_event_object.append(element)
            partitions_check_list.append(element.split('=')[0])

    # Mismatching partitions
    symmetric_set_difference = set(partitions_check_list).symmetric_difference(set(table_partitions))
    if ((len(partitions_check_list) != len(table_partitions)) |
            (len(symmetric_set_difference) != 0)):
        warning_message = "{event} doesn't match with configs structure. " \
                  "For {table} the next partitions are expected: {p1} " \
                  "Gotten partitions: {p2}".format(event=object_path,
                                                   table=table,
                                                   p1=table_partitions,
                                                   p2=partitions_check_list)
        logger.warning(warning_message)
        raise Exception(warning_message)

    for element in partitions_from_event_object:
        partition += '/' + element

    partition = partition[1:]

    # Inconsistency
    if partition not in object_path:
        warning_message = f"Partitions are not consistently nested. There is no {partition} in {object_path}"
        logger.warning(warning_message)
        raise Exception(warning_message)

    # Remove '/' on the beginning and return partition part of the path
    return partition


# TODO (oshyshkin): need to rework output format
def get_metadata(object_path: str,
                 schemas_list: List[str],
                 tables_dict: dict,
                 partitions_dict: dict,
                 source: Optional[str] = None) -> Tuple[str, str, str, str, str]:
    """
    Returns parsed metadata from object_path.

    :param object_path: String with file name and path to this file. Type = String
    :param schemas_list: List of schemas in config file. Type = List
    :param tables_dict: List of tables for particular schema in config file. Type = List
    :param partitions_dict: List of partitions for particular schema in config file. Type = List
    :param source: some S3 locations don't include schema or/and table name.
                   Therefore, the values are hardcoded and recognized using `source` argument.
    :return: schema, table, path, file, partition. Type = String (for all values)
    """
    file = get_file(object_path)
    if source == 'canonical':
        schema = "abs"
        table = "canonical_abs"
        partition = get_partition(object_path, f"{schema}.{table}".lower(), partitions_dict)

        # Inconsistency
        check_consistency = os.path.join(partition, file)

    elif source == 'wap':
        schema = "wap"
        table = get_table(object_path, schema, tables_dict)
        partition = get_partition(object_path, f"{schema}.{table}".lower(), partitions_dict)

        # Inconsistency
        check_consistency = os.path.join(table, partition, file)

    elif source == 'sla':
        schema = "sla"
        table = get_table(object_path, schema, tables_dict)
        partition = get_partition(object_path, f"{schema}.{table}".lower(), partitions_dict)

        # Inconsistency
        check_consistency = os.path.join(table, partition, file)

    elif source == 'uexp':
        schema = "uexp"
        table = get_table(object_path, schema, tables_dict)
        partition = get_partition(object_path, f"{schema}.{table}".lower(), partitions_dict)

        # Inconsistency
        check_consistency = os.path.join(table, partition, file)

    elif source == 'ds':
        schema = "ds"
        table = get_table(object_path, schema, tables_dict)
        partition = get_partition(object_path, f"{schema}.{table}".lower(), partitions_dict)

        # Inconsistency
        check_consistency = os.path.join(table, partition, file)

    else:
        schema = get_schema(object_path, schemas_list)
        table = get_table(object_path, schema, tables_dict)
        partition = get_partition(object_path, f"{schema}.{table}".lower(), partitions_dict)

        # Inconsistency
        check_consistency = os.path.join(table, partition, file)

    if check_consistency not in object_path:
        warning_message = f"There is no {check_consistency} in {object_path}"
        logger.warning(warning_message)
        raise Exception(warning_message)

    path = str(os.path.split(object_path)[0])
    return schema, table, path, file, partition


def get_source(bucket):
    if 'gogo-udp-canonical-logs-' in bucket:
        source = 'canonical'
    elif 'gogo-udp-ds-wap-' in bucket:
        source = 'wap'
    elif 'gogo-udp-sla-' in bucket:
        source = 'sla'
    elif 'gogo-udp-uexp-' in bucket:
        source = 'uexp'
    elif 'gogo-udp-ds-catalina-' in bucket:
        source = 'ds'
    elif 'gogo-udp-netcool-' in bucket:
        source = 'STG'
    else:
        source = None
    return source


def lambda_handler(event: dict, context):
    """
    Entry point for AWS Lambada function.
    More details are here: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
    About "context":  https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    :param event: S3 metadata in JSON like format
    :param context: runtime information; object
    """
    env = ACCOUNTS[context.invoked_function_arn.split(":")[4]].lower()

    env_config = set_modules(env)
    # TODO (oshyshkin): need to rework unresolved attribute reference
    metalayer_configs = env_config.metalayer_config

    logger.info(f"Log stream name: {context.log_stream_name}")
    logger.info(f"Event: {event}")
    bucket = urllib.parse.unquote_plus(event['Records'][0]['s3']['bucket']['name'])
    logger.info(f"S3 bucket: {bucket}")
    object_path = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    logger.info(f"S3 object: {object_path}")

    source = get_source(bucket)

    try:
        schema, table, path, file, partition = get_metadata(object_path, SCHEMAS, TABLES, PARTITIONS, source)

        table = f"{schema.lower()}.{table.lower()}"

        event_time = datetime.strptime(event['Records'][0]['eventTime'], "%Y-%m-%dT%H:%M:%S.%fZ")

        logger.info(f"Table: {table}")
        logger.info(f"File path on S3: {bucket}/{path}")
        logger.info(f"File:{file}")
        logger.info(f"Partition(s): {partition}")
        logger.info(f"Event time: {event_time}")

        try:
            conn = get_connection(metalayer_configs)
        except Exception as details:
            error_message = ("Log stream name: {log_stream}. "
                             "Could not connect to the RDS instance. "
                             "Host: {host}, Database: {db}, User: {user}, Port: {port}, Connection timeout: {con_tout}."
                             " Details :: {exception}"
                             .format(log_stream=context.log_stream_name,
                                     exception=details,
                                     host=metalayer_configs['host'],
                                     db=metalayer_configs['database'],
                                     user=metalayer_configs['user'],
                                     port=metalayer_configs['port'],
                                     con_tout=metalayer_configs['connect_timeout']))
            logger.error(error_message)
            raise Exception(error_message)

        try:
            insert_into_updates(connection=conn,
                                table=table,
                                path=path,
                                file=file,
                                partition=partition,
                                time=event_time)
        except Exception as details:
            error_message = f"Log stream name: {context.log_stream_name}. " \
                            f"Can not execute insert into [p2].[updates] :: {details}"
            logger.error(error_message)
            raise Exception(error_message)

        conn.close()
        logger.info("Done. Table is updated")

    except Exception as details:
        logger.warning(f"Something happened:: {details}. Finishing the program")
