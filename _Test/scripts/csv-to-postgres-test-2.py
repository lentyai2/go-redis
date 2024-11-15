import json
from boto3.dynamodb.types import TypeDeserializer
deserializer = TypeDeserializer()

# document = { "ACTIVE": { "BOOL": True }, "CRC": { "N": "-1600155180" }, "ID": { "S": "bewfv43843b" }, "params": { "M": { "customer": { "S": "TEST" }, "index": { "N": "1" } } }, "THIS_STATUS": { "N": "10" }, "TYPE": { "N": "22" } }
# {"M":{"CUST_NBR":{"S":"54324-543456-4556-46556"}}}
document = {'config': {'L': [{'M': {'CUST_NBR': {'S': '9001'}}}, {'M': {'MERCH_NBR': {'S': '811002'}}}, {'M': {'DBA_NBR': {'S': '1'}}}, {'M': {'TERMINAL_NBR': {'S': '1'}}}, {'M': {'MAC': {'S': '5'}}}]}}
deserialized_document = {k: deserializer.deserialize(v) for k, v in document.items()}
# print(deserialized_document["array"])

my_object = {"CUST_NBR": "9001"}

# Convert object to key-value pair tuples
key_value_pairs = tuple(my_object.items())

print(key_value_pairs)