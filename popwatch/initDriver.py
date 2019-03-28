# Class to Maintain the Chrome Driver
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

# Function to Determine Distro
def get_distro():
    # Checking Distrobution before passing in connection string
    distrobution = distro.linux_distribution()
    distroName = itemgetter(0)(distrobution)
    return distroName


class InitChromeDriver(object):
    # Function to Define Chrome Driver in Single Place
    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--credentials_enable_service=false")
        chrome_options.add_argument("--profile.password_manager_enabled=false")
        chrome_options.add_argument("--no-sandbox")

        if get_distro() == "Raspbian GNU/Linux":
            driver = webdriver.Chrome(executable_path=config.DRIVER_LOCATION, chrome_options=chrome_options)
            driver.wait = WebDriverWait(driver, 3)
            _LOG.info('Initialized Chrome Driver.')
            return driver
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
            driver.wait = WebDriverWait(driver, 3)
            _LOG.info('Initialized Chrome Driver.')
            return driver
