from datetime import datetime, timedelta, date
from sys import exit
import os
import time
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# from price_comparison_tool import get_login_creds
from datetime import datetime, date, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver import ActionChains

class Controller():
    def __init__(self):
        self.all_listings = []
        self.max_price = None
        self.min_price = None
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
        self.rental_url = 'https://www.facebook.com/marketplace/category/propertyrentals'
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
    def set_fb_filters(self):
        if self.max_price !=None:
            new = self.rental_url+"?maxPrice={}exact=false".format(self.max_price)
            self.rental_url = new
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
            
    def open_rentals(self):
        time.sleep(5)
        try:
            self.driver.get("https://www.facebook.com/marketplace/category/propertyrentals?maxPrice=1300&exact=false")
            # marketplace_btn = self.driver.find_element_by_xpath('//span[contains(text(), "Property Rentals")]') #Checks the text of all spans for any instance of marketplace
            # time.sleep(3)
            # marketplace_btn.click()
            # time.sleep(4)  
            time.sleep(5)

        except Exception as e:
            print('Make sure user is loggedd in')
            print('Unable to find rentals button:', str(e))
            #self.driver.quit()
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
        for i in range(10): 
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
                print("item", item.get_attribute('href'))
                if item.get_attribute('href').startswith('/marketplace/item', 24): #Page uses many href tags, this specifies only the item links
                    self.used_item_links.append(item.get_attribute('href'))
            except StaleElementReferenceException:
                self.used_item_links.append(None)
            
        return self.used_item_links

    def scrape_item_info(self):

        #This loops through every item URL and retrives the desired data for that item
        counter = 1
        for url in self.used_item_links: 
            self.driver.get(url)
            time.sleep(10)

            try:
                # //*[@id="mount_0_0_U7"]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/div/span
                price_raw = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/div/span').text #Locates the price element tag and extracts the text
                print(price_raw)
            except:
                pass
            # #The html xpath for title is used multiple times so always want to skip the first item scraped
            # title_html = []

            try:
                description = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[2]/div/div[2]/div/div[1]/div[1]/div[8]/div[2]/div/div/div/span').text
            except:
                description = ""
            print(description)
            exit()
            # urlId = url.split('/item/')[1]
            scraped_date = date.today() #Using a datetime object that does not include time            
            # self.all_listings.append(title)
            # insertValues = (urlId, title, price, description, scraped_date, scraped_date, category)


        # print("used_item_links", used_item_links, len(used_item_links))



    def today_rental_links(self):
        print("Todays Rentals Links")
        print("----------------------------------")
        for x in range(len(self.used_item_links)):
            print(x, "   ", self.used_item_links[x])

    def today_rental_title(self):
        print("Todays Rentals Title")
        print("----------------------------------")
        for x in range(len(self.all_listings)):
            print(x, "   ", self.all_listings[x])


if __name__ == '__main__':
    start_time = time.monotonic()
    fb_app = Controller()
    fb_app.login()
    # fb_app.open_mktplace()
    fb_app.open_rentals()
    # fb_app.search_item(item_name='1 bed',location_name='Elkhart')
    # used_item_links = fb_app.scrape_item_links()
    fb_app.scrape_item_links()
    print("\n")
    print("\n")
    print("####################################")
    print("\n")
    print("\n")
    fb_app.today_rental_links()
    fb_app.scrape_item_info()
    fb_app.today_rental_title()
    exit()
    # fb_app.scrape_item_info(used_item_links,category='smoker')
    # end_time = time.monotonic()
    # print('Runtime: ', timedelta(seconds=end_time - start_time))
