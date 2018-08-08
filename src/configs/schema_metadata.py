# Name of schema on S3, that's why name is case sensitive
SCHEMAS = ['RDP', 'XDW', 'opex']

# Dictionary of tables
# Key: Schema
# Value: List of tables
TABLES = {
     'RDP': ['fact_flight_availability',
             'fact_flight_segment',
             'SM_2KU_RECORD_LOGS',
             'SM_KU_RECORD_LOGS',
             'WAP_TYPE_1_SUMMARY',
             'WAP_TYPE_2_SUMMARY',
             'WAP_TYPE_3_SUMMARY',
             'WAP_TYPE_4_SUMMARY',
             'WAP_TYPE_1_CLIENT',
             'WAP_TYPE_2_CLIENT',
             'WAP_TYPE_3_CLIENT',
             'WAP_TYPE_4_CLIENT'
            ],

     'XDW': ['DIM_AIRCRAFT',
             'DIM_FLIGHT',
             'DIM_MEDIA_USAGE_FLT_KEY',
             'FACT_MEDIA_USAGE',
             'FACT_USAGE'],

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
              'fact_flight_wap_availability_new_definition',

              'messages_logs',
              'messages_logs_p2',

              'KANDU_files',
              'KANDU_files_minute_p2',
              'antennas_current_features',
              'antennas_current_features_enriched_submode420',
              
              'satcom_decile',
              'satcom_decile_tail',
              
              'parsed_devices',
              'abs_device_info',
              'antennas_current_health',
              'antennas_mtbf'
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
     'opex.fact_flight_wap_availability_new_definition': ["partition_date"],

     'opex.messages_logs': ["partition_date"],
     'opex.messages_logs_p2': ["partition_date"],
     'opex.antennas_current_features': ["partition_date"],
     'opex.antennas_current_features_enriched_submode420': ["partition_date"],

     'opex.kandu_files': ["partition_date"],
     'opex.kandu_files_minute_p2': ["partition_date"],
     
     'opex.satcom_decile': ["source", "partition_date"],
     'opex.satcom_decile_tail': ["source", "partition_date"],
     
     'opex.parsed_devices': ["source", "partition_date"],
     'opex.abs_device_info':["source", "partition_date"],
     'opex.antennas_current_health':["partition_date"],
     'opex.antennas_mtbf':["partition_date"],

     'rdp.fact_flight_availability': ["partition_date", "flight_source"],
     'rdp.fact_flight_segment': ["partition_date", "flight_source"],
     'rdp.sm_2ku_record_logs': ["partition_date"],
     'rdp.sm_ku_record_logs': ["partition_date"],
     'rdp.wap_type_1_summary': ["partition_date"],
     'rdp.wap_type_2_summary': ["partition_date"],
     'rdp.wap_type_3_summary': ["partition_date"],
     'rdp.wap_type_4_summary': ["partition_date"],
     'rdp.wap_type_1_client': ["partition_date"],
     'rdp.wap_type_2_client': ["partition_date"],
     'rdp.wap_type_3_client': ["partition_date"],
     'rdp.wap_type_4_client': ["partition_date"],

     'xdw.dim_aircraft': [],
     'xdw.dim_flight': ['year', 'month'],
     'xdw.fact_media_usage': ["partition_date"],
     'xdw.dim_media_usage_flt_key': ["partition_date"],
     'xdw.fact_usage':["partition_date"],

     # schema and table values are hardcoded in code
     'abs.canonical_abs': ["partition_date", "source"]
}
