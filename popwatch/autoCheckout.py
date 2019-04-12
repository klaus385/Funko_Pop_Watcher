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
from popwatch import popProfiles
from popwatch.storeStock import storeStock
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

# Get Profile From Json Config
def profileInit():
    with portalocker.Lock(config.USER_INFO, "r", timeout=10) as data_file:
        userProfileVars = json.load(data_file)
        city = userProfileVars.get('city')
        ccNumber = userProfileVars.get('ccNumber')
        f_name = userProfileVars.get('f_name')
        l_name = userProfileVars.get('l_name')
        zipCode = userProfileVars.get('zipCode')
        mm = userProfileVars.get('mm')
        yy = userProfileVars.get('yy')
        phone = userProfileVars.get('phone')
        ad_one = userProfileVars.get('ad_one')
        ad_two = userProfileVars.get('ad_two')
        ccSecurityCode = userProfileVars.get('ccSecurityCode')
        email = userProfileVars.get('email')
        ccOwner = f_name + " " + l_name
        expDate = mm + '/' + yy

    return popProfiles.Profile(city, ccNumber, f_name, l_name, zipCode, phone, ad_one, ad_two, ccSecurityCode, email, ccOwner, expDate)

# Instantiating Pop Profile
profile = profileInit()


def startDriver(stkObj):
    stkObj.init

# The Class that handles all the Selenium Logic for
# Auto checking out an Item

class AutoCheckout(object):
    def __init__(self, UPDATER):
        self.UPDATER = UPDATER
        self.driver = stkObj.ini
    
    def ht_bl_checkout_process(self):
        self.driver.refresh()
        # TODO: Add Quantity Input for the Check Funko Function
        # A. This will also dictate the original message sent to channel
        # B. This will dictate number to buy
        # NOTE: May want to run multiple instances and buy in singles.
        # Select Quantity
        quantity = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="Quantity"]/option[1]')))
        quantity.click()
        # Add to Cart Button
        atcBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(string(), "Add to Bag")]')))
        atcBtn.click()
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
        first_name_form = self.driver.find_element_by_id(
            "dwfrm_singleshipping_shippingAddress_addressFields_firstName")
        first_name_form.send_keys(profile.f_name)
        last_name_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_lastName")
        last_name_form.send_keys(profile.l_name)
        country_selection = WebDriverWait(self.driver, 20).until(
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
        state_selection = WebDriverWait(self.driver, 20).until(
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

    def hbo_checkout_process(self):
        # # Check if Pop Overlay Exists
        # # popup = self.driver.find_elements_by_xpath(
                #     '//*[@id="privy-inner-container"]/div[1]/div/div/div[3]/div[5]/button')

        # # Logic to Close Pop when it does exist
        # for popupCloseBtn in popup:
        #     popInnerText = popupCloseBtn.get_attribute('innerText')
        #     if popInnerText:
        #         print('Pop Found Initiating Closer of Pop Up')
        #         # Pop Up Found and Needs to be Dismissed
        #         popup.click()
        #     else:
        #         self.driver.refresh()
        # Find quantity element by name
        quantity = self.driver.find_element_by_name("quantity")
        # Reset Default Quantity Value
        self.driver.execute_script("arguments[0].value = ''", quantity)
        # Input to form number of items wanted
        quantity.send_keys("2")
        # Using Javascript to Add Item to Cart
        self.driver.execute_script("document.getElementById('AddToCart-product-template').click()")
        # Checkout Button
        hboCheckoutBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="MiniCart"]/a[1]')))
        hboCheckoutBtn.click()
        #  Enter Coupon Code
        # couponCode = self.driver.find_element_by_id("checkout_reduction_code")
        # couponCode.send_keys("WELCOME15")
        # Start Entering User Information
        hboEmailForm = self.driver.find_element_by_id("checkout_email")
        hboEmailForm.send_keys(profile.email)
        hboFName = self.driver.find_element_by_id("checkout_shipping_address_first_name")
        hboFName.send_keys(profile.f_name)
        hboLName = self.driver.find_element_by_id("checkout_shipping_address_last_name")
        hboLName.send_keys(profile.l_name)
        hboADOne = self.driver.find_element_by_id("checkout_shipping_address_address1")
        hboADOne.send_keys(profile.ad_one)
        hboADTwo = self.driver.find_element_by_id("checkout_shipping_address_address2")
        hboADTwo.send_keys(profile.ad_two)
        hboCity = self.driver.find_element_by_id("checkout_shipping_address_city")
        hboCity.send_keys(profile.city)
        hboCountrySelection = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="checkout_shipping_address_country"]/option[1]')))
        hboCountrySelection.click()
        hboStateSelection = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="checkout_shipping_address_province"]/option[5]')))
        hboStateSelection.click()
        hboZipCode = self.driver.find_element_by_id("checkout_shipping_address_zip")
        hboZipCode.send_keys(profile.zipCode)
        hboPhone = self.driver.find_element_by_id("checkout_shipping_address_phone")
        hboPhone.send_keys(profile.phone)
        # Go to Shipping Method Page
        hboShippingMethodBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/div/form/div[2]/button')))
        hboShippingMethodBtn.click()
        # Go to Payment Method Page
        hboPaymentMethodBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/div/form/div[2]/button')))
        hboPaymentMethodBtn.click()
        # Credit Card Information Form Fill Out
        # Credit Card Number
        hbocreditCardNumIframe = self.driver.switch_to.frame(
            self.driver.find_element_by_class_name("card-fields-iframe"))
        self.driver.switch_to.frame(hbocreditCardNumIframe)
        hbocreditCardNum = self.driver.find_element_by_name('number')
        hbocreditCardNum.send_keys(profile.ccNumber)
        self.driver.switch_to_default_content
        # Credit Card Owner
        # hbocreditCardOwner = self.driver.find_element_by_id("name")
        # hbocreditCardOwner.send_keys(profile.ccOwner)
        # # Credit Card Expiration Date
        # hbocreditCardExp = self.driver.find_element_by_id("expiry")
        # hbocreditCardExp.send_keys(profile.expDate)
        # # # Credit Card Security Code
        # hbocreditCardCCV = self.driver.find_element_by_id("verification_value")
        # hbocreditCardCCV.send_keys(profile.ccSecurityCode)
        # # Complete Order Button
        # hboCompleteOrderBtn = WebDriverWait(self.driver, 20).until(
        #     EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/div/div/form/div[3]/div[1]/button')))
        # hboCompleteOrderBtn.click()

    # def target_checkout_process(self):
