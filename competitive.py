import pandas as pd
from sqlalchemy import create_engine # database connection
import sqlalchemy as sa
import numpy as np
import os

base_dir = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
engine = create_engine('sqlite:///' + r'C:\Users\A_Do\Dropbox\Active Python\BizIntel\bizintel.db') #for developin


xlsx = r'D:\Dropbox\Active Python\BizIntel\Tables\Network IDs.xlsx'

df = pd.read_excel(xlsx)

df2 = pd.read_sql('select * from comp_perf', engine)

df['network'] = df['network'].astype('str')


merge_df = df2.merge(df, on='network', how='left')



merge_df.to_excel('q.xlsx')

print (merge_df)