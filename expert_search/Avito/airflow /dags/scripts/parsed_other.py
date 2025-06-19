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
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'items-items-Iy89l')))
    
    data = {}
    
    # Переходим по страницам
    for i in range(10):
        try:
            current_url = driver.current_url
            elem = driver.find_element(By.ID, 'bx_serp-item-list')
            button0 = elem.find_elements(By.CLASS_NAME, 'iva-item-sliderLink-Fvfau')

            # Находим все ссылки на элементах
           
            time.sleep(10)
            #button0 = elem.find_elements(By.TAG_NAME, 'a')
            links = []
            for button in button0:
                links.append(button.get_attribute('href'))
            links = list(set(links))
            print(len(links))
            for link in links:
                driver.get(link)
                time.sleep(10)
                # Собираем данные
                pars_data = {}
                # Парсим номер
                item_element = driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-id"]')
                pars_data.update({'num': item_element.text})
                try:
                    education = driver.find_elements(By.CLASS_NAME, 'style-serviceEducationWrapper-xvAfY')
                    for e in education:
                        pars_data.update({'education': item_element.text})
                except:
                    pars_data.update({'education': 'Не указано'})
                    pass


                # Парсим таблицу
                table = driver.find_elements(By.CLASS_NAME, 'style-item-description-pL_gy')
                for t in table:
                    pars_data.update({'description': t.text})
                try:
                    rate = driver.find_elements(By.CSS_SELECTOR,'span.style-seller-info-rating-score-C0y96')
                    for r in rate:
                        pars_data.update({'rate': r.text})

                    sum_review = driver.find_elements(By.CSS_SELECTOR, 'a[data-marker="rating-caption/rating"]')
                    for sum_r in sum_review:
                        pars_data.update({'sum_review': sum_r.text})    
                except:
                    pars_data.update({'rate': 'Оценок нет'})
                    pars_data.update({'sum_revie': 'Оценок нет'})
                    pass

                try:
                    xpath = '//*[@id="app"]/div/div[3]/div[1]/div/div[2]/div[3]/div/div[2]/div[1]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[1]/div/div[2]/a'
                    button_review = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-marker="rating-caption/rating"]')))
                    button_review.click()
                    time.sleep(10)
                    elements = driver.find_elements(By.CSS_SELECTOR, 'p[data-marker^="review("]')
                    texts = [el.text.strip() for el in elements]
                    pars_data.update({'review': texts})
                    #rating_review = driver.find_element(By.XPATH, '/html/body/div[2]/div[11]/div/div[2]/div/div/div/div/div/div[1]/div[2]/div/div')
                    #for r in rating_review:
                            #pars_data.update({'rating': r.text})
                except:
                    pars_data.update({'review': 'Нет отзывов'}) 
                    pass
            
                current_index = (button0.index(button)) + i*50
                data[current_index] = pars_data
                time.sleep(5)
    

            # Закрываем окно и возвращаемся к основному
            driver.get(current_url)
            
       

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