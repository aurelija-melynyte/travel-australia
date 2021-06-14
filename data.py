import pandas as pd
import sqlalchemy
import psycopg2
from constants.password import slaptazodis

"""duomenu nuskaitymas ir irasymas i postgres duomenu baze"""

data = pd.read_excel('locations.xlsx')

sqlEngine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:'+slaptazodis+'@localhost/a_new_database')
conn = sqlEngine.connect()
data.to_sql('new_data', con=sqlEngine, if_exists='replace')
conn.close()

"""duomenu atidarymas"""
conn = psycopg2.connect(host='localhost', database="a_new_database", user="postgres", password=slaptazodis)
conn.autocommit = True
cur=conn.cursor()
cur.execute("""Select * from public.new_data""")
locations=cur.fetchall()

location_list = []

for element in locations:
    element_tuple = (element[1], element[3], element[4])
    location_list.append(element_tuple)







