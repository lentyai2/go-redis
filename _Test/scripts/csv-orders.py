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
          return [self.deserialize(_v) for _v in v]
      if k == 'NULL':
        return None
      _out[k] = self.deserialize(v)
    return _out

def convert_ts(data):
  ts = (datetime.fromtimestamp(int(data)/1000)).strftime('%Y-%m-%d %H:%M:%S.%f') if data and data != 'null' and data != '' else None
  return ts

def convert_date(data):
  ts = (datetime.fromtimestamp(int(data)/1000)).strftime("%m/%d/%Y") if data and data != 'null' and data != '' else None
  return ts

def filter_refund(data):
  jsonData = { 
    "processor_reference_token": data["processor_reference_token"], 
    "refund_id": data["refund_id"], 
    "auth_code": data["auth_code"], 
    "credit_card_network": data["credit_card_network"], 
    "processor_response_id": data["processor_response_id"] 
  }
  print('FILTERED REFUND => ', jsonData)
  return jsonData

with open('dynamo_orders.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) #skip header row
    for user in reader:
      #postgres timestamp w/tz fields:
      order_date = convert_ts(user[11])
      shipping_date = convert_date(user[14])
      
      # hardware_id = get_hardware_id(hardware)
      hardware = deserialize_field(json.loads(user[8])) if user[8] and user[8] else None
      print('HARDWARE ==> ', hardware)
      hw_category = hardware["category"]
      print('HW CATEGORY ==> ', hw_category)
      hw_name= hardware["name"]
      print('HW NAME ==> ', hw_name)
      hw_type=hardware["type"]
      print('HW TYPE ==> ', hw_type)
      refund_filtered = None
      if (user[12]):
        refund = deserialize_field(json.loads(user[12]))
        print('refund ==> ', refund)
        refund_filtered = filter_refund(refund)
      print('refund_filtered ==> ', refund_filtered)
      # refund_filtered = filter_refund(refund)
      config = deserialize_field(json.loads(user[16])) if user[16] else None
      print('config ==> ', config)
    
      valuesObject = {
        'account_id': user[2], 
        'authorized_amount': user[3], 
        'canceled': bool(user[4]), 
        'device_serial': user[5], 
        'device_tracking': user[6],         
        'invoice': user[9], 
        'last_four': user[10], 
        'order_date': order_date, 
        'refund': json.dumps(refund_filtered),
        'requested_amount': user[13],
        'shipping_date': shipping_date,
        'sold_by': user[15], 
        'terminal_config': json.dumps(config),
        'transaction_id': user[17], 
        # 'created_ts': created_ts, 
        'canceled_ts': None,
        'email': user[0],
        'hw_type': hw_type, #!!! IMPORTANT: NEED TO FIX THIS VALUES IN THE CSV FILE TO MATCH CURRENT DATA!!! SPECIFICALLY PAX/North terminals:
        #"EPX PAX A35"
        #"EPX PAX A80" / "North PAX A80"
        #"EPX PAX A920 Pro" / "North PAX A920 Pro"
        #"EPX PAX A80+SP30" / "North PAX A80+SP30"
      }
      
      print('VALUES ==> ', valuesObject)
      withQuery = 'WITH upd AS (INSERT INTO users (email) VALUES (%(email)s) ON CONFLICT (email) DO UPDATE SET email=%(email)s RETURNING id)'
      insertQuery = 'INSERT INTO public.orders (account_id, authorized_amount, canceled, device_serial, device_tracking, invoice, last_four, order_date, refund, requested_amount, shipping_date, sold_by, terminal_config, transaction_id, canceled_ts, users_id, hardware_id) '
      valuesQuery = 'VALUES (%(account_id)s, %(authorized_amount)s, %(canceled)s, %(device_serial)s, %(device_tracking)s, %(invoice)s, %(last_four)s, %(order_date)s, %(refund)s, %(requested_amount)s, %(shipping_date)s, %(sold_by)s, %(terminal_config)s, %(transaction_id)s, %(canceled_ts)s, (SELECT id FROM upd), (SELECT id FROM public.hardware WHERE hardware_type = %(hw_type)s))'

      query = withQuery + insertQuery + valuesQuery
      print("QUERY ===> ", query)
      cur.execute(query, valuesObject)
      
conn.commit()
cur.close()
conn.close()

print('Done!')
