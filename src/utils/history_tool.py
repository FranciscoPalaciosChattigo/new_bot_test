import time

import discord
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class HistoryTool:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Ejecutar en modo headless
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(3)

    def build_url_and_porcent(self, directories, env, date):
        # Encontrar el elemento <text> con la clase 'chart__caption'
        url_list = []
        for directory in directories:
            try:
                url = 'https://storage.googleapis.com/' + directory + '/allure-report/index.html'
                url_resumen = url.replace('gs://qa-allure-report-storage-automation/', '')

                self.driver.get(url)
                # Esperar un poco para que la página se cargue completamente
                time.sleep(1)

                element = self.driver.find_element(By.CSS_SELECTOR, 'text.chart__caption')
                porcentaje = element.text.strip()
                print('porcentaje ::>> ', porcentaje)

                # embed.description = "[Haz clic aquí](https://example.com) para visitar nuestro sitio web."
                url_list.append(f"☁ {porcentaje}% [{url_resumen}]\n")
                # Cerrar el navegador
                self.driver.quit()
            except Exception as e:
                print(f"No se encontró el elemento: {e}")

        embed = discord.Embed(title=f"Hola!, Estas son las autos de {env} el {date}",
                              description="🦸‍♂️ Super:\n"
                                        f"{[url_i for url_i in url_list if 'supervisor' in url_i]}"
                                        "👮🏽 Agente:\n"
                                        f"{[url_i for url_i in url_list if 'agente' in url_i]}"
                                        "🤖 Bot:\n"
                                        f"{[url_i for url_i in url_list if 'bot' in url_i]}",
                              colour=discord.Colour.green(),
                              type='article')
        return embed


