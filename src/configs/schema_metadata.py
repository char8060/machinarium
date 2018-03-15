# Name of schema on S3, that's why name is case sensitive
schemas = ['RDP', 'XDW', 'opex']

# table = folder name on S3
tables = {
     'RDP': ['fact_flight_availability', 'fact_flight_segment'],
     'XDW': ['DIM_AIRCRAFT', 'DIM_FLIGHT', 'FACT_MEDIA_USAGE', 'DIM_MEDIA_USAGE_FLT_KEY'],
     'opex': ['type_1_logs', 'type_2_logs', 'type_4_logs',
              'type_1_header_flatten', 'type_2_header_flatten', 'type_3_header_flatten', 'type_4_header_flatten',
              'type_1_client_flatten', 'type_2_client_flatten', 'type_3_client_flatten', 'type_4_client_flatten',
              'type_1_header_w_dom_pos', 'type_2_header_w_dom_pos', 'type_3_header_w_dom_pos', 'type_4_header_w_dom_pos',
              'type_1_header_clean', 'type_2_header_clean', 'type_3_header_clean', 'type_4_header_clean',
              'type_1_client_clean', 'type_2_client_clean', 'type_3_client_clean', 'type_4_client_clean',
              'fact_flight_wap_availability'
              ]
}

# Need to combine schema name and table name
# Using to create a list of job; in database it's usually in lowercase
partitions = {
     'type_1_logs': ["partition_date"],
     'type_2_logs': ["partition_date"],
     'type_4_logs': ["partition_date"],
     'type_1_header_flatten': ["partition_date"],
     'type_2_header_flatten': ["partition_date"],
     'type_3_header_flatten': ["partition_date"],
     'type_4_header_flatten': ["partition_date"],
     'type_1_client_flatten': ["partition_date"],
     'type_2_client_flatten': ["partition_date"],
     'type_3_client_flatten': ["partition_date"],
     'type_4_client_flatten': ["partition_date"],
     'type_1_header_w_dom_pos': ["partition_date"],
     'type_2_header_w_dom_pos': ["partition_date"],
     'type_3_header_w_dom_pos': ["partition_date"],
     'type_4_header_w_dom_pos': ["partition_date"],
     'type_1_header_clean': ["partition_date"],
     'type_2_header_clean': ["partition_date"],
     'type_3_header_clean': ["partition_date"],
     'type_4_header_clean': ["partition_date"],
     'type_1_client_clean': ["partition_date"],
     'type_2_client_clean': ["partition_date"],
     'type_3_client_clean': ["partition_date"],
     'type_4_client_clean': ["partition_date"],
     'fact_flight_wap_availability': ["partition_date"],
     'fact_flight_availability': ["partition_date", "flight_source"],
     'fact_flight_segment': ["partition_date", "flight_source"],
     'DIM_AIRCRAFT': ['year', 'month'],
     'DIM_FLIGHT': ['year', 'month'],
     'FACT_MEDIA_USAGE': ["partition_date"],
     'DIM_MEDIA_USAGE_FLT_KEY': ["partition_date"]
}

