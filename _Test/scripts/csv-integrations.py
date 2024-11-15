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

# class obj:     
#   # constructor
#   def __init__(self, dict1):
#     self.__dict__.update(dict1)

# def dict2obj(dict1):
#   # using json.loads method and passing json.dumps
#   # method and custom object hook as arguments
#   return json.loads(json.dumps(dict1), object_hook=obj)

# def deserialize_item(item):
#    d = TypeDeserializer()
#    jsonItem = {k: d.deserialize(v) for k, v in item.items()}
#    print("jsonItem: => ", jsonItem)
#    return jsonItem

# def marshaled_to_json(field):
#     d = TypeDeserializer()
#     if not field:
#       # print("item is empty ", field)
#       return field
#     else:
#       # print("array is NOT empty ", field)
#       # jsonField = []
#       if isinstance(field, list):                
#         # print('ARRAY ITEM: ==> ', {"array": {"L": field}})
#         val = {"array": {"L": field}}
#         jsonField = {k: d.deserialize(value=v) for k, v in val.items()}

#         # print('ARRAY jsonField ==> ', jsonField["array"])
#         # dd = defaultdict(dict)
#         # print('DISCTIONARY OBJ ==> ', defaultdict(dict))
#         # [dd.update({list(p.values())[0]: list(p.values())[1]}) for p in jsonField["array"]]
#         # new_dict = {k: v for k, v in jsonField["array"]}
#         # print("DICT => ", new_dict)
#         # # new_dict = dict(d)
        
#         # print('ARRAY TYPE: ', type(jsonField["array"]))

#         np_array = np.array(jsonField["array"])
#         print("Numpy array type: ", np_array.dtype)
#         if np_array.dtype != "object":
#            return json.dumps(jsonField["array"])
        
#         # return "### TBD ###"
#         jsonObject = {}        
        
#         # print("LIST TYPE: ", jsonField["array"])
#         for dict in jsonField["array"]:
#           print("Array element type: ", dict, type(dict))
#           for k, v in dict.items():
#             jsonObject[k] = v; 
#         print("jsonObj ==> ", jsonObject)
#         return json.dumps(jsonObject)
      
#         # tupleDict = json.dumps(jsonItem["array"]).replace('{','').replace('}','')
#         # print('MOD ARRAY: ', tupleDict)
#         # for k, v in dict.items():
#         #   print("K, V ==> ", k, v)
#         #   jsonObject[k] = v
#         #   print("jsonObj 2 ==> ", jsonObject)

#           # key, val = tuple(v)
#           # jsonObject[key] = val
        
#         # return jsonItem["array"]
#         # for i in item:
#         #   # for k, v in i:
#         #   #   if k in ('S', 'SS', 'BOOL'):
#         #   #     print('ARRAY ITEM VALUE: ', v)
#         #   #     jsonItems.append(v)

#         #   print('List Item ==> ', i['S'])
#         #   # jsonItem = {k: d.deserialize(value=v) for k, v in i.items()}
#         #   # print('jsonItem ==> ', jsonItem)
#         #   jsonItems.append(i['S'])
#         # # print('jsonITems LIST: ', jsonItems)
#         # return jsonItems
#       else:
#         # print('NOT Array Item ==> ', field)
#         # jsonField = {k: d.deserialize(value=v) for k, v in field.items()}
#         jsonField = Deserializer().deserialize(field)       
#         # print('jsonItem & Type => ', jsonField, type(jsonField))
        
#         return jsonField
        
def deserialize_field(field):
  jsonField = Deserializer().deserialize(field)     
  return jsonField
  
def convert_to_object(data):
  jsonObject = {}           
  for dict in data:
    for k, v in dict.items():
      jsonObject[k] = v; 
  return Json(jsonObject)

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
      print("data BEFORE DESER: ", data)
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
          arr = [self.deserialize(_v) for _v in v]
          print("DESER ARRAY: ", arr)
          return arr
      if k == 'NULL':
        return None
      _out[k] = self.deserialize(v)
      print("_OUT => ", _out[k])
    return _out

def convert_ts(data):
  ts = (datetime.fromtimestamp(int(data)/1000)).strftime('%Y-%m-%d %H:%M:%S.%f') if data and data != 'null' and data != '' else None
  return ts
  
def convert_ts_prop(data):
  test = { **data, 'date': convert_ts(data['date'])}
  return test

def parse_sort_key(data):
  if data.startswith('LEGACY'):
    arr = data.split('_ISV-')
    return 'ISV-' + arr[1]
  else:
    arr = data.split('_INT-')
    return 'INT-' + arr[1]

