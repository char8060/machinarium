# Name of schema on S3, that's why name is case sensitive
SCHEMAS = ['RDP', 'XDW', 'opex', 'satcom', 'abs', 'wap']

# Dictionary of tables
# Key: Schema
# Value: List of tables
TABLES = {
    # schema and table values are hardcoded in codexX
    'abs': ['canonical_abs'],

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

             'satcom_decile',
             'satcom_decile_tail',
             'satcom_decile_grid',

             'abs_device_info',
             'abs_device_info_with_duplication',

             'dim_flight',
             'dim_flight_periodic'
             ],

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
            'WAP_TYPE_4_CLIENT',

            'FACT_DRC_MESSAGES_DAILY'
            ],

    'satcom': ['antenna_current_spikes',
               'antenna_gmm_features',
               'antenna_gmm_output',
               'antenna_regression_features',
               'antenna_regression_output',
               'kandu_files',
               'kandu_files_audit',
               'kandu_files_minute',
               'kandu_logs',
               'antenna_flight_features',
               'outages_summary'
               ],

    'wap': ['wap_meta',
            'type_1_json',
            'type_2_json',
            'type_3_json',
            'type_4_json',
            'type_5_json'
            ],

    'XDW': ['DIM_AIRCRAFT',
            'DIM_FLIGHT',
            'DIM_FLIGHT_PERIODIC',
            'DIM_MEDIA_USAGE_FLT_KEY',
            'FACT_MEDIA_USAGE',
            'FACT_USAGE'
            ]
}


# Valid partitions for each table
# Key: table name ( schema + table)
# Value: List of partitions
PARTITIONS = {
    # schema and table values are hardcoded in codexX
    'abs.canonical_abs': ["partition_date", "source"],

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

    'opex.dim_flight': ["partition_date"],
    'opex.dim_flight_periodic': ["partition_date"],
    'opex.dim_flight_matched': ["partition_date"],

    'opex.kandu_files': ["partition_date"],
    'opex.kandu_files_minute_p2': ["partition_date"],

    'opex.satcom_decile': ["source", "partition_date"],
    'opex.satcom_decile_tail': ["source", "partition_date"],
    'opex.satcom_decile_grid': ["source", "partition_date"],

    'opex.abs_device_info': ["source", "partition_date"],
    'opex.abs_device_info_with_duplication': ["source", "partition_date"],

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
    'rdp.fact_drc_messages_daily': ["partition_date"],

    'satcom.antenna_current_spikes': ["partition_date"],
    'satcom.antenna_gmm_features': ["partition_date"],
    'satcom.antenna_gmm_output': ["partition_date"],
    'satcom.antenna_regression_features': ["partition_date"],
    'satcom.antenna_regression_output': ["partition_date"],
    'satcom.kandu_files': ["partition_date"],
    'satcom.kandu_logs': ["partition_date"],
    'satcom.kandu_files_minute': ["partition_date"],
    'satcom.kandu_files_audit': ["partition_date"],
    'satcom.antenna_flight_features': ["partition_date"],
    'satcom.outages_summary': ["partition_date"],

    'wap.wap_meta': ["partition_date"],
    'wap.type_1_json': ["partition_date"],
    'wap.type_2_json': ["partition_date"],
    'wap.type_3_json': ["partition_date"],
    'wap.type_4_json': ["partition_date"],
    'wap.type_5_json': ["partition_date"],

    'xdw.dim_aircraft': [],
    'xdw.dim_flight': ['year', 'month'],
    'xdw.dim_flight_periodic': ['partner_airline_code_icao', 'year', 'month'],
    'xdw.fact_media_usage': ["partition_date"],
    'xdw.dim_media_usage_flt_key': ["partition_date"],
    'xdw.fact_usage': ["partition_date"]
}
