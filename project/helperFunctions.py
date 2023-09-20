import time
from selenium.common import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import platform

# CHROME
def driver_init():
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')

    if platform.system() == "Linux":
            driver = webdriver.Chrome(service=Service(executable_path=r'/usr/bin/chromedriver'), options=options)
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="114.0.5735.90").install()), options=options)
    driver.implicitly_wait(5)
    return driver

# SIGN IN
def sign_in_wave(driver):
    # get password from local file
    with open('password.txt', 'r') as f:
        password = f.readline()

    try:
        driver.get("https://panel.wave.com.pl/?co=logowanie&redirect=%2F") # login page url
    except WebDriverException:
        print("Page down")
        exit()
    elem = driver.find_element(By.NAME, "pass")
    elem.clear()
    elem.send_keys(password + Keys.RETURN) # password 
    return driver

# FETCH DATA FROM PANEL WAVE
def fetch_wave(driver, node):
    try:
        driver.get(f"https://panel.wave.com.pl/?co=alias&alias={node}&uri=/?co=dziennik") # search feature url
    except WebDriverException:
        print("Page down")

    # find elements
    table = driver.find_element(By.CLASS_NAME, 'dosrodka')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')

    # scrape selected data
    data = list()
    for row in rows:
        tds = row.find_elements(By.TAG_NAME, 'td')
        if len(tds) > 2:
            data.append(tds[10].text)

    # FILTER DATA
    channels = [x.split(' ')[1] for x in data if x not in ('-', 'Freq')]

    # CLASSIFY DATA
    occupiedFrequencies = set()
    for channel in channels:
        start, end = channel.split('-')
        freqList = [f for f in range(int(start), int(end)+1)]
        for f in freqList:
            occupiedFrequencies.add(f)

    occupiedFrequencies = list(occupiedFrequencies)
    occupiedFrequencies.sort()

    freq5G = [f for f in occupiedFrequencies if (f > 4700 and f < 6500)]
    channels = [c for c in channels if int(c.split('-')[0]) > 4700]
    
    return driver, freq5G, channels

if __name__ == "__main__":
    driver = driver_init()
    print(driver)
    driver = sign_in_wave(driver)
    print(driver)
    driver.quit()