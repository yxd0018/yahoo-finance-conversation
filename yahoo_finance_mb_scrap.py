from selenium import webdriver
from time import sleep
import errno    
import os
import os.path
import datetime
import sys
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


xpath_dropdown = '//*[@id="canvass-0-CanvassApplet"]/div/div[3]/button'
xpath_time = '//*[@id="canvass-0-CanvassApplet"]/div/ul/li/div/div[1]/span/span'
xpath_update = '//*[@id="canvass-0-CanvassApplet"]/div/button[1]'
xpath_nextpage = '//*[@id="canvass-0-CanvassApplet"]/div/button[2]'
xpath_msg = '//*[@id="canvass-0-CanvassApplet"]/div/ul/li/div/div[2]/div'
xpath_poster = '//*[@id="canvass-0-CanvassApplet"]/div/ul/li/div/div[1]/button'

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

TRAFFIC_MED = ['aapl', ]
TRAFFIC_HIGH = [] #['aapl', ]

def build_chrome_options():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.accept_untrusted_certs = True
    chrome_options.assume_untrusted_cert_issuer = True
    # chrome configuration
    # More: https://github.com/SeleniumHQ/docker-selenium/issues/89
    # And: https://github.com/SeleniumHQ/docker-selenium/issues/87
    chrome_options.add_argument("incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1024,800")
    chrome_options.add_argument("disable-extensions")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--test-type=browser")
    chrome_options.add_argument("--disable-impl-side-painting")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-seccomp-filter-sandbox")
    chrome_options.add_argument("--disable-breakpad")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-cast")
    chrome_options.add_argument("--disable-cast-streaming-hw-encoding")
    chrome_options.add_argument("--disable-cloud-import")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-session-crashed-bubble")
    chrome_options.add_argument("--disable-ipv6")
    chrome_options.add_argument("--allow-http-screen-capture")
    return chrome_options 


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

           
def clickByText(text):
    driver.find_elements_by_xpath('//span[contains(text(),"' + text + '")]')[0].click()


def init(base):
    global driver
    driver = webdriver.Chrome("${CHROME_DRIVER}/chromedriver.exe", options=build_chrome_options())

    folderBase = base + '/' + datetime.date.today().strftime(DATE_FORMAT)
    mkdir_p(folderBase)
    return folderBase


def connect(symbol):
    driver.get("https://finance.yahoo.com/quote/" + symbol + "/community/")
    #from selenium.webdriver.support.ui import WebDriverWait
    #WebDriverWait(browser, 20).until(lambda browser: browser.execute_script("return document.readyState;") == "complete")


def selectReaction():
    clickByText('Top Reactions')
    clickByText('Newest Reactions')
    sleep(5)
    

def checkTime(symbol, time):
    timeStrDefault = ['last year', 'years ago', ]
    # timeStrDefault = ['last month', 'months ago', 'last year', 'years ago', ]
    timeStrMed = timeStrDefault + ['days ago', ]
    timeStrHigh = timeStrMed + ['yesterday', ]
    
    checkList = timeStrDefault
    if symbol in TRAFFIC_MED:
        checkList = timeStrMed
    if symbol in TRAFFIC_HIGH:
        checkList = timeStrHigh

    return reduce(lambda x, y: x and y, [ not s in time for s in checkList])
    
    
def expand(symbol):
    times = driver.find_elements_by_xpath(xpath_time)
    try:
        while checkTime(symbol, times[-1].text):
            clickByText('Show more')
            sleep(3)
            times = driver.find_elements_by_xpath(xpath_time)
    except:
        pass
        

def scrap(folderBase, s):
    filePath = folderBase + '/' + 'yahoo_mb_' + s + '.txt'
    output = open(filePath, 'w')
    output.write('=========\n')
    output.write('Timestamp: ' + datetime.datetime.now().strftime(TIME_FORMAT) + '\n')
    output.write('=========\n')
    posters = driver.find_elements_by_xpath(xpath_poster)
    times = driver.find_elements_by_xpath(xpath_time)
    msgs = driver.find_elements_by_xpath(xpath_msg)

    print(len(posters), len(times), len(msgs))
    
    try:
        for i in range(len(msgs)):
            try:
                soup = BeautifulSoup(msgs[i].text, 'html.parser').encode("utf-8")
                poster = posters[i].text
                time = times[i].text
                
                if not checkTime(s, time):
                    break
                    
                output.write(poster + ' @ ' + time + '\n')
                if soup.endswith('More'):
                    output.write(soup[:-4])
                else:
                    output.write(soup + '\n')
                output.write('---------\n')
            except Exception as ex:
                pass
    finally:
        output.close()
    return filePath


def main(argv):
    symbols = ['ftk', 'uan', 'asps', 'ocn', 'lxu', 'bbx', 'bxg', 'aapl']
    base = 'C:/temp'
    folderBase = init(base)
    
    for s in symbols:
        connect(s)
        selectReaction()
        expand(s)
        scrap(folderBase, s)
    print('saved to {}'.format(folderBase))


if __name__ == "__main__":
    main(sys.argv)
