import requests
from bs4 import BeautifulSoup
import csv
import re
import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from time import sleep
import os
from collections import Counter
import pickle
import warnings
import time
warnings.filterwarnings("ignore")

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import PIL
from PIL import Image, ImageFilter
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import boto3
import botocore

# Use proxy and headers for safe web scraping
# os.environ['HTTPS_PROXY'] = 'http://3.112.188.39:8080'

# pd.options.mode.chained_assignment = None
headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
    '537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}


def hover(browser, xpath):
    '''
    This function makes an automated mouse hovering in the selenium webdriver
    element based on its xpath.

    PARAMETER
    ---------
    browser: Selenium based webbrowser
    xpath: str
        xpath of the element in the webpage where hover operation has to be
        performed.
    '''
    element_to_hover_over = browser.find_element_by_xpath(xpath)
    hover = ActionChains(browser).move_to_element(element_to_hover_over)
    hover.perform()
    element_to_hover_over.click()

def browser(link):
    '''This funtion opens a selenium based chromebrowser specifically tuned
    to work for amazon product(singular item) webpages. Few functionality
    includes translation of webpage, clicking the initial popups, and hovering
    over product imagesso that the images can be scrape

    PARAMETER
    ---------
    link: str
        Amazon Product item link

    RETURN
    ------
    driver: Selenium web browser with operated functions
    '''
    options = Options()
    prefs = {
      "translate_whitelists": {"ja":"en","de":'en'},
      "translate":{"enabled":"true"}
    }
#     helium = r'C:\Users\Dell-pc\AppData\Local\Google\Chrome\User Data\Default\Extensions\njmehopjdpcckochcggncklnlmikcbnb\4.2.12_0'
#     options.add_argument(helium)
    chrome_path = r'C:/Users/Dell-pc/Desktop/publication/chromedriver.exe'
    options.add_experimental_option("prefs", prefs)
    options.headless = True
    driver = webdriver.Chrome(chrome_path,chrome_options=options)
    driver.get(link)
    try:
        driver.find_element_by_xpath('//*[@id="nav-main"]/div[1]/div[2]/div/div[3]/span[1]/span/input').click()
    except:
        pass
    try:
        hover(driver,'//*[@id="altImages"]/ul/li[3]')
    except:
        pass
    try:
        driver.find_element_by_xpath('//*[@id="a-popover-6"]/div/header/button/i').click()
    except:
        pass
    try:
        hover(driver,'//*[@id="altImages"]/ul/li[4]')
    except:
        pass
    try:
        driver.find_element_by_xpath('//*[@id="a-popover-6"]/div/header/button/i').click()
    except:
        pass
    try:
        hover(driver,'//*[@id="altImages"]/ul/li[5]')
    except:
        pass
    try:
        driver.find_element_by_xpath('//*[@id="a-popover-6"]/div/header/button/i').click()
    except:
        pass
    try:
        hover(driver,'//*[@id="altImages"]/ul/li[6]')
    except:
        pass
    try:
        driver.find_element_by_xpath('//*[@id="a-popover-6"]/div/header/button/i').click()
    except:
        pass
    try:
        hover(driver,'//*[@id="altImages"]/ul/li[7]')
    except:
        pass
    try:
        driver.find_element_by_xpath('//*[@id="a-popover-6"]/div/header/button/i').click()
    except:
        pass
    try:
        hover(driver,'//*[@id="altImages"]/ul/li[8]')
    except:
        pass
    try:
        driver.find_element_by_xpath('//*[@id="a-popover-6"]/div/header/button/i').click()
    except:
        pass
    try:
        hover(driver,'//*[@id="altImages"]/ul/li[9]')
    except:
        pass
    try:
        driver.find_element_by_xpath('//*[@id="a-popover-6"]/div/header/button/i').click()
    except:
        pass
    return driver

def scroll_temp(driver):
    '''
    Automated Scroller in Selenium Webbrowser

    PARAMETER
    ---------
    driver: Selenium Webbrowser
    '''
    pre_scroll_height = driver.execute_script('return document.body.scrollHeight;')
    run_time, max_run_time = 0, 2
    while True:
        iteration_start = time.time()
        # Scroll webpage, the 100 allows for a more 'aggressive' scroll
        driver.execute_script('window.scrollTo(0,0.6*document.body.scrollHeight);')

        post_scroll_height = driver.execute_script('return document.body.scrollHeight;')

        scrolled = post_scroll_height != pre_scroll_height
        timed_out = run_time >= max_run_time

        if scrolled:
            run_time = 0
            pre_scroll_height = post_scroll_height
        elif not scrolled and not timed_out:
            run_time += time.time() - iteration_start
        elif not scrolled and timed_out:
            break

def scroll(driver):
    '''
    Automated Scroller in Selenium Webbrowser with conditional find.

    PARAMETER
    ---------
    driver: Selenium Webbrowser
    '''

    scroll_temp(driver)
    try:
        element = driver.find_element_by_xpath('//*[@id="reviewsMedley"]/div/div[1]')
    except NoSuchElementException:
        try:
            element = driver.find_element_by_xpath('//*[@id="reviewsMedley"]')
        except NoSuchElementException:
            element = driver.find_element_by_xpath('//*[@id="detail-bullets_feature_div"]')
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()

