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
        return {_k: self.deserialize(_v) for _k, _v in v.items()}
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

with open('dynamo_users_orig.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) #skip header row
    for user in reader:
      print(user)
      created_ts = created_ts = convert_ts(user[4])
      print('CREATED ==> ', created_ts)
      signin_ts = created_ts = convert_ts(user[7])
      print('SIGN IN ==> ', signin_ts)
      # products = deserialize_field(json.loads(user[11])) if user[11] else None
      # email,agentId,appSource,company,created,emailVerified,firstName,lastLoggedIn,lastName,merchantId,phone,products,userId,userType
      values = [ 
         user[0],  #email
         user[1], #agentd
         user[2], #appSource
         user[3], #company
         created_ts, #created
         user[5], #emailVerified
         user[6], #firstName
         signin_ts, #lastLoggedIn
         user[8], #lastName
         user[9], #merchantId
         user[10], #phone
        #  products, #products
         user[12], #userId
         user[13] #userType
      ]
      print('VALUES ==> ', values)
      queryInsert = "INSERT INTO public.users (email, agent_id, app_source, company, created_ts, email_verified, first_name, signin_ts, last_name, merchant_id, phone, user_id, user_type)"
      queryValues = "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
      cur.execute(queryInsert + queryValues, values)
      
conn.commit()
cur.close()
conn.close()

print('Done!')
