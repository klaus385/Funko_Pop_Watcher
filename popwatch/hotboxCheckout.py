# Checkout Class for Hot Topic and Box Lunch
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

class hotBox(object):

     def __init__(self, UPDATER):
        self.TIMEOUT = {}
        self.UPDATER = UPDATER
        self.THREAD_ALIVE = False
        self.driver = self.init_driver()

    def ht_bl_checkout_process(self):
        # Checkout Button then as unregistrated user
        checkoutBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="checkout-form"]/fieldset/div/button'))).click();
        # Start as an Unregistered User
        checkoutBtnAsGuest = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="primary"]/div[2]/div[1]/form/fieldset/div/button/span'))).click();
        # Fill Out Form for Guest Checkout
        # USER FORM AUTOMATION #
        email_form = self.driver.find_element_by_id("dwfrm_singleshipping_email_emailAddress")
        email_form.send_keys(email)
        first_name_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_firstName")
        first_name_form.send_keys(f_name)
        last_name_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_lastName")
        last_name_form.send_keys(l_name)
        country_selection =  WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress_addressFields_country"]/option[2]'))).click();
        zip_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_postal")
        zip_form.send_keys(zipCode)
        ad_one_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_address1")
        ad_one_form.send_keys(ad_one)
        ad_two_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_address2")
        ad_two_form.send_keys(ad_two)
        city_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_city")
        city_form.send_keys(city)
        country_selection =  WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress_addressFields_states_state"]/option[5]'))).click();
        phone_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_phone")
        phone_form.send_keys(phone)
        # Continue to Billing Button
        continueBillingBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress"]/div[2]/fieldset/div/button'))).click();
        # Enter Credit Card Information
        # Credit Card Owner
        creditCardOwner = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_owner")
        creditCardOwner.send_keys(ccOwner)
        # Credit Card Number
        creditCardNum = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_number")
        creditCardNum.send_keys(ccNumber)
        # Credit Card Expiration Date
        creditCardExp = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_userexp")
        creditCardExp.send_keys(expDate)
        # Credit Card Security Code
        creditCardCCV = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_cvn")
        creditCardCCV.send_keys(ccSecurityCode)
        # Billing Review Button
        reviewBillingBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_billing"]/div[3]/button'))).click();
        # Place Order Button
        placeOrderBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="summarySubmit"]'))).click();