def browser_link(product_link,country):
    '''Returns all the web link of the products based on the first
    page of the product category. It captures product link of all the pages for
    that specific product.

    PARAMETER
    ---------
    link: str
        The initial web link of the product page. This is generally the
        first page of the all the items for that specfic product

    RETURN
    ------
    links: list
        It is a list of strings which contains all the links of the items
        for the specific product

    '''
    driver = browser(product_link)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    try:
        pages_soup = soup.findAll("ul",{"class":"a-pagination"})
        pages = int(pages_soup[0].findAll("li",{'class':'a-disabled'})[1].text)
    except:
        pass
    try:
        pages_soup = soup.findAll("div",{"id":"pagn"})
        pages = int(pages_soup[0].findAll("span",{'class':'pagnDisabled'})[0].text)
    except:
        try:
            pages_soup = soup.findAll("div",{"id":"pagn"})
            pages = int(pages_soup[0].findAll("span",{'class':'pagnDisabled'})[1].text)
        except:
            pass
    print(pages)
    links = []

    for page in range(1,pages+1):
        print(page)
        link_page = product_link + 'page=' + str(page)
        driver_temp = browser(link_page)
        soup_temp = BeautifulSoup(driver_temp.page_source, 'lxml')
        search = soup_temp.findAll("div",{"class":"s-main-slot s-result-list s-search-results sg-row"})
        try:
            for i in range(len(search[1].findAll("h2"))):
                temp = search[1].findAll("h2")[i]
                for j in range(len(temp.findAll('a'))):
                    link = countries_link[country]+temp.findAll('a')[j].get('href')
                    links.append(link)
        except:
            try:
                for i in range(len(search[0].findAll("h2"))):
                    temp = search[0].findAll("h2")[i]
                    for j in range(len(temp.findAll('a'))):
                        link = countries_link[country]+temp.findAll('a')[j].get('href')
                        links.append(link)
                print(len(links))
            except:
                print('Not Scrapable')
    return links

def indexes(amazon_links,link_list):
    '''Returns the product main page link based on the country and the directory

    PARAMETERS
    ----------
    amazon_links: string
    link_list: list

    RETURN
    ------
    Product Catalog link: str

    '''
    amazon_dict = amazon_links
    if len(link_list) == 5:
        return amazon_dict[link_list[0]][link_list[1]][link_list[2]][link_list[3]][link_list[4]]
    elif len(link_list) == 4:
        return amazon_dict[link_list[0]][link_list[1]][link_list[2]][link_list[3]]
    elif len(link_list) == 3:
        return amazon_dict[link_list[0]][link_list[1]][link_list[2]]
    elif len(link_list) == 2:
        return amazon_dict[link_list[0]][link_list[1]]
    elif len(link_list) == 1:
        return amazon_dict[link_list[0]]
    else:
        return print("Invalid Product")

def products_links(country, **kwargs):
    '''
    This function returns all the web link for a user defined product for all
    the pages in Amazon.

    PARAMETER
    ---------
    country: string
        Country of interest
    RETURN
    ------
    main_links: list
        list of all the product catalog links

    '''
    amazon_links = amazon[country]
    directory_temp = []
    for key, value in kwargs.items():
        directory_temp.append(value)
    directory = '/'.join(directory_temp)
    print(directory)
    product_link = indexes(amazon_links,directory_temp)
    main_links = browser_link(product_link,country=country)
    return main_links,directory

def delete_images(filename):
    import os
    file_path = r'C:/Users/Dell-pc/Desktop/publication/test/'
    os.remove(file_path + filename)

def upload_s3(filename,key):
    key_id = 'AKIAWR6YW7N5ZKW35OJI'
    access_key = 'h/xrcI9A2SRU0ds+zts4EClKAqbzU+/iXdiDcgzm'
    bucket_name = 'amazon-data-ecfullfill'
    s3 = boto3.client('s3',aws_access_key_id=key_id,
                      aws_secret_access_key=access_key)
    try:
        s3.upload_file(filename,bucket_name,key)
    except FileNotFoundError:
        pass

