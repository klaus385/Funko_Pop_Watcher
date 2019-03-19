import re
import time
import json
import hashlib
import logging
import requests
import portalocker
import distro

from popwatch import config
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from operator import itemgetter

_LOG = logging.getLogger(__name__)

HTML_OBJ = {
    "hottopic": "presale-pdp",
    "boxlunch": "presale-pdp",
    "walmart": "spin-button-children",
    "barnesandnoble": "btn-addtocart",
    "gamestop": "addOnSalesModalEligible",
    "blizzard": "product-addtocart-button",
    "geminicollectibles": "add-to-cart",
    "target": "h-text-orangeDark"}

def get_distro():
    # Checking Distrobution before passing in connection string
    distrobution = distro.linux_distribution()
    distroName = itemgetter(0)(distrobution)
    return distroName

class storeStock(object):

    def cart_links(self, site):
        if site in ['hottopic', 'boxlunch']:
            if site in ['hottopic']:
                cartLink = "https://www.hottopic.com/cart"
                return cartLink
            elif site in ['boxlunch']:
                cartLink = "https://www.boxlunch.com/cart"
                return cartLink
        else:
            print("Not Hottopic or BoxLunch")
            print("Implement other sites later time")

    def __init__(self, UPDATER):
        self.TIMEOUT = {}
        self.UPDATER = UPDATER
        self.THREAD_ALIVE = False
        self.driver = self.init_driver()

    def init_driver(self):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--credentials_enable_service=false")
        chrome_options.add_argument("--profile.password_manager_enabled=false")

        if get_distro() == "Raspbian GNU/Linux":
            driver = webdriver.Chrome(executable_path=config.DRIVER_LOCATION, chrome_options=chrome_options)
            driver.wait = WebDriverWait(driver, 3)
            _LOG.info('Initialized chrome driver.')
            return driver
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
            driver.wait = WebDriverWait(driver, 3)
            _LOG.info('Initialized chrome driver.')
            return driver

    def check_funko(self, site, url):
        status = False

        _LOG.info('Checking: {0}'.format(site + " " + url))

        if site in ['hottopic', 'boxlunch']:
            status = self.in_stock(site, url)
        elif site in ['walmart', 'barnesandnoble', 'gamestop', 'blizzard', 'geminicollectibles']:
            status = self.add_to_cart(site, url)
        elif site in ['target']:
            status = self.out_of_stock(site, url)

        # Report from Bot When in Stock
        if status:
            msg = site + " - In Stock: " + ":\n" + url
            self.UPDATER.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID,
                                          text=msg)

            url_md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
            # When set prevents lookup until TIMEOUT Expires
            self.TIMEOUT[url_md5] = datetime.today().date()
            _LOG.info('Timeout Set: {0}'.format(url_md5))
            atcBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(string(), "Add to Bag")]'))).click();

    def set_cookies(self):
        self.driver.get('https://www.hottopic.com')
        self.driver.get('https://www.boxlunch.com')

    def pop_search(self, sleep_interval=2):
        self.set_cookies()

        while True:
            # Load in items from pops.json
            if self.THREAD_ALIVE:
                with portalocker.Lock(config.FUNKO_POP_LIST, "r", timeout=10) as data_file:
                    funkopop_links = json.load(data_file)

                for funko in funkopop_links:
                    url_md5 = hashlib.md5(funko['url'].encode('utf-8')).hexdigest()
                    try:
                        if url_md5 not in self.TIMEOUT:
                            self.check_funko(funko['store'], funko['url'])
                        elif url_md5 in self.TIMEOUT and self.TIMEOUT[url_md5] < datetime.today().date():
                            if datetime.now().hour > 7:
                                self.check_funko(funko['store'], funko['url'])
                    except Exception as excp:
                        _LOG.error('Exception {0}'.format(excp))
                        import traceback
                        traceback.print_exc()

            time.sleep(sleep_interval)

    def in_stock(self, site, url):
        self.driver.get(url)

        try:
            inStock = self.driver.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, HTML_OBJ[site])))
        except TimeoutException:
            _LOG.error('Failed to locate element for "In Stock".')
            return False

        if inStock and inStock.text.lower() == "in stock":
            return True

        return False

    def out_of_stock(self, site, url):
        self.driver.get(url)

        try:
            outOfStock = self.driver.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, HTML_OBJ[site])))
        except TimeoutException:
            _LOG.error('Failed to locate element for "Out of Stock".')
            return False

        if outOfStock and "out of stock" in outOfStock.text.lower():
            return False

        return True

    def add_to_cart(self, site, url):
        response = False
        self.driver.get(url)

        try:
            if site == 'blizzard':
                addToCart = self.driver.wait.until(
                    EC.presence_of_element_located((By.ID, HTML_OBJ[site])))
            else:
                addToCart = self.driver.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, HTML_OBJ[site])))
        except TimeoutException:
            _LOG.warning('Failed to locate element for "Add to Cart".')
            return False

        if addToCart and addToCart.text.lower() == "add to cart":
            response = True
        elif addToCart and addToCart.get_attribute('value') in ["ADD TO CART", "Add To Cart"]:
            response = True

        return response
