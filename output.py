import pandas as pd
from sqlalchemy import create_engine, text # database connection
import sqlalchemy as sa
import numpy as np
import os

import tools
from models import rpsh_sql

base_dir = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
engine = create_engine('sqlite:///' + r'C:\Users\A_Do\Dropbox\Active Python\BizIntel\bizintel.db') #for developin
#engine = create_engine('sqlite:///' + r'D:\Dropbox\Active Python\BizIntel\bizintel.db') #home

rpsh_df = pd.read_sql(rpsh_sql, engine)
ah_df = pd.read_sql('''SELECT DISTINCT mso, offering, offering_rollup from allotted_hours''', engine)


#This merge ensures offering rollup is properly implemented because the first merge does not link to stuff rentrak has but we dont
rpsh_df = rpsh_df.merge(ah_df, how='left', on=['mso', 'offering']).reset_index(drop=True)

#because of that nationwide shit, i do not want to merge with the hours, so this is how i roll it up
rpsh_df['offering_dupe'] = rpsh_df.duplicated(['mso', 'month_year', 'offering_rollup'], keep='first').astype(str)

#if offering_rollup is duplicated, then I make the allotted hours zero for the pivot
rpsh_df['allotted_hours'] = rpsh_df.apply(lambda row: np.nan if row['offering_dupe']=='True' else row['allotted_hours'], 1)






#rpsh_df['allotted_hours2'] = rpsh_df.apply(allotted_hours_fix, 1)


#rpsh_df['allotted_hours'] = rpsh_df.apply(allotted_hours_fix, axis=1)


rpsh_df.to_excel('output_rpsh.xlsx', index=False)
