import pandas as pd
from sqlalchemy import create_engine # database connection
import sqlalchemy as sa
import numpy as np
import os, re, calendar, datetime

from grab_table import Grab_Data
from tools import mso_dict, sql_update


base_dir = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
engine = create_engine('sqlite:///' + r'C:\Users\A_Do\Dropbox\Active Python\BizIntel\bizintel.db')

base_url = 'https://ondemand.rentrak.com/reports/'
comp_perf_url = 'provider_analysis.html?dsr_adv_report_options_are_expanded=1;pricing_xtn_type_no=;tv_market_no=;provider_categories_tree=provider_category_no%2C__yours;go=Loading...;is_hd_filter=;is_adult_filter=;collective_view__hidden=should_roll_up_providers;is_local=;dsr_sort=sort_position+provider_anonymous_id+mso_no;generate_dataset=1;no_paging=1;date_range=RANGE;pricing_xtn_type_no=pricing_type_no%2C20'
title_perf_url = 'xtns_by_title.html?collective_view=none;currency_code_to=USD;dsr_adv_report_options_are_expanded=1;dsr_sort=sort_position%20xtns%20title_name;generate_dataset=1;is_adult_filter=;is_hd_filter=;is_local=;no_paging=1;pricing_xtn_type_no=;provider_categories_tree=;studio_no=;title_category_name=;title_name=;title_subcategory_name=;top_or_bottom_n=;tv_market_no=;user_title_category_name=;user_title_subcategory_name=;date_range=RANGE;pricing_xtn_type_no=pricing_type_no%2C20'
provider_perf_url = 'xtns_by_provider.html?dsr_adv_report_options_are_expanded=1;pricing_xtn_type_no=;tv_market_no=;provider_categories_tree=provider_category_no%2C__yours;go=Loading...;is_hd_filter=;is_adult_filter=;collective_view__hidden=should_roll_up_providers;is_local=;dsr_sort=sort_position+provider_anonymous_id+mso_no;generate_dataset=1;no_paging=1;date_range=RANGE;pricing_xtn_type_no=pricing_type_no%2C20'


grabby = Grab_Data()


class Rentrak:
    def __init__(self, start):
        self.start = start + '01'
        self.end =  str(start[:6]) + str(calendar.monthrange(int(start[:4]), int(start[4:6]))[1])
        self.month_year = str(self.start[:6])# + ' ' + calendar.month_abbr[int(self.start[4:6])]
        self.date_range = ';date_range={}%2000%3A00%3A00;date_range={}%2000%3A00%3A00'.format(self.start, self.end)


    def provider_perf(self):
        for mso in mso_dict:
            mso_code = ';subsystem_filter=mso_no%2C{}'.format(mso_dict[mso])
            url = base_url + provider_perf_url + self.date_range + mso_code
            #url = base_url + network_perf_url + self.date_range + mso_code            
            #print (url)
            try:
                extract_df = grabby.grab_table(url)

            #additional columns
                extract_df['mso'] = mso
                extract_df['month_year'] = self.month_year


                sql_update('provider_perf', self.month_year, mso)

                extract_df.to_sql('provider_perf', engine, flavor='sqlite', if_exists='append', index=False)
            except AttributeError:
                pass

            print ('{} extracted'.format(mso))

        print ('Provider Performance extracted')



    def comp_perf(self):        
        for mso in mso_dict:
            mso_code = ';subsystem_filter=mso_no%2C{}'.format(mso_dict[mso])
            url = base_url + comp_perf_url + self.date_range + mso_code
            #print (url)
            try:
                extract_df = grabby.grab_table(url)

            #additional columns
                extract_df['mso'] = mso
                extract_df['month_year'] = self.month_year

            #print (extract_df)
                sql_update('comp_perf', self.month_year, mso)
                extract_df.to_sql('comp_perf', engine, flavor='sqlite', if_exists='append', index=False)
                print ('{} extracted'.format(mso))
            except AttributeError:
                pass

        print ('Competitor Performance extracted')



    def title_perf(self):
        for mso in mso_dict:
            mso_code = ';subsystem_filter=mso_no%2C{}'.format(mso_dict[mso])
            url = base_url + title_perf_url + self.date_range + mso_code
            #print (url)

            try:
                extract_df = grabby.grab_table(url)

            #additional columns
                extract_df['mso'] = mso
                extract_df['month_year'] = self.month_year
       
                extract_df['warehouse_href'] = base_url + extract_df['warehouse_href']
        
                extract_df['title_id'] = extract_df['warehouse_href'].map(lambda x: re.findall('title_no=(.+?);', x)[0])
                extract_df['provider_id'] = extract_df['warehouse_href'].map(lambda x: re.findall('provider_no=(.+?);', x)[0])


                sql_update('title_perf', self.month_year, mso)
                extract_df.to_sql('title_perf', engine, flavor='sqlite', if_exists='append', index=False)
                print ('{} extracted'.format(mso))
            
            except AttributeError:
                pass
        print ('Title Performance extracted')



    def warehouse_perf(self):
        print ('Collecting warehouse information')
        #login(driver, "Selenium")
        df = pd.read_sql('select * from title_perf where month_year = "{}"'.format(self.month_year), engine)
        df = df[['title_id', 'provider_id', 'warehouse_href', 'title', 'network']]
        
        total_href = len(df['warehouse_href'])

        print (total_href)

        #extract_df.to_sql('warehouse_perf', engine, flavor='sqlite', if_exists='append', index=False)


        '''
        while total_href > 0:
            with requests.session() as req:
                
                login_data = {'login_id': username, 'password': password}
                req.post(login_url, data = login_data)

                for title_id, provider_id, warehouse_href, title, network in zip(df['title_id'], df['provider_id'], df['warehouse_href'], df['title'], df['network']):
                    
                    while True:
                        try:
                            rsp = req.get(warehouse_href)                    
                        except:
                            print ('response problem')
                            continue
                        break

                    soup = bs4(rsp.text, 'html.parser')
                    col_headers = [x.get_text().strip() for x in soup.select('thead > tr:nth-of-type(2) > td > a')]#[0].split('\n')
                    data = [x.get_text().strip().split('\n') for x in soup.find_all('tr', attrs={'class': ['body', 'body-alt']})]
                    data_df = pd.DataFrame(data, columns=col_headers)

                    #clean
                    data_df.columns = data_df.columns.str.lower().str.replace(' ', '_')
                    data_df = data_df.rename(columns={'revenue_($)': 'revenue', 'avg_price_($)':'avg_price', 'transactions_(txns)':'txns'})
                    data_df = data_df.replace('-', np.nan).replace('Â ', np.nan)
                    data_df['title_id'] = title_id
                    data_df['provider_id'] = provider_id
                    data_df['title'] = title
                    data_df['network'] = network


                    data_df.to_sql('warehouse', engine, flavor='sqlite', if_exists='append', index=False, chunksize=50000)

                    time.sleep(randint(1, 3))
                    
                    total_href = total_href - 1
                    print ('{} left'.format(total_href + 1))
        '''



#Uncomment everything so that the tables reformat
grabby.login()

for x in ['201601','201602','201603','201604', '201605', '201606', '201607']:
    rentrak = Rentrak(x)
    rentrak.provider_perf()
    rentrak.comp_perf()
    #rentrak.title_perf()

grabby.logout()

