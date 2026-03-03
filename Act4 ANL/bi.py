import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

user = "standard_user"
password = "secret_sauce"

def main():
    # setup webdriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1920,1080")
    #options.add_argument("--headless")  # descomentar si no quieres ver el navegador
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # ir a la página de login e iniciar sesión
    driver.get("https://www.saucedemo.com/")
    time.sleep(2) 
    driver.find_element("id", "user-name").send_keys(user)
    driver.find_element("id", "password").send_keys(password)
    driver.find_element("id", "login-button").click()
    time.sleep(2) 
    
    # después de login estamos en el inventario, capturamos el HTML y hacemos scraping
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    items = soup.find_all('div', class_='inventory_item')
    print(f"Items encontrados: {len(items)}")
    
    nombres = []
    precios = []
    descripciones = []
    for item in items:
        nombre_elem = item.find('div', class_='inventory_item_name')
        precio_elem = item.find('div', class_='inventory_item_price')
        desc_elem = item.find('div', class_='inventory_item_desc')
        
        nombres.append(nombre_elem.text.strip() if nombre_elem else "N/A")
        precios.append(precio_elem.text.strip() if precio_elem else "N/A")
        descripciones.append(desc_elem.text.strip() if desc_elem else "N/A")
    
    df = pd.DataFrame({
        "Nombre": nombres, 
        "Precio": precios, 
        "Descripción": descripciones
    })
    print(df)
    
    # conservar el comportamiento de compra que ya tenías
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
