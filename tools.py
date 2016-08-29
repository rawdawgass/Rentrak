import pandas as pd
from sqlalchemy import create_engine, text # database connection
import sqlalchemy as sa
import numpy as np
import os

base_dir = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
engine = create_engine('sqlite:///' + r'C:\Users\A_Do\Dropbox\Active Python\BizIntel\bizintel.db') #for developin

#chooses which MSOs i want to fuck with in Rentrak
mso_df = pd.read_excel(os.path.join('tables', 'MSOs.xlsx'))
mso_df = mso_df[mso_df['include?'] == 'y']

mso_dict = {k:str(v) for (k,v) in zip(mso_df['mso'], mso_df['mso_no'])}



def sql_update(table, month_year, mso):
    with engine.connect() as con:
        if mso == 'No':
            sql = text('delete from {} where month_year = "{}"'.format(table, month_year))
        else:
            sql = text('delete from {} where month_year = "{}" and mso = "{}"'.format(table, month_year, mso))
        con.engine.execute(sql)#.execution_options(autocommit=True)


def allotted_hours():
    ah_xlsx = os.path.join('tables', 'allotted_hours.xlsx')
    
    ah_df = pd.read_excel(ah_xlsx)
    ah_df = pd.melt(ah_df, id_vars=['mso', 'offering', 'provider', 'notes', 'offering_rollup', 'type', 'default_hours'], var_name='month_year', value_name='allotted_hours')
    ah_df = ah_df[['month_year', 'mso', 'offering', 'offering_rollup', 'default_hours', 'notes', 'allotted_hours']]



    #multiply default_hours x allotted_hours
    ah_df['allotted_hours'] = ah_df['allotted_hours'] * ah_df['default_hours']


    ah_df = ah_df.sort_values(['month_year', 'mso']).reset_index(drop=True)

    return ah_df
    #print (ah_df)
    #ah_df.to_excel('test123.xlsx')


#Refreshes my tables in my sqlite db that i can edit on my own
def refresh_tables():
    network_df = pd.read_excel(os.path.join('tables', 'allotted_hours.xlsx'), 'network_ids')
    default_avg_price_df = pd.read_excel(os.path.join('tables', 'allotted_hours.xlsx'), 'default_avg_price')
    allotted_hours_df = allotted_hours()

    network_df.to_sql('network_id', engine, flavor='sqlite', if_exists='replace', index=False)
    default_avg_price_df.to_sql('default_avg_price', engine, flavor='sqlite', if_exists='replace', index=False)
    allotted_hours_df.to_sql('allotted_hours', engine, flavor='sqlite', if_exists='replace', index=False)

    print ('Excel tables refreshed to SQLite!')


refresh_tables()
allotted_hours()