def product_info(link,directory,country):
    '''Get all the product information of an Amazon Product

    PARAMETER
    ---------
    link: string
        Product link from the catalog of specific product
    directory: string
        Directory where all the data(images and database file) of the product
        will be stored
    country: string
        Country of interest

    RETURN
    ------
    product_title: string
        Title of the product
    rating_star: string
        Star rating of the product
    overall_rating: string
        Total number of feedbacks
    company: string
        Name of the company of the product
    price: string
        Price of the product based on country's currency
    product_highlights: string
        Short snippet of the product description
    product_length: string
        In terms of dimension, length of the product
    product_width: string
        In terms of dimension, width of the product
    product_height: string
        In terms of dimension, height of the product
    product_weight: string
        In terms of dimension, weight of the product
    asin: string
        Amazon Standard Identification Number, a unique identifier of each product in Amazon
    pd_unit: string
        Product Dimension SI unit
    best_seller_cat: string
        Best Seller rank of the product based on Category
    best_seller_prod: string
        Best Seller rank of the product based on Product type
    weight_unit: string
        SI unit of product weight
    shipping_weight: string
        Weight of the product including the shipping package
    shipping_weight_unit: string
        SI unit of shipping weight
    crr_5: string
        Customer Review Rating for 5 Stars
    crr_4: string
        Customer Review Rating for 4 Stars
    crr_3: string
        Customer Review Rating for 3 Stars
    crr_2: string
        Customer Review Rating for 2 Stars
    crr_1: string
        Customer Review Rating for 1 Stars
    crr_fr_1: string
        Customer Review Rating by feature for Feature 1
    crr_fr_2: string
        Customer Review Rating by feature for Feature 2
    crr_fr_3: string
        Customer Review Rating by feature for Feature 3
    tags: string
        List of tags associated with the product
    directory: string
        Directory in S3 bucket where the data(images and database file) is stored
    '''

    #Opening Selenium Webdrive with Amazon product
    driver = browser(link)
    time.sleep(4)
    scroll(driver)
    time.sleep(2)

    #Initializing BeautifulSoup operation in selenium browser
    selenium_soup = BeautifulSoup(driver.page_source, 'lxml')

    #Product Title
    try:
        product_title = driver.find_element_by_xpath('//*[@id="productTitle"]').text
    except:
        product_title = 'Not Scrapable'
    print(product_title)

    #Ratings - Star
    try:
        rating_star = float(selenium_soup.findAll('span',{'class':'a-icon-alt'})[0].text.split()[0])
    except:
        rating_star = 'Not Scrapable'
    print(rating_star)

    #Rating - Overall
    try:
        overall_rating = int(selenium_soup.findAll('span',{'id':'acrCustomerReviewText'})[0].text.split()[0].replace(',',''))
    except:
        overall_rating = 'Not Scrapable'
    print(overall_rating)

    #Company
    try:
        company = selenium_soup.findAll('a',{'id':'bylineInfo'})[0].text
    except:
        company = 'Not Scrapable'
    print(country)

    #Price
    try:
        denomination = '$'
        if country=='UAE':
            denomination = selenium_soup.findAll('span',{'id':'priceblock_ourprice'})[0].text[:3]
            price = float(selenium_soup.findAll('span',{'id':'priceblock_ourprice'})[0].text[3:])
        else:
            denomination = selenium_soup.findAll('span',{'id':'priceblock_ourprice'})[0].text[0]
            price = float(selenium_soup.findAll('span',{'id':'priceblock_ourprice'})[0].text[1:])
    except:
        try:
            if country=='UAE':
                try:
                    price = float(selenium_soup.findAll('span',{'id':'priceblock_ourprice'})[0].text[3:].replace(',',''))
                except:
                    price = float(selenium_soup.findAll('span',{'id':'priceblock_dealprice'})[0].text[3:].replace(',',''))
            else:
                try:
                    price = float(selenium_soup.findAll('span',{'id':'priceblock_ourprice'})[0].text[3:].replace(',',''))
                except:
                    price = float(selenium_soup.findAll('span',{'id':'priceblock_dealprice'})[0].text[3:].replace(',',''))
        except:
            denomination = 'Not Scrapable'
            price = 'Not Scrapable'
    print(denomination,price)

    #Product Highlights
    try:
        temp_ph = selenium_soup.findAll('ul',{'class':'a-unordered-list a-vertical a-spacing-none'})[0].findAll('li')
        counter_ph = len(temp_ph)
        product_highlights = []
        for i in range(counter_ph):
            raw = temp_ph[i].text
            clean = raw.strip()
            product_highlights.append(clean)
        product_highlights = '<CPT14>'.join(product_highlights)
    except:
        try:
            temp_ph = selenium_soup.findAll('div',{'id':'rich-product-description'})[0].findAll('p')
            counter_ph = len(temp_ph)
            product_highlights = []
            for i in range(counter_ph):
                raw = temp_ph[i].text
                clean = raw.strip()
                product_highlights.append(clean)
            product_highlights = '<CPT14>'.join(product_highlights)
        except:
            product_highlights = 'Not Available'
    print(product_highlights)

    #Helium

    #Product Details/Dimensions:
    #USA
    try:
        temp_pd = selenium_soup.findAll('div',{'class':'content'})[0].findAll('ul')[0].findAll('li')
        counter_pd = len(temp_pd)
        for i in range(counter_pd):
            try:
                if re.findall('ASIN',temp_pd[i].text)[0]:
                    try:
                        asin = temp_pd[i].text.split(' ')[1]
                    except:
                        pass
            except IndexError:
                pass
            try:
                if re.findall('Product Dimensions|Product Dimension|Product dimensions',temp_pd[i].text)[0]:
                    pd_temp = temp_pd[i].text.strip().split('\n')[2].strip().split(';')
                    try:
                        product_length = float(pd_temp[0].split('x')[0])
                    except IndexError:
                        pass
                    try:
                        product_width = float(pd_temp[0].split('x')[1])
                    except IndexError:
                        pass
                    try:
                        product_height = float(pd_temp[0].split('x')[2].split(' ')[1])
                    except IndexError:
                        pass
                    try:
                        pd_unit = pd_temp[0].split('x')[2].split(' ')[2]
                    except IndexError:
                        pass
                    try:
                        product_weight = float(pd_temp[1].split(' ')[1])
                    except IndexError:
                        pass
                    try:
                        weight_unit = pd_temp[1].split(' ')[2]
                    except IndexError:
                        pass
            except:
                pass
            try:
                if re.findall('Shipping Weight|Shipping weight|shipping weight',temp_pd[i].text)[0]:
                    sweight_temp = temp_pd[i].text.split(':')[1].strip().split(' ')
                    shipping_weight = float(sweight_temp[0])
                    shipping_weight_unit = sweight_temp[1]
            except IndexError:
                pass
            try:
                if re.findall('Amazon Best Sellers Rank|Amazon Bestsellers Rank',temp_pd[i].text)[0]:
                    x = temp_pd[i].text.replace('\n','').split(' ')
                    indexes = []
                    for j,k in enumerate(x):
                        if re.findall('#',k):
                            indexes.append(j)
                    try:
                        best_seller_cat = int(temp_pd[i].text.strip().replace('\n','').split(' ')[3].replace(',',''))
                        best_seller_prod = int(x[indexes[0]].split('#')[1].split('in')[0])
                    except:
                        try:
                            best_seller_cat = x[indexes[0]].split('#')[1]
                        except:
                            pass
                        try:
                            best_seller_prod = x[indexes[1]].split('#')[1].split('in')[0]
                        except:
                            pass
            except IndexError:
                pass
        print(asin)
    except:
        pass

    try:
        temp_pd = selenium_soup.findAll('div',{'class':'content'})[1].findAll('ul')[0].findAll('li')
        counter_pd = len(temp_pd)
        for i in range(counter_pd):
            try:
                if re.findall('ASIN',temp_pd[i].text)[0]:
                    try:
                        asin = temp_pd[i].text.split(' ')[1]
                    except:
                        pass
            except IndexError:
                pass
            try:
                if re.findall('Product Dimensions|Product Dimension|Product dimensions',temp_pd[i].text)[0]:
                    pd_temp = temp_pd[i].text.strip().split('\n')[2].strip().split(';')
                    try:
                        product_length = float(pd_temp[0].split('x')[0])
                    except IndexError:
                        pass
                    try:
                        product_width = float(pd_temp[0].split('x')[1])
                    except IndexError:
                        pass
                    try:
                        product_height = float(pd_temp[0].split('x')[2].split(' ')[1])
                    except IndexError:
                        pass
                    try:
                        pd_unit = pd_temp[0].split('x')[2].split(' ')[2]
                    except IndexError:
                        pass
                    try:
                        product_weight = float(pd_temp[1].split(' ')[1])
                    except IndexError:
                        pass
                    try:
                        weight_unit = pd_temp[1].split(' ')[2]
                    except IndexError:
                        pass
            except:
                pass
            try:
                if re.findall('Shipping Weight|Shipping weight|shipping weight',temp_pd[i].text)[0]:
                    sweight_temp = temp_pd[i].text.split(':')[1].strip().split(' ')
                    shipping_weight = float(sweight_temp[0])
                    shipping_weight_unit = sweight_temp[1]
            except IndexError:
                pass
            try:
                if re.findall('Amazon Best Sellers Rank|Amazon Bestsellers Rank',temp_pd[i].text)[0]:
                    x = temp_pd[i].text.replace('\n','').split(' ')
                    indexes = []
                    for j,k in enumerate(x):
                        if re.findall('#',k):
                            indexes.append(j)
                    try:
                        best_seller_cat = int(temp_pd[i].text.strip().replace('\n','').split(' ')[3].replace(',',''))
                        best_seller_prod = int(x[indexes[0]].split('#')[1].split('in')[0])
                    except:
                        try:
                            best_seller_cat = x[indexes[0]].split('#')[1]
                        except:
                            pass
                        try:
                            best_seller_prod = x[indexes[1]].split('#')[1].split('in')[0]
                        except:
                            pass
            except IndexError:
                pass
        print(asin)
    except:
        pass

    #India
    try:
        temp_pd = selenium_soup.findAll('div',{'class':'content'})[0].findAll('ul')[0].findAll('li')
        counter_pd = len(temp_pd)
        for i in range(counter_pd):
            try:
                if re.findall('ASIN',temp_pd[i].text)[0]:
                    asin = temp_pd[i].text.split(' ')[1]
            except:
                pass
            try:
                if re.findall('Product Dimensions|Product Dimension|Product dimensions',temp_pd[i].text)[0]:
                    pd_temp = temp_pd[i].text.strip().split('\n')[2].strip().split(' ')
                    try:
                        product_length = float(pd_temp[0])
                    except:
                        pass
                    try:
                        product_width = float(pd_temp[2])
                    except:
                        pass
                    try:
                        product_height = float(pd_temp[4])
                    except:
                        pass
                    try:
                        pd_unit = pd_temp[5]
                    except:
                        pass
                    try:
                        product_weight = float(pd_temp[1].split(' ')[1])
                    except:
                        pass
                    try:
                        weight_unit = pd_temp[1].split(' ')[2]
                    except:
                        pass
                print(asin)
            except IndexError:
                pass
            try:
                if re.findall('Shipping Weight|Shipping weight|shipping weight',temp_pd[i].text)[0]:
                    sweight_temp = temp_pd[i].text.split(':')[1].strip().split(' ')
                    shipping_weight = float(sweight_temp[0])
                    shipping_weight_unit = sweight_temp[1]
            except IndexError:
                pass
            try:
                if re.findall('Item Weight|Product Weight|Item weight|Product weight|Boxed-product Weight',temp_pd[i].text)[0]:
                    pd_weight_temp = temp_pd[i].text.replace('\n','').strip().split('     ')[1].strip()
                    product_weight = float(pd_weight_temp.split(' ')[0])
                    weight_unit = pd_weight_temp.split(' ')[1]
            except IndexError:
                pass
            try:
                if re.findall('Amazon Best Sellers Rank|Amazon Bestsellers Rank',temp_pd[i].text)[0]:
                    x = temp_pd[i].text.strip().replace('\n','').split(' ')
                    indexes = []
                    for j,k in enumerate(x):
                        if re.findall('#',k):
                            indexes.append(j)
                    try:
                        best_seller_cat = int(temp_pd[i].text.strip().replace('\n','').split(' ')[3].replace(',',''))
                        best_seller_prod = int(x[indexes[0]].split('#')[1].split('in')[0])
                    except:
                        try:
                            best_seller_cat = x[indexes[0]].split('#')[1]
                        except:
                            pass
                        try:
                            best_seller_prod = x[indexes[1]].split('#')[1].split('in')[0]
                        except:
                            pass
            except IndexError:
                pass
            print(asin)
    except:
        pass
    try:
        try:
            asin = list(selenium_soup.findAll('div',{'class':'pdTab'})[1].findAll('tr')[0].findAll('td')[1])[0]
        except:
            pass
        try:
            dimensions = list(selenium_soup.findAll('div',{'class':'pdTab'})[0].findAll('tr')[0].findAll('td')[1])[0]
        except:
            pass
        try:
            weight_temp = list(selenium_soup.findAll('div',{'class':'pdTab'})[1].findAll('tr')[1].findAll('td')[1])[0]
        except:
            pass
        try:
            best_seller_cat = float(list(selenium_soup.findAll('div',{'class':'pdTab'})[1].findAll('tr')[5].findAll('td')[1])[0].split('\n')[-1].split(' ')[0].replace(',',''))
        except:
            pass
        try:
            best_seller_prod = int(list(list(list(list(selenium_soup.findAll('div',{'class':'pdTab'})[1].findAll('tr')[5].findAll('td')[1])[5])[1])[1])[0].replace('#',''))
        except:
            pass
        try:
            product_length = float(dimensions.split('x')[0])
        except:
            pass
        try:
            product_width = float(dimensions.split('x')[1])
        except:
            pass
        try:
            product_height = float(dimensions.split('x')[2].split(' ')[1])
        except:
            pass
        try:
            product_weight = weight_temp.split(' ')[0]
        except:
            pass
        try:
            weight_unit = weight_temp.split(' ')[1]
        except:
            pass
        try:
            pd_unit = dimensions.split(' ')[-1]
        except:
            pass
        print(asin)
    except:
        try:
            for j in [0,1]:
                temp_pd = selenium_soup.findAll('table',{'class':'a-keyvalue prodDetTable'})[j].findAll('tr')
                for i in range(len(temp_pd)):
                    if re.findall('ASIN',temp_pd[i].text):
                        asin = temp_pd[i].text.strip().split('\n')[3].strip()
                    if re.findall('Item Model Number|Item model number',temp_pd[i].text):
                        bait = temp_pd[i].text.strip().split('\n')[3].strip()
                    if re.findall('Best Sellers Rank|Amazon Best Sellers Rank|Amazon Bestsellers Rank',temp_pd[i].text):
                        x = temp_pd[i].text.strip().replace('\n','').split(' ')
                        indexes = []
                        for j,k in enumerate(x):
                            if re.findall('#',k):
                                indexes.append(j)
                        best_seller_cat = int(x[indexes[0]].split('#')[1])
                        best_seller_prod = int(x[indexes[1]].split('#')[1].split('in')[0])
                    if re.findall('Product Dimensions|Product dimension|Product Dimension',temp_pd[i].text):
                        dimensions = temp_pd[i].text.strip().split('\n')[3].strip().split('x')
                        product_length = float(dimensions[0].strip())
                        product_width = float(dimensions[1].strip())
                        product_height = float(dimensions[2].strip().split(' ')[0])
                        pd_unit = dimensions[2].strip().split(' ')[1]
                    if re.findall('Item Weight|Product Weight|Item weight|Boxed-product Weight',temp_pd[i].text):
                        weight_temp = temp_pd[i].text.strip().split('\n')[3].strip()
                        product_weight = float(weight_temp.split(' ')[0])
                        weight_unit = weight_temp.split(' ')[1]
                    if re.findall('Shipping Weight|Shipping weight|shipping weight',temp_pd[i].text):
                        sweight_temp = temp_pd[i].text.replace('\n','').strip().split('                      ')[1].lstrip().split(' ')
                        shipping_weight = float(sweight_temp[0])
                        shipping_weight_unit = sweight_temp[1]
                print(asin,bait)
        except:
            try:
                temp_pd = selenium_soup.findAll('div',{'id':'prodDetails'})[0].findAll('tr')
                for i in range(len(temp_pd)):
                    if re.findall('ASIN',temp_pd[i].text):
                        asin = temp_pd[i].text.strip().split('\n')[3].strip()
                    if re.findall('Best Sellers Rank|Amazon Best Sellers Rank|Amazon Bestsellers Rank',temp_pd[i].text):
                        x = temp_pd[i].text.strip().replace('\n','').split(' ')
                        indexes = []
                        for j,k in enumerate(x):
                            if re.findall('#',k):
                                indexes.append(j)
                        best_seller_cat = int(x[indexes[0]].split('#')[1])
                        best_seller_prod = int(x[indexes[1]].split('#')[1].split('in')[0])
                    if re.findall('Product Dimensions|Product dimension|Product Dimension',temp_pd[i].text):
                        dimensions = temp_pd[i].text.strip().split('\n')[3].strip().split('x')
                        product_length = float(dimensions[0].strip())
                        product_width = float(dimensions[1].strip())
                        product_height = float(dimensions[2].strip().split(' ')[0])
                        pd_unit = dimensions[2].strip().split(' ')[1]
                    if re.findall('Item Weight|Product Weight|Item weight|Boxed-product Weight',temp_pd[i].text):
                        weight_temp = temp_pd[i].text.strip().split('\n')[3].strip()
                        product_weight = float(weight_temp.split(' ')[0])
                        weight_unit = weight_temp.split(' ')[1]
                    if re.findall('Shipping Weight|Shipping weight|shipping weight',temp_pd[i].text):
                        sweight_temp = temp_pd[i].text.replace('\n','').strip().split('                      ')[1].lstrip().split(' ')
                        shipping_weight = float(sweight_temp[0])
                        shipping_weight_unit = sweight_temp[1]
            except:
                try:
                    temp_pd = selenium_soup.findAll('div',{'id':'detail_bullets_id'})[0].findAll('tr')[0].findAll('li')
                    for i in range(len(temp_pd)):
                        if re.findall('ASIN',temp_pd[i].text):
                            asin = temp_pd[i].text.strip().split(':')[1].strip()
                        if re.findall('Best Sellers Rank|Amazon Best Sellers Rank|Amazon Bestsellers Rank',temp_pd[i].text):
                            x = temp_pd[i].text.strip().replace('\n','').split(' ')
                            indexes = []
                            for j,k in enumerate(x):
                                if re.findall('#',k):
                                    indexes.append(j)
                            best_seller_cat = int(x[indexes[0]].split('#')[1])
                            best_seller_prod = int(x[indexes[1]].split('#')[1].split('in')[0])
                        if re.findall('Product Dimensions|Product dimension|Product Dimension',temp_pd[i].text):
                            dimensions = temp_pd[i].text.strip().split('\n')[2].strip().split('x')
                            product_length = float(dimensions[0].strip())
                            product_width = float(dimensions[1].strip())
                            product_height = float(dimensions[2].strip().split(' ')[0])
                            pd_unit = dimensions[2].strip().split(' ')[1]
                        if re.findall('Item Weight|Product Weight|Item weight|Boxed-product Weight',temp_pd[i].text):
                            weight_temp = temp_pd[i].text.strip().split('\n')[2].strip()
                            product_weight = float(weight_temp.split(' ')[0])
                            weight_unit = weight_temp.split(' ')[1]
                        if re.findall('Shipping Weight|Shipping weight|shipping weight',temp_pd[i].text):
                            sweight_temp = temp_pd[i].text.replace('\n','').strip().split('                      ')[1].lstrip().split(' ')
                            shipping_weight = float(sweight_temp[0])
                            shipping_weight_unit = sweight_temp[1]
                except:
                    pass
    try:
        print(asin)
    except NameError:
        asin = 'Not Scrapable'
    try:
        print(best_seller_cat)
    except NameError:
        best_seller_cat = 'Not Scrapable'
    try:
        print(best_seller_prod)
    except NameError:
        best_seller_prod = 'Not Scrapable'
    try:
        print(product_length)
    except NameError:
        product_length = 'Not Scrapable'
    try:
        print(product_width)
    except NameError:
        product_width = 'Not Scrapable'
    try:
        print(product_height)
    except NameError:
        product_height = 'Not Scrapable'
    try:
        print(product_weight)
    except NameError:
        product_weight = 'Not Scrapable'
    try:
        print(weight_unit)
    except NameError:
        weight_unit = 'Not Scrapable'
    try:
        print(pd_unit)
    except NameError:
        pd_unit = 'Not Scrapable'
    try:
        print(shipping_weight_unit)
    except NameError:
        shipping_weight_unit = 'Not Scrapable'
    try:
        print(shipping_weight)
    except NameError:
        shipping_weight = 'Not Scrapable'

    print(product_length,product_width,product_height,product_weight,asin,pd_unit,
          best_seller_cat,best_seller_prod,weight_unit,shipping_weight,shipping_weight_unit)

    #Customer Review Ratings - Overall
    time.sleep(0.5)
    try:
        temp_crr = selenium_soup.findAll('table',{'id':'histogramTable'})[1].findAll('a')
        crr_main = {}
        crr_temp = []
        counter_crr = len(temp_crr)
        for i in range(counter_crr):
            crr_temp.append(temp_crr[i]['title'])
        crr_temp = list(set(crr_temp))
        for j in range(len(crr_temp)):
            crr_temp[j] = crr_temp[j].split(' ')
            stopwords = ['stars','represent','of','rating','reviews','have']
            for word in list(crr_temp[j]):
                if word in stopwords:
                    crr_temp[j].remove(word)
            print(crr_temp[j])
            try:
                if re.findall(r'%',crr_temp[j][1])[0]:
                    crr_main.update({int(crr_temp[j][0]): int(crr_temp[j][1].replace('%',''))})
            except:
                crr_main.update({int(crr_temp[j][1]): int(crr_temp[j][0].replace('%',''))})
    except:
        try:
            temp_crr = selenium_soup.findAll('table',{'id':'histogramTable'})[1].findAll('span',{'class':'a-offscreen'})
            crr_main = {}
            counter_crr = len(temp_crr)
            star = counter_crr
            for i in range(counter_crr):
                crr_main.update({star:int(temp_crr[i].text.strip().split('/n')[0].split(' ')[0].replace('%',''))})
                star -= 1
        except:
            pass
    try:
        crr_5 = crr_main[5]
    except:
        crr_5 = 0
    try:
        crr_4 = crr_main[4]
    except:
        crr_4 = 0
    try:
        crr_3 = crr_main[3]
    except:
        crr_3 = 0
    try:
        crr_2 = crr_main[2]
    except:
        crr_2 = 0
    try:
        crr_1 = crr_main[1]
    except:
        crr_1 = 0

    #Customer Review Ratings - By Feature
    time.sleep(1)
    try:
        driver.find_element_by_xpath('//*[@id="cr-summarization-attributes-list"]/div[4]/a/span').click()
        temp_fr = driver.find_element_by_xpath('//*[@id="cr-summarization-attributes-list"]').text
        temp_fr = temp_fr.split('\n')
        crr_feature_title = []
        crr_feature_rating = []
        for i in [0,2,4]:
             crr_feature_title.append(temp_fr[i])
        for j in [1,3,5]:
            crr_feature_rating.append(temp_fr[j])
        crr_feature = dict(zip(crr_feature_title,crr_feature_rating))
    except:
        try:
            temp_fr = driver.find_element_by_xpath('//*[@id="cr-summarization-attributes-list"]').text
            temp_fr = temp_fr.split('\n')
            crr_feature_title = []
            crr_feature_rating = []
            for i in [0,2,4]:
                 crr_feature_title.append(temp_fr[i])
            for j in [1,3,5]:
                crr_feature_rating.append(temp_fr[j])
            crr_feature = dict(zip(crr_feature_title,crr_feature_rating))
        except:
            crr_feature = 'Not Defined'
    try:
        crr_feature_key = list(crr_feature.keys())
    except:
        pass
    try:
        crr_fr_1 = crr_feature[crr_feature_key[0]]
    except:
        crr_fr_1 = 0
    try:
        crr_fr_2 = crr_feature[crr_feature_key[1]]
    except:
        crr_fr_2 = 0
    try:
        crr_fr_3 = crr_feature[crr_feature_key[2]]
    except:
        crr_fr_3 = 0

    #Tags:
    time.sleep(1)
    try:
        temp_tags = selenium_soup.findAll('div',{'class':'cr-lighthouse-terms'})[0]
        counter_tags = len(temp_tags)
        print('Counter Tags:',counter_tags)
        tags = []
        for i in range(counter_tags):
            tags.append(temp_tags.findAll('span')[i].text.strip())
            print(tags[i])
    except:
        tags = ['None']
    try:
        for feature in crr_feature_key:
            tags.append(feature)
    except:
        pass
    tags = list(set(tags))
    tags = '<CPT14>'.join(tags)
    print(tags)


    #Images
    images = []
    for i in [0,3,4,5,6,7,8,9]:
        try:
            images.append(selenium_soup.findAll('div',{'class':'imgTagWrapper'})[i].find('img')['src'])
        except:
            pass
    import urllib.request
    for i  in range(len(images)):
        if asin =='Not Scrapable':
            product_image = "{}_{}.jpg".format(product_title,i)
            product_image = product_image.replace('/','')
            urllib.request.urlretrieve(images[i],product_image)
