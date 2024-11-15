import psycopg2
import csv
from datetime import datetime

conn = psycopg2.connect(
  host='dev-rds.nabproduct.blueclouds.io',
  database='rdsdevportal',
  user='postgres',
  password='KMLRkC6wr3K4dHC2aDcWoHt3'
)

cur = conn.cursor()

with open('hardware-type.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) #skip header row
    for user in reader:
      print(user)
      created_ts = datetime.now()
      # Category,Hardware Name,Hardware Type,Cost,For Sale,Deprecated,Description,Image,ImageWebp,Icon,Software
      values = [ 
         user[0],  
         user[1], 
         user[2], 
         user[3], 
         bool(user[4]), 
         bool(user[5]), 
         user[6], 
         user[7], 
         user[8],
         user[9], 
         user[10],
         created_ts
      ]
      print('VALUES ==> ', values)
      queryInsert = "INSERT INTO public.hardware (category, hardware_name, hardware_type, hardware_cost, for_sale, depricated, description, image, image_webp, icon, software, created_ts)"
      queryValues = "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
      cur.execute(queryInsert + queryValues, values)
      
conn.commit()
cur.close()
conn.close()

print('Done!')
