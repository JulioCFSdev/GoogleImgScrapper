import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Função para baixar imagens e criar log
def download_image(url, file_path, log_file):
    try:
        img_data = requests.get(url).content
        with open(file_path, 'wb') as img_file:
            img_file.write(img_data)
        # Log da imagem baixada
        log_msg = f"Imagem baixada: {file_path} - URL: {url}\n"
        print(log_msg)
        with open(log_file, 'a') as log:
            log.write(log_msg)
    except Exception as e:
        error_msg = f"Erro ao baixar {url}: {e}\n"
        print(error_msg)
        with open(log_file, 'a') as log:
            log.write(error_msg)

# Configuração do Selenium sem modo headless
def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Removido para abrir a janela do navegador
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Função principal
def scrape_google_images(search_query, num_images=500):
    driver = setup_driver()
    driver.get('https://images.google.com')

    # Buscar a consulta
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    # Esperar que as imagens com a classe 'YQ4gaf' sejam carregadas
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.YQ4gaf")))

    # Scroll na página para carregar mais imagens
    image_urls = set()
    log_file = 'download_log.txt'
    if os.path.exists(log_file):
        os.remove(log_file)  # Remove o log anterior, se existir
    
    while len(image_urls) < num_images:
        # Scroll para o final da página para carregar mais imagens
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Aguarda o carregamento das imagens

        # Coleta os elementos img com a classe 'YQ4gaf'
        images = driver.find_elements(By.CSS_SELECTOR, "img.YQ4gaf")
        print(f"Imagens encontradas: {len(images)}")

        for img in images:
            try:
                src = img.get_attribute('src') or img.get_attribute('data-src')
                if src and 'http' in src:
                    image_urls.add(src)
                    print(f"Imagem coletada: {src}")
                if len(image_urls) >= num_images:
                    break
            except Exception as e:
                print(f"Erro ao coletar imagem: {e}")

        # Continuar rolando a página até obter o número necessário de imagens
        if len(image_urls) < num_images:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    print(f"Coletado {len(image_urls)} URLs de imagens.")

    # Cria diretório para salvar imagens
    if not os.path.exists('downloaded_images/femur/normal/'):
        os.makedirs('downloaded_images/femur/normal/')

    # Baixa as imagens e escreve o log
    for i, url in enumerate(image_urls):
        file_path = f'downloaded_images/femur/normal/img_{i+1}.jpg'
        download_image(url, file_path, log_file)

    driver.quit()

if __name__ == "__main__":
    scrape_google_images("femur x ray normal", 200)
