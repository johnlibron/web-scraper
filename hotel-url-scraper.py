import json
import time
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver

browser = webdriver.Chrome()
browser.maximize_window()

urls = []

try:
    browser.execute_script("window.open('https://www.tripadvisor.com.ph/Hotels-g294261-Cebu_Island_Visayas-Hotels.html', '_parent')")
    time.sleep(10)

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    try:
        check_last_page = '.pageNumbers .pageNum:last-child'
        page_list = range(int(soup.select(check_last_page)[0].text))
    except:
        page_list = range(1)

    for current_page in page_list:
        current_page += 1

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        business_blocks = soup.find_all('div', {"class": "prw_rup prw_meta_hsx_responsive_listing ui_section listItem"})

        for business_block in business_blocks:
            url = "https://www.tripadvisor.com.ph" + business_block.find('div', {"class": "meta_listing ui_columns large_thumbnail_mobile"}).get('data-url')
            if url not in urls:
                urls.append(url)
        
        if current_page < len(page_list):
            browser.execute_script("document.getElementsByClassName('nav next ui_button primary')[0].click()")

        time.sleep(10)

except Exception as e:
    print(traceback.format_exc())
finally:
    browser.quit()

    with open('data/urls.json', 'w', encoding='utf-8') as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)