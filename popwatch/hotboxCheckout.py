# Checkout Class for Hot Topic and Box Lunch
import re
import time
import json
import hashlib
import logging
import requests
import portalocker
import distro
import os

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
        EC.element_to_be_clickable((By.XPATH, '//*[@id="checkout-form"]/fieldset/div/button')))
        checkoutBtn.click()
        # Start as an Unregistered User
        checkoutBtnAsGuest = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="primary"]/div[2]/div[1]/form/fieldset/div/button/span')))
        checkoutBtnAsGuest.click()
        # Fill Out Form for Guest Checkout
        # USER FORM AUTOMATION #
        email_form = self.driver.find_element_by_id("dwfrm_singleshipping_email_emailAddress")
        email_form.send_keys(profile.email)
        first_name_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_firstName")
        first_name_form.send_keys(profile.f_name)
        last_name_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_lastName")
        last_name_form.send_keys(profile.l_name)
        country_selection =  WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress_addressFields_country"]/option[2]')))
        country_selection.click()
        zip_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_postal")
        zip_form.send_keys(profile.zipCode)
        ad_one_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_address1")
        ad_one_form.send_keys(profile.ad_one)
        ad_two_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_address2")
        ad_two_form.send_keys(profile.ad_two)
        city_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_city")
        city_form.send_keys(profile.city)
        state_selection =  WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress_addressFields_states_state"]/option[5]')))
        state_selection.click()
        phone_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_phone")
        phone_form.send_keys(profile.phone)
        # Continue to Billing Button
        continueBillingBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress"]/div[2]/fieldset/div/button')))
        continueBillingBtn.click()
        # Enter Credit Card Information
        # Credit Card Owner
        creditCardOwner = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_owner")
        creditCardOwner.send_keys(profile.ccOwner)
        # Credit Card Number
        creditCardNum = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_number")
        creditCardNum.send_keys(profile.ccNumber)
        # Credit Card Expiration Date
        creditCardExp = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_userexp")
        creditCardExp.send_keys(profile.expDate)
        # Credit Card Security Code
        creditCardCCV = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_cvn")
        creditCardCCV.send_keys(profile.ccSecurityCode)
        # Billing Review Button
        reviewBillingBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_billing"]/div[3]/button')))
        reviewBillingBtn.click()
        # Place Order Button
        if os.environ['POPENV'] == "dev":
            self.UPDATER.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text="Funko Bot in Test Mode. Checkout Not Proceeding")
        elif os.environ['POPENV'] == "prd":
            placeOrderBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="summarySubmit"]')))
            placeOrderBtn.click()
