import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time


def main():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1920,1080")
    #options.add_argument("--headless")  # descomentar si no quieres ver el navegador
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.mercadolibre.com.mx/ofertas/novedades-de-temporada")
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    items = soup.find_all('div', class_="andes-card poly-card poly-card--grid-card poly-card--xlarge andes-card--flat andes-card--padding-0 andes-card--animated")
    print(f"Items encontrados: {len(items)}")
    
    titulos = []
    precios = []

    for item in items:
        ti  = item.find('h3', class_='poly-component__title-wrapper')           
        pre = item.find('span', class_='andes-money-amount__fraction')  

        titulos.append(ti.text.strip() if ti else "N/A")
        precios.append(pre.text.strip() if pre else "N/A")

    df = pd.DataFrame({
        "Nombre": titulos,
        "Precio": precios,
    })
    print(df)

    driver.quit()

    df.to_csv('Mercado Libre.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    main()