with open('dynamo_integrations.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) #skip header row
    for user in reader:
      #postgres timestamp w/tz fields:
      created_ts = convert_ts(user[11])
      updated_ts = convert_ts(user[12])
      cert_ts = convert_ts(user[8])
      terminal_ts = convert_ts(user[38])
            
      #postgres text[] fields:
      attachments = deserialize_field(json.loads(user[6])) if user[6] and user[6] else None
      print("attachments: ", attachments)
      industry = deserialize_field(json.loads(user[15])) if user[15] else None
      products = deserialize_field(json.loads(user[22])) if user[22] else None

      #postgres json fields
      application = json.dumps(deserialize_field(json.loads(user[4]))) if user[4] else None
      rel_mgr = json.dumps(convert_ts_prop(deserialize_field(json.loads(user[23])))) if user[23] else None #need to convert date property from EPOCH to postgres ts
      config = deserialize_field(json.loads(user[28])) if user[28] else None
      
      #json field, but in dynamo it's an array, so need to re-format as object
      configObject = convert_to_object(config) if config != None else None 
      print("CONFIG JSON ==> ", configObject)

      valuesObject = { 
         'integration_type': user[14], 
         'active': user[2], 
         'agent_id': user[3], 
         'application': application, 
         'assignee': user[5], 
         'attachments': attachments, 
         'cert_info': user[7], 
         'cert_info_ts': cert_ts, 
         'company': user[9], 
         'created_ts': created_ts,
         'device_serial': user[13],
         'industry': industry, 
         'isv_date': check_null(user[16]),  #review for date string
         'lead_source': check_null(user[17]), 
         'meeting_type': check_null(user[18]), 
         'mid': check_null(user[19]), 
         'private_description': check_null(user[20]),
         'product': check_null(user[21]),
         'products_discussed': products, #check_null(user[21]), #review for string[] string
         'relationship_manager': rel_mgr,
         'reporter': check_null(user[24]), 
         'sales_agent': check_null(user[25]),
         'sales_group': check_null(user[27]), 
         'sandbox_config': configObject,
         'stakeholder_contact': check_null(user[29]), 
         'stakeholder_developer': check_null(user[31]),
         'status': check_null(user[33]),
         'step': check_null(user[34]), 
         'summary': check_null(user[35]),
         'team_assigned': check_null(user[36]),
         'terminal_info': check_null(user[37]), #review for string[] string
         'terminal_info_ts': terminal_ts,
         'third_party_agent': check_null(user[39]),
         'ticket': parse_sort_key(user[1]), 
         'updated_ts': updated_ts,
         'email': user[0]
      }
      
      print('VALUES ==> ', valuesObject)
      withQuery = 'WITH upd AS (INSERT INTO users (email) VALUES (%(email)s) ON CONFLICT (email) DO UPDATE SET email=%(email)s RETURNING id)'
      insertQuery = 'INSERT INTO public.integrations (integration_type, active, agent_id, application, assignee, attachments, cert_info, cert_info_ts, company, created_ts, industry, isv_date, lead_source, meeting_type, mid, private_description, product, products_discussed, relationship_manager, reporter, sales_agent, sales_group, sandbox_config, stakeholder_contact, stakeholder_developer,	status, step, summary, team_assigned, terminal_info, terminal_info_ts, third_party_agent, ticket, updated_ts, users_id) '
      valuesQuery = 'VALUES (%(integration_type)s, %(active)s, %(agent_id)s, %(application)s, %(assignee)s, %(attachments)s, %(cert_info)s, %(cert_info_ts)s, %(company)s, %(created_ts)s, %(industry)s, %(isv_date)s, %(lead_source)s, %(meeting_type)s, %(mid)s, %(private_description)s, %(product)s, %(products_discussed)s, %(relationship_manager)s, %(reporter)s, %(sales_agent)s, %(sales_group)s, %(sandbox_config)s, %(stakeholder_contact)s, %(stakeholder_developer)s, %(status)s, %(step)s, %(summary)s, %(team_assigned)s, %(terminal_info)s, %(terminal_info_ts)s, %(third_party_agent)s, %(ticket)s, %(updated_ts)s, ( SELECT id FROM upd))'

      query = withQuery + insertQuery + valuesQuery
      print("QUERY ===> ", query)
      cur.execute(query, valuesObject)
      
conn.commit()
cur.close()
conn.close()

print('Done!')
