from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

class MakeImage():
    def __init__(self):
        self.url = "https://www.ptsearch.info/compute/create/t2i/"
        self.model_hash_name_list = ['PTsearch v30 2.3D', 'PTsearch v35 Style 2D', 'PTsearch v30 3D','PTsearch v30 3D', 'CamelliaMix v3', 'Counterfeit v30 2D', 'DarkSushiMix 2D', 'Animelike 2D', 'HenmixReal v10 2.9D', 'HazyAbyss 2D', 'Camelliamix v20 2.3D', 'MIX-Pro V3.5 Lignes 2D', 'AOM A3 2.2D', 'RandomMix 2D', 'ChilloutMix 3D', 'AOM2 : 2.2D', 'AbyssBasil : 2.5D', 'AbyssBasil2 : 2.8D', 'Anything v3 : 2D', 'PastelMix : 2D']
        self.username = "test_baro"
        self.password = "test1004"
    
    def login(self,driver):
        # 로그인
        login_id = driver.find_element(By.NAME, "username")
        login_password = driver.find_element(By.NAME, "password")
        login_id.send_keys(self.username)
        login_password.send_keys(self.password)
        submit_button = driver.find_element(By.XPATH, "//input[@value='Submit']")
        submit_button.submit()

    def prompt_make(self,prompt_text,negative_text):
        driver = webdriver.Safari()  # 웹 드라이버를 설치하고 경로를 지정해야 합니다.
        driver.get(self.url)

        self.login(driver)
        #wait = WebDriverWait(driver,30)

        for model_hash_value in self.model_hash_name_list:
            time.sleep(5)
            url = "https://www.ptsearch.info/compute/create/t2i/"
            driver.get(url)
            # 폼 작성 및 제출
            prompt_input = driver.find_element(By.NAME, "prompts")
            prompt_input.send_keys(prompt_text)

            negative_input = driver.find_element(By.NAME, "negative_prompts")
            negative_input.send_keys(negative_text)

            model_hash_select = Select(driver.find_element(By.NAME, "model_hash"))
            model_hash_select.select_by_visible_text(model_hash_value)

            submit_button = driver.find_element(By.XPATH, "//input[@value='Compute']")
            submit_button.submit()

            # 결과 기다림 (예: 20초)
            time.sleep(20)
        
        driver.quit()
    
    def crawlling(self):
        driver = webdriver.Safari()  # 웹 드라이버를 설치하고 경로를 지정해야 합니다.
        driver.get(self.url)

        self.login(self,driver)
        #wait = WebDriverWait(driver,30)

        time.sleep(5)
        url = "https://www.ptsearch.info/compute/articles/t2i/?page=1"
        driver.get(url)
        
        html=driver.page_source
        soup=BeautifulSoup(html,'html.parser')
        main=soup.find('main')
        imgs=main.find_all("img")
        for img in imgs:
            if "src" in str(img):
                url=img.get("src")
                print(url)

        # 결과 기다림 (예: 20초)
        time.sleep(20)
        
        driver.quit()