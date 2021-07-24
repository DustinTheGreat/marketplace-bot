from datetime import datetime, timedelta, date
from sys import exit
import os
import time
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# from price_comparison_tool import get_login_creds
from datetime import datetime, date, timedelta
##Login to facebook and scrape marketplace
# import MySQLdb
# import mysql.connector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver import ActionChains

class Controller():
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        try:
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        except:
            exit()
        self.is_logged_it = False
        self.email = os.getenv('USERNAME', 'email')
        self.password = os.getenv('PASSWORD', 'pass')

        self.main_url = 'https://www.facebook.com/'
        self.used_item_links = [] #List for holding the links to each item in search screen
        try:
            self.driver.get(self.main_url)
            print("got DB")
            self.site_status = True
        except:
            self.site_status = False

        # self.db = mysql.connector.connect(host='localhost',user=sql_user,passwd=sql_password, database='facebook_marketplace_items')
        time.sleep(5)
        print("All Ready to go")


    def login(self):
        try: 
            email_input = self.driver.find_element_by_id('email')
            email_input.send_keys(self.email)
            time.sleep(0.6)
            pw_input = self.driver.find_element_by_id('pass')
            pw_input.send_keys(self.password)
            time.sleep(0.4)
            login_button = self.driver.find_element_by_name('login')
            login_button.click()
            print('Login successful')
            self.is_logged_in =True
            time.sleep(3)
        
            
        except Exception as e:
            print('Login unsuccessful:', str(e))
            self.driver.quit()
            exit()

    def open_mktplace(self):
        time.sleep(3)
        try:
            marketplace_btn = self.driver.find_element_by_xpath('//span[contains(text(), "Marketplace")]') #Checks the text of all spans for any instance of marketplace
            time.sleep(3)
            marketplace_btn.click()
            time.sleep(4)  
        except Exception as e:
            print('Make sure user is loggedd in')
            print('Unable to find marketplace button:', str(e))
            #self.driver.quit()
            exit()        


    def search_item(self,item_name, location_name):
        try:
            search_bar = self.driver.find_element_by_xpath('//input[@placeholder="Search Marketplace"]') #Locates the marketplace search bar
            search_bar.send_keys(item_name)
            search_bar.send_keys(Keys.RETURN)
            print('Search successful')
            time.sleep(4)
        except:
            print('Unable to find marketplace search bar')
            self.driver.quit()
            exit()

    def scrape_item_links(self):

        #Used to scroll down page in order to load more items, otherwise stale element error
        #To speed up the scrape, try doing while len(url_list) < 100 instead of just constantly running for loops
        for i in range(500): 
            try:
                self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                time.sleep(1.3)
            except Exception:
                pass
        
        print('Page scrolled')
        full_item_list = self.driver.find_elements_by_xpath('//a[contains(@class, "oajrlxb2")]') #Returns a list with location of all items links

        #Loops through each item from the location list and returns the unique portion of the URL 
        for item in full_item_list:
            try:
                if item.get_attribute('href').startswith('/marketplace/item', 24): #Page uses many href tags, this specifies only the item links
                    self.used_item_links.append(item.get_attribute('href'))
            except StaleElementReferenceException:
                self.used_item_links.append(None)
            
        return self.used_item_links

    def scrape_item_info(self,used_item_links,category):

        #This loops through every item URL and retrives the desired data for that item
        counter = 1
        for url in used_item_links: 
            self.driver.get(url)
            time.sleep(10)

            try:
                price_raw = self.driver.find_element_by_xpath('//div[contains(@class, "dati1w0a qt6c0cv9 hv4rvrfc discj3wi")]/div[2]/div/span[1]').text #Locates the price element tag and extracts the text
                price_raw1 = price_raw.replace(',','').replace('C','') #For reduced prices in canadian dollars, a C will prepend the second $, need to remove it to match int format 
                
                if '·' in price_raw1: #Some titles say · In Stock, need to remove for int format
                    price_raw2, instock = price_raw1.split('·') 
                else:
                    price_raw2 = price_raw1

                if price_raw2.count('$') == 2: #if the price is reduced, both prices will be scraped with two $ characters and the reduced value appearing first
                    blank,price_str,orig_price = price_raw2.split('$') 
                    price = int(price_str) #Price was passing as a string, db expects int for price
                else:
                    price_str = price_raw2.replace('$','')
                    price = int(price_str)
            except Exception:
                print('\nPrice failed\n')
                price = 0 #Don't use None, it causes issues since it's not an int

            #The html xpath for title is used multiple times so always want to skip the first item scraped
            title_html = []
            title_html = self.driver.find_elements_by_xpath('//span[contains(@class,"iv3no6db o0t2es00 f530mmz5 hnhda86s")]')
            title = title_html[1].text

            try:
                description = self.driver.find_element_by_xpath('//div[contains(@class,"ii04i59q ")]/div/span').text
            except:
                description = ""
            
            urlId = url.split('/item/')[1]
            scraped_date = date.today() #Using a datetime object that does not include time            

            insertValues = (urlId, title, price, description, scraped_date, scraped_date, category)


        print("used_item_links", used_item_links, len(used_item_links))


        self.driver.quit()



if __name__ == '__main__':
    start_time = time.monotonic()
    fb_app = Controller()
    fb_app.login()
    fb_app.open_mktplace()
    fb_app.search_item(item_name='smoker',location_name='Toronto')
    used_item_links = fb_app.scrape_item_links()
    print("\n")
    print("\n")
    print("####################################")
    print("\n")
    print("\n")
    print("Thanks for using!)
    exit()
    # fb_app.scrape_item_info(used_item_links,category='smoker')
    # end_time = time.monotonic()
    # print('Runtime: ', timedelta(seconds=end_time - start_time))