#             upload_s3("{}_{}.jpg".format(product_title,i),
#                       directory+"/images/" + product_image)
#             delete_images(product_image)
        else:
            product_image = "{}_{}.jpg".format(asin,i)
            product_image = product_image.replace('/','')
            urllib.request.urlretrieve(images[i],product_image)
#             upload_s3("{}_{}.jpg".format(asin,i),
#                       directory+"/images/" + product_image)
#             delete_images(product_image)
    try:
        with open("{}.html".format(asin), "w",encoding='utf-8') as file:
            file.write(str(selenium_soup))
    except:
        with open("{}.html".format(product_title), "w",encoding='utf-8') as file:
            file.write(str(selenium_soup))
    return [product_title,rating_star,overall_rating,company,price,
            product_highlights,product_length,product_width,product_height,
            product_weight,asin,pd_unit,best_seller_cat,best_seller_prod,
            weight_unit,shipping_weight,shipping_weight_unit,crr_5,crr_4,
            crr_3,crr_2,crr_1,crr_fr_1,crr_fr_2,crr_fr_3,tags,directory]

def database(product_data,**kwargs):
    '''This function creates and updates the database file of the product

    PARAMETER
    ---------
    product_data: list
        list of product information gathered while scraping by product_info function
    '''
    try:
        try:
            link = kwargs['link']
        except KeyError:
            print('Error in Link')
        try:
            country = kwargs['country']
        except KeyError:
            print("Enter Country Name")
        try:
            cat1 = kwargs['cat1']
        except KeyError:
            pass
        try:
            cat2 = kwargs['cat2']
        except KeyError:
            pass
        try:
            cat3 = kwargs['cat3']
        except KeyError:
            pass
        try:
            cat4 = kwargs['cat4']
        except KeyError:
            pass
        try:
            product = kwargs['product']
        except KeyError:
            print("Enter Product Name")
        metadata = [link,country,cat1,cat2,cat3,cat4,product]
    except NameError:
        try:
            cat4 = None
            metadata = [link,country,cat1,cat2,cat3,cat4,product]
        except NameError:
            try:
                cat4 = None
                cat3 = None
                metadata = [link,country,cat1,cat2,cat3,cat4,product]
            except NameError:
                cat4 = None
                cat3 = None
                cat2 = None
                metadata = [link,country,cat1,cat2,cat3,cat4,product]
    conn = sqlite3.connect('{}.db'.format(product))
    headers = ['link','country','cat1','cat2','cat3','cat4','product','product_title',
               'rating_star','overall_rating','company','price',
               'product_highlights','product_length','product_width','product_height',
               'product_weight','asin','pd_unit','best_seller_cat','best_seller_prod',
               'weight_unit','shipping_weight','shipping_weight_unit','crr_5','crr_4',
               'crr_3','crr_2','crr_1','crr_fr_1','crr_fr_2','crr_fr_3','tags','images_link']
    product_data.append(metadata)
    product_data = product_data[-1] + product_data[:len(product_data)-1]
    temp = pd.DataFrame(data= [product_data],columns=headers)
    temp.to_sql('Product',conn,if_exists='append')
