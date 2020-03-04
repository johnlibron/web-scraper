import json
import time
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver

browser = webdriver.Chrome()
browser.maximize_window()

urls = []

try:
    browser.execute_script("window.open('https://www.tripadvisor.com.ph/Restaurants-g294261-Cebu_Island_Visayas.html', '_parent')")
    time.sleep(10)

    browser.execute_script("document.getElementsByClassName('restaurants-filter-results-header-FilterResultsHeader__clearFiltersText--3_R93 restaurants-filter-results-header-FilterResultsHeader__cx_brand_refresh_phase2--3xgDY')[0].click()")
    time.sleep(5)

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    try:
        check_last_page = '.pageNumbers .pageNum:last-child'
        page_list = range(int(soup.select(check_last_page)[0].text))
    except:
        page_list = range(1)

    for current_page in page_list:
        current_page += 1

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        business_blocks = soup.find_all('div', {"class": "_1llCuDZj"})

        for business_block in business_blocks:
            url = "https://www.tripadvisor.com.ph" + business_block.find('a', {"class": "_15_ydu6b"}).get('href')
            if url not in urls:
                urls.append(url)
        
        if current_page < len(page_list):
            browser.execute_script("document.getElementsByClassName('nav next rndBtn ui_button primary taLnk')[0].click()")

        time.sleep(10)

except Exception as e:
    print(traceback.format_exc())
finally:
    browser.quit()

    with open('data/urls.json', 'w', encoding='utf-8') as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)