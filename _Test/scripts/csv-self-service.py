import psycopg2
import csv
import json
from datetime import datetime
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from decimal import Decimal
from psycopg2.extras import Json 

conn = psycopg2.connect(
  host='dev-rds.nabproduct.blueclouds.io',
  database='rdsdevportal',
  user='postgres',
  password='KMLRkC6wr3K4dHC2aDcWoHt3'
)

cur = conn.cursor()
        
def deserialize_field(field):
  jsonField = Deserializer().deserialize(field)  
  print("json TEST => ", json.dumps(jsonField))   
  return jsonField

def check_null(val):
  return val if val != '' and val != 'null' else None

def decimal_serializer(obj):
  if isinstance(obj, Decimal):
    return str(obj)
  raise TypeError("Type not serializable")

class Deserializer:
  def deserialize(self, data: dict) -> dict:
    _out = {}
    if not data or data == [] or data == 'null':
      return None
    if type(data) == list:
      data = {"L": data}
    for k, v in data.items():
      if isinstance(v, Decimal):
        return str(v)
      if k in ('S', 'SS', 'BOOL'):
        return v
      if k == 'N':
        return float(v) if '.' in v else int(v)
      if k == 'NS':
        return [float(_v) if '.' in _v else int(_v) for _v in v]
      if k == 'M':
        return json.dumps({_k: self.deserialize(_v) for _k, _v in v.items()})
      if k == 'L':
        if v == [] or v == None:
          return None
        else:
          test = [self.deserialize(_v) for _v in v]
          print("TEST: ", test)
          return test
      if k == 'NULL':
        return None
      _out[k] = self.deserialize(v)
    return _out

def convert_ts(data):
  ts = (datetime.fromtimestamp(int(data)/1000)).strftime('%Y-%m-%d %H:%M:%S.%f') if data and data != 'null' and data != '' else None
  return ts

def obj_to_str(val):
  return json.dumps(val)

def convert_to_object(data):  
  jsonObject = []           
  for dict in data: 
    # test = json.dumps({ **data, 'date': convert_ts(data['date'])})   
    jsonObject.append(json.dumps(dict))
    print('TEST DATA 3: ', jsonObject)
    # for k, v in dict.items():
    #   jsonObject[k] = Json(v); 
  return jsonObject

with open('dynamo_self-service.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) #skip header row
    for user in reader:
      #postgres timestamp w/tz fields:
      created_ts = convert_ts(user[3])
            
      #json[] array
      profiles = deserialize_field(json.loads(user[6])) if user[6] and user[6] else None
      print("PROFILES => ", profiles)
      valuesObject = { 
         'active': bool(user[2]),
         'created_ts': created_ts,
         'profiles': profiles,
         'product': user[7], 
         'email': user[0]
      }
      
      print('VALUES ==> ', valuesObject)
      withQuery = 'WITH upd AS (INSERT INTO users (email) VALUES (%(email)s) ON CONFLICT (email) DO UPDATE SET email=%(email)s RETURNING id)'
      insertQuery = 'INSERT INTO public.self_service (active, created_ts, product, merchant_profiles, users_id) '
      valuesQuery = 'VALUES (%(active)s, %(created_ts)s, %(product)s, %(profiles)s::json[], (SELECT id FROM upd))'

      query = withQuery + insertQuery + valuesQuery
      print("QUERY ===> ", query)
      cur.execute(query, valuesObject)
      
conn.commit()
cur.close()
conn.close()

print('Done!')
