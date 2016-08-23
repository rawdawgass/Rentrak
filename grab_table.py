import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup as bs4

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from random import randint
import time

login_url = 'https://ondemand.rentrak.com/login.html'
username = "steven.fong"
password = "blinkme1"


class Grab_Data:
    def __init__(self):
        #self.url = url
        self.driver = webdriver.Firefox()
        self.wait = WebDriverWait(self.driver, 2)

    def login(self):
        self.driver.get(login_url)
        login_field = self.wait.until(lambda driver: driver.find_element_by_xpath("//*[@id='login-container']/input[1]")).send_keys(username)
        pass_field = self.wait.until(lambda driver: driver.find_element_by_xpath("//*[@id='login-container']/input[2]")).send_keys(password)
        login_button = self.wait.until(lambda driver: driver.find_element_by_xpath("//*[@id='login-container']/input[4]")).click()


    def grab_table(self, url):
        self.driver.get(url)
        retries = 0
        while True and retries < 50:
            try:
                retries = retries + 1
                print('Attempt {}'.format(retries))
                #wait for that filter that is in every table, in this case the content table
                content_filter = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='custom-pricing-xtn-type-no-style']/span/table/tbody/tr/td/select")))
                print ('loading complete!')
                break
            except TimeoutException:
                #print('Still Loading')
                time.sleep(10)
                continue

        rsp = self.driver.page_source
        soup = bs4(rsp, 'html.parser')
        #driver.close()

        #get the column headers here
        col_headers = [x.get_text().strip() for x in soup.select('thead > tr:nth-of-type(2) > td > a')]
        
        #get table information here
        data = [x.get_text().strip().split('\n') for x in soup.find_all('tr', attrs={'class': ['body', 'body-alt', '']})]

        #data = [x.get_text().strip() for x in soup.select('thead > tr:nth-of-type(2) > td')]

       
        #make into a df here
        extract_df = pd.DataFrame(data, columns=col_headers)
        #clean
        extract_df = extract_df.replace('-', np.nan)          
        extract_df.columns = extract_df.columns.str.lower().str.replace(' ', '_')
        extract_df = extract_df.rename(columns={'revenue_($)': 'revenue', 
                                                'avg_price_($)':'avg_price', 
                                                'transactions_(txns)':'txns',
                                                'vod_window_(days)':'vod_window',
                                                '%':'percent',
                                                'avg_txns_/stb':'avg_txns_stb',
                                                'txns_/stb':'txns_stb',
                                                })

        #stupid code to be a catchall so that I can get all the data but sometimes there are nuull or blank columns
        extract_df = extract_df[extract_df['network'] != ''].reset_index(drop=True)
        extract_df = extract_df[extract_df['network'] != None].reset_index(drop=True)
        extract_df = extract_df[extract_df['network'].notnull()].reset_index(drop=True)
        #print (extract_df)

        #clean numbers
        def num(s):
            s = s.replace(',', '')
            try:
                return int(s)
            except ValueError:
                return float(s)
        extract_df['txns'] = extract_df['txns'].apply(lambda x: num(x))

        try:
            extract_df['revenue'] = extract_df['revenue'].apply(lambda x: num(x))
            extract_df['avg_price'] = extract_df['avg_price'].apply(lambda x: num(x))

        except:
            pass



        #sole purpose of this is for the titles href links for warehouse, but it doesn't exist in every table
        warehouse_data = [x.get('href') for x in soup.select('tr > td:nth-of-type(15) > a[href]')]
        warehouse_df = pd.DataFrame(warehouse_data, columns=['warehouse_href'])
        warehouse_df['warehouse_href'] = warehouse_df['warehouse_href'] + ';no_paging=1'
        warehouse_df = warehouse_df.ix[1:].reset_index(drop=True)#drop first row


        #if i merge that shit without any data it fucks everything up and makes it zero
        if len(warehouse_df) > 0:
            extract_df = extract_df.merge(warehouse_df, right_index=True, left_index=True)

        #print (extract_df)
        return (extract_df)
    def logout(self):
        self.driver.close()



