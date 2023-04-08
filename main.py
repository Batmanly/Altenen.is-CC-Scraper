import re
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
start = time.time()
# proxy config for tor
options = webdriver.ChromeOptions()
proxy = '127.0.0.1:9050'
# run faster selenium
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('disable-cache')
options.add_argument('-ignore-certificate-errors')
options.add_argument('-ignore -ssl-errors')

#tor proxy
options.add_argument('--proxy-server=socks5://' + proxy)
#headless browser
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

links = set()
cc_list = set()
back = int(sys.argv[1])


# collect links from pages.
def open_and_import_cookie():
    # for import cookie open a page and copy the cookies
    driver.get('https://altenens.is/')
    # driver.get('https://ipinfo.io/')
    driver.add_cookie({
        "name": "PMBC",
        "value": ""
    })
    driver.add_cookie({"name": "xf_csrf", "value": ""})
    driver.add_cookie({
        "name": "xf_session",
        "value": ""
    })
    driver.add_cookie({
        "name":
            "xf_user",
        "value":
            ""
    })


def scrape_links(back):
    for i in range(back):
        driver.get(
            f'https://altenens.is/forums/accounts-and-database-dumps.45/page-{i + 1}?order=post_date&direction=desc'
        )
        elements = driver.find_elements(By.TAG_NAME, 'a')
        # don't add this links
        dont_add = [
            'https://altenens.is/threads/accounts-and-database-dumps-cc-posting-rules-must-read-100-updated-may-2021.1397037/',
            'https://altenens.is/threads/altenen-bin-checker-credit-card-generator-ip-checker.1390606/',
            'https://altenens.is/threads/atn-official-rules-all-members-must-read-and-follow-them.1055161/',
            'https://altenens.is/threads/accounts-and-database-dumps-cc-posting-rules-must-read-100-updated-may-2021.1397037/latest',
            'https://altenens.is/threads/western-union-transfer-bank-transfer-skrill-transfer-transferring-worldwide.271663/',
            'https://altenens.is/threads/altenen-bin-checker-credit-card-generator-ip-checker.1390606/page-3',
            'https://altenens.is/threads/altenen-bin-checker-credit-card-generator-ip-checker.1390606/latest',
            'https://altenens.is/threads/altenen-bin-checker-credit-card-generator-ip-checker.1390606/page-2'
        ]
        for element in elements:
            href = element.get_attribute('href')
            if 'https://altenens.is/threads/' not in str(href):
                continue
            elif str(href) in dont_add:
                continue
            elif '/lates' in str(href):
                continue
            elif '/unread' in str(href):
                continue
            else:
                links.add(element.get_attribute('href'))


def open_web_page(url):
    # Open a new window
    try:
        driver.get(url)
        # before close page get cc
        get_source = driver.page_source
        # get credit card from context
        cc = re.findall(r'\d{4}\d{4}\d{4}\d{4}', get_source)
        # write to file
        for i in cc:
            cc_list.add(i)
            # print(i)
        # Closing new_url tab
        # driver.close()
    except:
        pass


open_and_import_cookie()
scrape_links(back)
print(str(len(links)) + ' links found')
link_list = list(links)
# print(link_list)

for i in link_list:
    open_web_page(i)

driver.quit()
cc_list = list(cc_list)
with open('cc.txt', 'w') as f:
    for i in cc_list:
        f.write(i + '\n')
print(str(len(cc_list)) + ' credit cards found')
end = time.time()
print("The time of execution of above program is :", end-start)
