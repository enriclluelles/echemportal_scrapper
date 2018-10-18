import time

from selenium import webdriver
import selenium.webdriver.chrome.service as service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

import sys
import os

try:
    filename = sys.argv[1]
except IndexError:
    filename = "./output.csv"

url = "https://www.echemportal.org/echemportal/propertysearch/treeselect_input.action"

service = service.Service('./chromedriver')
service.start()
driver = webdriver.Remote(service.service_url,
        DesiredCapabilities.CHROME.copy())

all_rows_content = []

def try_to_find_by_xpath(path,tries=10):
    try:
        return driver.find_element_by_xpath(path)
    except NoSuchElementException as e:
        if tries > 0:
            time.sleep(1)
            return try_to_find_by_xpath(path, tries - 1)
        else:
            raise Exception("too many tries")

def fetch_content():
    table = try_to_find_by_xpath('//*[@id="propertysearchresult"]/table/tbody')
    for row in table.find_elements_by_xpath('./tr'):
        row_content = []
        cols = row.find_elements_by_xpath("./td")
        for col in cols:
            row_content.append(col.text.replace("\n"," "))
        if len(cols) > 0:
            all_rows_content.append(";".join(row_content))
        print("appending {0}".format(row_content))
    go_to_next()

def go_to_next():
    try:
        driver.find_element_by_link_text("Next").click()
        driver.find_element_by_link_text("Click").click()
        fetch_content()
    except NoSuchElementException as e:
        print(e)
        pass

def write():
    print(all_rows_content)
    csv = open(filename,"w")
    csv.write("\n".join(all_rows_content))
    csv.close()


try:
    driver.get(url);

    link_to_upload = driver.find_element_by_css_selector("#querytree .queryblocktools a")
    link_to_upload.click()
    upload_file_input = driver.find_element_by_id("loadquery_execute_upload")
    upload_file_input.send_keys(os.getcwd() + "/sample_query.xml")
    driver.find_element_by_name('savebtn').click()
    driver.find_element_by_name('executebtn').click()
    time.sleep(5)
    fetch_content()
    write()
    driver.quit()
except:
    print(sys.exc_info()[0])
    write()
    driver.quit()
