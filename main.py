import os
import re
import sys
import time

import structlog
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# LOGGING
LOG = structlog.get_logger()

# Install driver

load_dotenv()
COOKIE = os.getenv("COOKIE")

start = time.time()

# proxy config for tor

# Tor proxy Settings
# proxy = '127.0.0.1:9050'
# options.add_argument('--proxy-server=socks5://' + proxy)

options = webdriver.ChromeOptions()
# Faster Chrome config
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-gpu")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--headless")

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=options)

links = set()
cc_list = set()
if len(sys.argv) < 2:
    back = 1
else:
    back = int(sys.argv[1])


# collect links from pages.
def open_and_import_cookie(COOKIE):
    # for import cookie open a page and copy the cookies
    driver.get("https://altenens.is/")
    cookie_list = COOKIE.split(";")
    for cookie in cookie_list:
        cookie = cookie.split("=")
        driver.add_cookie({"name": cookie[0], "value": cookie[1]})
    driver.refresh()


def scrape_links(back):
    for i in range(back):
        driver.get(
            f"https://altenens.is/forums/accounts-and-database-dumps.45/page"
            f"-{i + 1}?order=post_date&direction=desc"
        )
        elements = driver.find_elements(By.TAG_NAME, "a")
        # don't add this links
        dont_add = [
            "https://altenens.is/threads/accounts-and-database-dumps-cc"
            "-posting-rules-must-read-100-updated-may-2021.1397037/",
            "https://altenens.is/threads/altenen-bin-checker-credit-card"
            "-generator-ip-checker.1390606/",
            "https://altenens.is/threads/atn-official-rules-all-members-must"
            "-read-and-follow-them.1055161/",
            "https://altenens.is/threads/accounts-and-database-dumps-cc"
            "-posting-rules-must-read-100-updated-may-2021.1397037/latest",
            "https://altenens.is/threads/western-union-transfer-bank"
            "-transfer-skrill-transfer-transferring-worldwide.271663/",
            "https://altenens.is/threads/altenen-bin-checker-credit-card"
            "-generator-ip-checker.1390606/page-3",
            "https://altenens.is/threads/altenen-bin-checker-credit-card"
            "-generator-ip-checker.1390606/latest",
            "https://altenens.is/threads/altenen-bin-checker-credit-card"
            "-generator-ip-checker.1390606/page-2",
        ]
        for element in elements:
            href = element.get_attribute("href")
            if "https://altenens.is/threads/" not in str(href):
                continue
            elif str(href) in dont_add:
                continue
            elif "/lates" in str(href):
                continue
            elif "/unread" in str(href):
                continue
            else:
                links.add(element.get_attribute("href"))


def open_web_page(url):
    try:
        driver.get(url)

        # before close page get cc
        get_source = driver.page_source
        # get credit card from source

        # matches = re.findall(r'(\d{16})\|(\d{2})\|(\d{4})\|(\d{3})',
        # get_source)
        regex1 = re.findall(
            r"(\d{16})\|(\d{2})\|(\d{4})\|(\d{3})", get_source
        )  # [('4201996000195279', '01', '2026', '667')]
        regex2 = re.findall(r"\d{4}\d{4}\d{4}\d{4}",
                            get_source)  # ['4201996000195279']
        # if regex2 is already in regex1, delete regex2, because regex1 is
        # more accurate
        try:
            for i in range(len(regex2)):
                if regex2[i] in regex1[i]:
                    regex2.remove(regex2[i])
        except:
            pass

        try:

            for match in regex1:
                cc_info = "|".join(match)
                # add cc list
                if cc_info in cc_list:
                    continue
                else:
                    cc_list.add(cc_info)
                    LOG.info(f"Credit Card Info: {cc_info} from {url}")

            for match in regex2:
                cc_info = match
                # add cc list
                if cc_info in cc_list:
                    continue
                else:
                    cc_list.add(cc_info)
                    LOG.info(f"Credit Card Info: {cc_info} from {url}")
        except:
            pass
    except:
        pass


open_and_import_cookie(COOKIE=COOKIE)
scrape_links(back)
LOG.info(f"{str(len(links))} links found")
link_list = list(links)

for i in link_list:
    open_web_page(i)

driver.quit()
cc_list = list(cc_list)
with open("cc.txt", "w") as f:
    for i in cc_list:
        f.write(i + "\n")
LOG.info(f"{str(len(cc_list))} credit cards found")
end = time.time()
LOG.info(f"Execution time: {end - start}")
