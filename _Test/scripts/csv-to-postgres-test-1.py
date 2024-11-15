from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v) 
        for k, v in dynamo_obj.items()
    }  


def python_obj_to_dynamo_obj(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }


def main():
    p = {
        'a': 1,
        'b': 'b',
        'c': {
            'd': False
        },
        'e': [10, 20, 30]
    }
    print('Python object: ')
    print(p)
    print('Converted to DynamoDB object: ')
    print(python_obj_to_dynamo_obj(p))

    d = {
        'e': {'L': [{'M': {'Credential 1': {'S': '1324'}}}, {'M': {'Credential 2': {'S': '23434'}}}, {'M': {'Credential 3': {'S': '34445'}}}, {'M': {'Credential 4': {'S': '4567'}}}, {'M': {'Credential 5': {'S': '567767'}}}, {'M': {'Credential 6': {'S': '67878'}}}, {'M': {'Credential 7': {'S': '789'}}}]}
    }
    print('DynamoDB object: ')
    print(d)
    print('Converted to Python object: ')
    print(dynamo_obj_to_python_obj(d))


if __name__ == '__main__':
    main()