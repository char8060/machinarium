# Name of schema on S3, that's why name is case sensitive
SCHEMAS = ['RDP', 'XDW', 'opex']

# Dictionary of tables
# Key: Schema
# Value: List of tables
TABLES = {
     'RDP': ['fact_flight_availability',
             'fact_flight_segment'],

     'XDW': ['DIM_AIRCRAFT',
             'DIM_FLIGHT',
             'DIM_MEDIA_USAGE_FLT_KEY',
             'FACT_MEDIA_USAGE'],

     'opex': ['type_1_logs',
              'type_2_logs',
              'type_4_logs',

              'type_1_header_flatten',
              'type_2_header_flatten',
              'type_3_header_flatten',
              'type_4_header_flatten',

              'type_1_client_flatten',
              'type_2_client_flatten',
              'type_3_client_flatten',
              'type_4_client_flatten',

              'type_1_header_w_dom_pos',
              'type_2_header_w_dom_pos',
              'type_3_header_w_dom_pos',
              'type_4_header_w_dom_pos',

              'type_1_header_clean',
              'type_2_header_clean',
              'type_3_header_clean',
              'type_4_header_clean',

              'type_1_client_clean',
              'type_2_client_clean',
              'type_3_client_clean',
              'type_4_client_clean',

              'fact_flight_wap_availability',

              'messages_logs',
              'messages_logs_p2',

              'KANDU_files'
              ]
}

# Valid partitions for each table
# Key: table name ( schema + table)
# Value: List of partitions
PARTITIONS = {
     'opex.type_1_logs': ["partition_date"],
     'opex.type_2_logs': ["partition_date"],
     'opex.type_4_logs': ["partition_date"],

     'opex.type_1_header_flatten': ["partition_date"],
     'opex.type_2_header_flatten': ["partition_date"],
     'opex.type_3_header_flatten': ["partition_date"],
     'opex.type_4_header_flatten': ["partition_date"],

     'opex.type_1_client_flatten': ["partition_date"],
     'opex.type_2_client_flatten': ["partition_date"],
     'opex.type_3_client_flatten': ["partition_date"],
     'opex.type_4_client_flatten': ["partition_date"],

     'opex.type_1_header_w_dom_pos': ["partition_date"],
     'opex.type_2_header_w_dom_pos': ["partition_date"],
     'opex.type_3_header_w_dom_pos': ["partition_date"],
     'opex.type_4_header_w_dom_pos': ["partition_date"],

     'opex.type_1_header_clean': ["partition_date"],
     'opex.type_2_header_clean': ["partition_date"],
     'opex.type_3_header_clean': ["partition_date"],
     'opex.type_4_header_clean': ["partition_date"],

     'opex.type_1_client_clean': ["partition_date"],
     'opex.type_2_client_clean': ["partition_date"],
     'opex.type_3_client_clean': ["partition_date"],
     'opex.type_4_client_clean': ["partition_date"],

     'opex.fact_flight_wap_availability': ["partition_date"],

     'opex.messages_logs': ["partition_date"],
     'opex.messages_logs_p2': ["partition_date"],

     'opex.kandu_files': ["partition_date"],

     'rdp.fact_flight_availability': ["partition_date", "flight_source"],
     'rdp.fact_flight_segment': ["partition_date", "flight_source"],

     'xdw.dim_aircraft': [],
     'xdw.dim_flight': ['year', 'month'],
     'xdw.fact_media_usage': ["partition_date"],
     'xdw.dim_media_usage_flt_key': ["partition_date"]
}