'''
def grab_table(url, load):
    #specifically for Rentrak
    #load 'long' is for using selenium because of that fucking Rentrak loading screen
    #load 'short' is for using pure Beautiful Soup because of that fucking Rentrak loading screen

    login_url = 'https://ondemand.rentrak.com/login.html'
    username = "steven.fong"
    password = "@pple1987"

    if load == 'long':
        #driver = webdriver.Firefox()
        #wait = WebDriverWait(driver, 2)
        
        #driver.get(login_url)

        #login_field = wait.until(lambda driver: driver.find_element_by_xpath("//*[@id='login-container']/input[1]")).send_keys(username)
        #pass_field = wait.until(lambda driver: driver.find_element_by_xpath("//*[@id='login-container']/input[2]")).send_keys(password)
        #login_button = wait.until(lambda driver: driver.find_element_by_xpath("//*[@id='login-container']/input[4]")).click()
        

        driver.get(url)

        retries = 0
        while True and retries < 50:
            try:
                retries = retries + 1
                print('Attempt {}'.format(retries))
                #wait for that filter that is in every table, in this case the content table
                content_filter = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='custom-pricing-xtn-type-no-style']/span/table/tbody/tr/td/select")))
                print ('loading complete!')
                break
            except TimeoutException:
                #print('Still Loading')
                time.sleep(10)
                continue

        rsp = driver.page_source
        soup = bs4(rsp, 'html.parser')
        driver.close()

    if load == 'short':
        #throw a counter in here so that it only logs in once
        with requests.session() as req:
            login_data = {'login_id': username, 'password': password}
            req.post(login_url, data=login_data)

        while True:
            try:
                rsp = req.get(url)
                time.sleep(randint(2,5))                                    
            except:
                print ('did not get full response')
                continue
            break
        
        soup = bs4(rsp.text, 'html.parser')


    #get the column headers here
    col_headers = [x.get_text().strip() for x in soup.select('thead > tr:nth-of-type(2) > td > a')]
    
    #get table information here
    data = [x.get_text().strip().split('\n') for x in soup.find_all('tr', attrs={'class': ['body', 'body-alt', '']})]

    #data = [x.get_text().strip() for x in soup.select('thead > tr:nth-of-type(2) > td')]

   
    #make into a df here
    extract_df = pd.DataFrame(data, columns=col_headers)
    #clean
    extract_df = extract_df.replace('-', np.nan)          
    extract_df.columns = extract_df.columns.str.lower().str.replace(' ', '_')
    extract_df = extract_df.rename(columns={'revenue_($)': 'revenue', 
                                            'avg_price_($)':'avg_price', 
                                            'transactions_(txns)':'txns',
                                            'vod_window_(days)':'vod_window',
                                            '%':'percent',
                                            'avg_txns_/stb':'avg_txns_stb',
                                            'txns_/stb':'txns_stb',
                                            })

    extract_df = extract_df[extract_df['network'].notnull()].reset_index(drop=True)

    print (extract_df)
    #sole purpose of this is for the titles href links for warehouse, but it doesn't exist in every table
    warehouse_data = [x.get('href') for x in soup.select('tr > td:nth-of-type(15) > a[href]')]
    warehouse_df = pd.DataFrame(warehouse_data, columns=['warehouse_href'])
    warehouse_df['warehouse_href'] = warehouse_df['warehouse_href'] + ';no_paging=1'
    warehouse_df = warehouse_df.ix[1:].reset_index(drop=True)#drop first row


    #if i merge that shit without any data it fucks everything up and makes it zero
    if len(warehouse_df) > 0:
        extract_df = extract_df.merge(warehouse_df, right_index=True, left_index=True)

    print (extract_df)
    return (extract_df)

    time.sleep(randint(2,5))
    #print ('table extracted')


    



#warehouse_df = grab_table(url, 'short')

#print (warehouse_df)

'''