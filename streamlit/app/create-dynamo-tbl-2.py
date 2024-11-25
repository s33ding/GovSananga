from shared_func.dynamo_func import create_dynamodb_table
import config


response = create_dynamodb_table(
    table_name= config.dynamo_tbl_2,
    attribute_definitions=[
        {
            'AttributeName': 'coordinates-heading',  # Attribute used as HASH key
            'AttributeType': 'S'  # S represents a string data type
        },
        {
            'AttributeName': 'group',  # Attribute used as RANGE key
            'AttributeType': 'S'  # S represents a string data type
        }
    ],
    key_schema=[
        {
            'AttributeName': 'coordinates-heading',
            'KeyType': 'HASH'  # HASH indicates the partition key
        },
        {
            'AttributeName': 'group',
            'KeyType': 'RANGE'  # RANGE indicates the sort key
        }
    ]
)
