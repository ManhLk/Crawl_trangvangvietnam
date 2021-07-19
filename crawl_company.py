from numpy.core.defchararray import count
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from numpy.random import randint
import numpy as np
from datetime import datetime
from pymongo import MongoClient

cli = MongoClient(host='192.168.1.168', username='admin', password='CIST2o20')
clo = cli.company.trangvangvietnam

def init_driver():
    # Turn off notification
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)

    # Init driver
    driver = webdriver.Chrome('./chromedriver', chrome_options= chrome_options)
    driver.get("https://trangvangvietnam.com/")
    return driver

def next_page(driver):
    try:
        current_page = 1
        last_page = [a.text for a in driver.find_element_by_id("paging").find_elements_by_tag_name("a")][-2]
        last_page = int(last_page)
        while current_page <= last_page:
            sleep(randint(3,5))
            driver.find_element_by_xpath("//div[@id='paging']//a[text()='Tiếp']").click()
            current_page += 1
    except:
        print("Page tèo rồi next sao được nữa ^^!")

def get_company(driver, src_company):
    check = True
    driver.get(src_company)
    sleep(randint(3,5))

    company = {}
    # Name
    try:
        company['name'] = [detail.text for detail in driver.find_elements_by_xpath("//div[@class='thongtinchitiet']//div[@class='hosocongty_li']//div[@class='hosocongty_text']")][0]
    except:
        company['name'] = np.nan

    # Tax code
    try:
        detail = [detail.text for detail in driver.find_elements_by_xpath("//div[@class='thongtinchitiet']//div[@class='hosocongty_li']//div[@class='hosocongty_text']")]
        for d in detail:
            if str(d).isdigit() and len(str(d)) > 5:
                company['tax_code'] = d
        if 'tax_code' not in company or clo.find({"tax_code": company["tax_code"]}).count() > 0:
            return False, company
    except:
        return False, company

    # establish at 
    try:  
        company['establish_at'] = np.nan
        detail = [detail.text for detail in driver.find_elements_by_xpath("//div[@class='thongtinchitiet']//div[@class='hosocongty_li']//div[@class='hosocongty_text']")]
        for d in detail:
            d = str(d)
            if d.isdigit() and (int(d) >= 1000 and int(d)<= datetime.today().year):
                company['establish_at'] = d
    except:

        company['establish_at'] = np.nan

    # Introduce
    try:
        company['introduce'] = driver.find_element_by_xpath('//div[@class="thongtinchitiet"]//div[@class="gioithieucongty"]//p').text
    except:
        company['introduce'] = np.nan

    # Industry
    try:
        industry = [e.find_element_by_xpath('.//div[@class="nganhgnhe_chitiet_text"]//p//a').text for e in driver.find_elements_by_class_name("nganhnghe_chitiet_li")]
        company["industry"] = list(set(industry))
    except:
        company["industry"] = np.nan

    # Product
    try:
        product = {}
        for element in driver.find_elements_by_class_name("sanphamdichvu_phannhom_box"):
            try:
                group_product_name = element.find_element_by_class_name("tennhom_sp_text")
                for e in element.find_elements_by_class_name("tensanphamdichvu_box"):
                    if group_product_name.text not in product:
                        product[group_product_name.text] = [e.text]
                    else:
                        product[group_product_name.text].append(e.text)
            except:
                pass
        company['product'] = product
    except:
        company["product"] = np.nan

    # Website
    try:
        website = driver.find_element_by_class_name("text_website").text
        company['website'] = website
    except:
        company['website'] = np.nan

    # Email
    try:
        email = driver.find_element_by_class_name("text_email").text
        company['email'] = email
    except:
        company['email'] = np.nan    

    # Address
    try:
        company["address"] = driver.find_elements_by_class_name("diachi_chitiet_li")[0].find_element_by_class_name("diachi_chitiet_li2dc").text
    except:
        company["address"] = np.nan

    # phone number
    try:
        company["phone_number"] = driver.find_elements_by_class_name("diachi_chitiet_li")[1].find_element_by_class_name("diachi_chitiet_li2").text
    except:
        company["phone_number"] = np.nan

    # fax
    try:
        company["fax"] = driver.find_elements_by_class_name("diachi_chitiet_li")[2].find_element_by_class_name("diachi_chitiet_li2").text
    except:
        company["fax"] = np.nan

    # Create at:
    try:
        company["created_at"] = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    except:
        company["created_at"] = np.nan

    return (True, company)


if __name__ == "__main__":

    driver = init_driver()
    driver.find_element_by_xpath("//a[text()='+ Xem thêm']").click()
    sleep(randint(3,5))

    # Get industry
    industries = [industry.find_element_by_tag_name("a").get_attribute("href") for industry in  driver.find_elements_by_class_name("cell_niengiam")]
    
    for industry in set(industries):
        driver.get(industry)
        sleep(randint(3,5))
        try:
            for a in driver.find_elements_by_tag_name("a"):
                try:
                    src = a.get_attribute("href")
                    if not str(src).startswith("https://trangvangvietnam.com/categories/"):
                        continue

                    driver.get(src)
                    sleep(randint(2,5))
                    src_company = [company.find_element_by_xpath('.//div[@class="noidungchinh"]//h2[@class="company_name"]//a').get_attribute("href") for company in driver.find_elements_by_class_name("boxlistings")]
                    
                    # Next page
                    try:
                        current_page = 1
                        last_page = [a.text for a in driver.find_element_by_id("paging").find_elements_by_tag_name("a")][-2]
                        last_page = int(last_page)
                        while current_page <= last_page:
                            sleep(3)
                            driver.find_element_by_xpath("//div[@id='paging']//a[text()='Tiếp']").click()
                            current_page += 1
                            src_company += [company.find_element_by_xpath('.//div[@class="noidungchinh"]//h2[@class="company_name"]//a').get_attribute("href") for company in driver.find_elements_by_class_name("boxlistings")]
                    except:
                        print("Page tèo rồi next sao được nữa ^^!")

                    src_company = list(set(src_company))
                    for src_com in src_company:  
                        # Insert to MongoDB
                        cli = MongoClient(host='192.168.1.168', username="admin", password="CIST2o20")  
                        clo = cli.company.trangvangvietnam
                        check , company = get_company(driver, src_com)
                        if check:
                            clo.insert_one(company)
                except:
                    continue
        except:
            print("error")
            continue
    driver.close()
    