#     upload_s3(product+'.db',directory+'/'+product+'.db')
    conn.close()

def checkpoint(link_list,directory,product):
    '''This chehckpoint function makes sure that if ever, the scraping is
        interrupted and restarted, the scraper starts from.

    PARAMETER
    ---------
    link_list: list
        List that contains all the links of the product Catalog.

    directory: string
        Directory where the data(image and database file) is stored

    product: string
        Name of the product

    RETURN
    ------
    new_list: list
        List of all the products that needs to be scraped
    '''
#     BUCKET_NAME = 'amazon-data-ecfullfill'
#     key_id = 'AKIAWR6YW7N5ZKW35OJI'
#     access_key = 'h/xrcI9A2SRU0ds+zts4EClKAqbzU+/iXdiDcgzm'
#     KEY = '{}/{}.db'.format(directory,product)
#     s3 = boto3.resource('s3',aws_access_key_id=key_id,
#                           aws_secret_access_key=access_key)
#     try:
#         s3.Bucket(BUCKET_NAME).download_file(KEY, 'test.db')
#     except botocore.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             print("The object does not exist.")
#         else:
#             raise
    conn = sqlite3.connect('{}.db'.format(product))
    try:
        df = pd.read_sql('''SELECT * FROM Product''', conn)
        product_link = df['link'].unique()
        new_list = []
        for i in link_list:
            if i in product_link:
                pass
            else:
                new_list.append(i)
    except:
        new_list = link_list
    return new_list
