from bs4 import BeautifulSoup
import re
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os

# Шлях до BrowserMob Proxy
bmp_path = "browsermob-proxy-2.1.4/bin/browsermob-proxy.bat"

# Створюємо сервер BrowserMob Proxy
server = Server(bmp_path)
server.start()

# Створюємо новий проксі-сервер
proxy = server.create_proxy()

# Шлях до chromedriver
chromedriver_path = 'bin/chromedriver.exe'

# Налаштування для Chrome з проксі-сервером
options = Options()
options.headless = False
options.add_argument("--proxy-server={0}".format(proxy.proxy))

# Встановлюємо проксі
capabilities = webdriver.DesiredCapabilities.CHROME

service = ChromeService(executable_path=chromedriver_path)


def read_links_from_csv(file_path):
    links = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            if len(row) > 1:  # Ensure there is a link in the row
                links.append((row[0], row[1]))  # Append the title and link as a tuple to the list
    return links


def write_links_to_csv(file_path, links):
    existing_links = []
    # Читаємо вміст CSV файлу
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if len(row) > 1:  # Ensure there is a link in the row
                    existing_links.append(row[3])  # Append the processed link to the list

    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        for link in links:
            processed_link = link[1].replace('/output.mpd', '')
            # Перевіряємо, чи вже існує посилання
            if processed_link not in existing_links:
                writer.writerow([link[0], license_url, link[1], processed_link])


links = read_links_from_csv('links.csv')
license_url = "https://wdvn.blutv.com/"
for title, link in links:
    # Ініціалізуємо браузер Chrome
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(link)

    # Чекаємо, поки сторінка завантажиться
    time.sleep(10)
    driver.refresh()

    # Знаходимо і натискаємо кнопку "Увійти"
    login_button = driver.find_element(By.XPATH, '//div[text()="Üye Girişi"]')
    login_button.click()

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//form[@data-testid="form-login"]')))

    username_input = driver.find_element(By.XPATH, '//input[@data-testid="input-username-login"]')
    password_input = driver.find_element(By.XPATH, '//input[@data-testid="input-password-login"]')
    username_input.send_keys('creatives-europu@talentmail.world')
    password_input.send_keys('$>b7@jYhZnB/Pt?')

    # Знаходимо і натискаємо кнопку входу
    submit_button = driver.find_element(By.XPATH, '//button[@data-testid="button-login"]')
    submit_button.click()
    time.sleep(20)

    profile_button = driver.find_element(By.XPATH, '//div[@data-testid="profile-avatar-665dae284c62c7dbb4cc150c"]')
    profile_button.click()
    time.sleep(10)

    # Починаємо перехоплення запитів
    proxy.new_har("request", options={'captureHeaders': True, 'captureContent': True})

    driver.get(link)
    time.sleep(10)

    # Отримуємо перехоплені запити
    result = proxy.har

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Знаходимо всі скрипти на сторінці
    scripts = soup.find_all('script')

    subtitle_pattern = re.compile(r'"label":"([^"]+)".*?"src":"(https://blutv-subtitle\.mncdn\.com/[^\s,]*\.vtt)"')
    subtitles = []

    for script in scripts:
        matches = re.findall(subtitle_pattern, script.text)
        if matches:
            subtitles.extend(matches)

    if subtitles:
        # Створюємо папку з назвою фільму в директорії files, якщо вона ще не існує
        os.makedirs(os.path.join('files', title), exist_ok=True)
        # Відкриваємо файл у цій папці для запису посилань
        with open(os.path.join('files', title, 'subs.txt'), 'w') as file:
            for label, link in subtitles:
                file.write(f"{label}: {link}\n")
                print(f'Written link: {label}: {link}')  # Додаємо друк знайдених посилань

    for entry in result['log']['entries']:
        url = entry['request']['url']
        method = entry['request']['method']

    # Список ключових слів для фільтрації
    keywords = ['gcp.blutv.com', 'output.mpd', 'outputs', 'dash-0']
    excluded_keywords = ['infinity-c15', 'youboranqs01']


    def filter_urls(entry):
        url = entry['request']['url']
        method = entry['request']['method']
        if method == "GET":
            # Перевіряємо, чи містить URL будь-яке ключове слово
            contains_all_keywords = all(keyword in url for keyword in keywords)
            # Перевіряємо, чи URL не містить жодного виключеного ключового слова
            contains_no_excluded_keywords = not any(keyword in url for keyword in excluded_keywords)
            return contains_all_keywords and contains_no_excluded_keywords
        return False


    # Фільтруємо записи за допомогою функції filter_urls
    filtered_entries = filter(filter_urls, result['log']['entries'])

    links_to_write = []
    for entry in filtered_entries:
        print(entry['request']['url'])
        links_to_write.append(entry['request']['url'])

    # Записуємо отримані посилання в list.csv
    write_links_to_csv('list.csv', [(title, url) for url in links_to_write])

    driver.quit()

server.stop()
