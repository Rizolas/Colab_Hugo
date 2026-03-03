#python -m venv venv
#Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
#.\venv\Scripts\activate
#pip install selenium 
#pip install webdriver-manager

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

user = "standard_user"
password = "secret_sauce"

def main():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1920,1080")
    
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get("https://www.saucedemo.com/")
    time.sleep(2) 
    
    driver.find_element("id", "user-name").send_keys(user)
    driver.find_element("id", "password").send_keys(password)
    driver.find_element("id", "login-button").click()
    time.sleep(2) 
    
    driver.find_element("name", "add-to-cart-sauce-labs-backpack").click()
    driver.find_element("name", "add-to-cart-sauce-labs-bike-light").click()
    time.sleep(2) 
    
    driver.find_element("xpath", "/html/body/div/div/div/div[1]/div[1]/div[3]/a").click()
    time.sleep(2) 
    
    driver.find_element("id", "checkout").click()
    time.sleep(2) 
    
    driver.find_element("id", "first-name").send_keys("test")
    driver.find_element("id", "last-name").send_keys("test")
    driver.find_element("id", "postal-code").send_keys("12345")
    driver.find_element("id", "continue").click()
    time.sleep(2) 
    
    driver.find_element("id", "finish").click()
    time.sleep(4) 
    
    driver.quit()

if __name__ == "__main__":
    main()