from selenium import webdriver as wd
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
from selenium.webdriver.common.action_chains import ActionChains
import random
import requests

def save_data(data, filename):
    """Сохраняет данные в JSON-файл."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Данные сохранены в файл {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении данных в файл: {e}")
        
def data_pars(url): #ссылка на авито-резюме
    driver = wd.Chrome()
    driver.get(url)
    
    # Ожидаем загрузки элементов на странице
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'items-items-zOkHg')))
    
    data = {}
    
    # Переходим по страницам
    for i in range(6):
        try:
            current_url = driver.current_url
            elem = driver.find_element(By.ID, 'bx_serp-item-list')
            button0 = elem.find_elements(By.CLASS_NAME, 'iva-item-sliderLink-kra4e')

            # Находим все ссылки на элементах
           
            time.sleep(10)
            #button0 = elem.find_elements(By.TAG_NAME, 'a')
            links = []
            for button in button0:
                links.append(button.get_attribute('href'))
            for button in button0:
                driver.execute_script("arguments[0].scrollIntoView();", button)
                button.click()

                windows = driver.window_handles  # получаем список окон

                for scr in windows[1:]: 
                    driver.switch_to.window(scr)# переключаемся на все новые окна
                   
                    # Ждем, пока загрузится необходимый элемент на странице
                        #WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div[1]/div/div[2]/div[3]/div/div[1]/div[2]/div[5]/div/article/p/span[1]')))
                    time.sleep(10)
                    # Собираем данные
                    pars_data = {}

                    # Парсим номер
                    elements = driver.find_elements(By.XPATH, '//*[@id="app"]/div/div[3]/div[1]/div/div[2]/div[3]/div/div[1]/div[2]/div[5]/div/article/p/span[1]')
                    for e in elements:
                        pars_data.update({'num': e.text})

                    # Парсим таблицу
                    table = driver.find_elements(By.TAG_NAME, 'tbody')
                    for t in table:
                        pars_data.update({'table': t.text})

                    # Парсим основной список
                    basic = driver.find_elements(By.TAG_NAME, 'ul')
                    for b in basic:
                        pars_data.update({'basic': b.text})

                    # Парсим описание
                    description_class = driver.find_element(By.CLASS_NAME,"style-item-description-pL_gy")
                    description = description_class.find_elements(By.TAG_NAME, 'p')
                    for d in description:
                        pars_data.update({'description': d.text})
                    curren_index = (button0.index(button)//2) + i*50
                    data[curren_index] = pars_data

                    # Закрываем окно и возвращаемся к основному
                    driver.close()
                    driver.switch_to.window(windows[0])


            # Переход на следующую страницу
            try:
                next_button = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-marker="pagination-button/nextPage"]')))
                next_page_url = next_button.get_attribute('href')
                # Переходим на следующую страницу
                driver.get(next_page_url)

            except Exception as e:
                print("Ошибка при переходе на следующую страницу:", e)
                break
        except Exception as e:
            print(f"Ошибка на странице {i + 1}: {e}")
            # Сохраняем данные в случае ошибки
            save_data(data, f'{i}_page_.json')
            driver.get(current_url)
            continue

    driver.quit()  # Закрываем браузер
    return data
