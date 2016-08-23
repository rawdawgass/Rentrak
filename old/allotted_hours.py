import pandas as pd
import os


base_dir = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))

def allotted_hours():
	ah_xlsx = os.path.join('tables', 'allotted_hours.xlsx')

	ah_df = pd.read_excel(ah_xlsx, sheetname='Sheet2')

	ah_df = pd.melt(ah_df, id_vars=['mso', 'offering'], var_name='month_year', value_name='allotted_hours')
	ah_df = ah_df[['month_year', 'mso', 'offering', 'allotted_hours']]





