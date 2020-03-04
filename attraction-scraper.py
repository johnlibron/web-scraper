import json
import re
import time
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse, parse_qs
 
target_urls = []

browser = webdriver.Chrome()
browser.maximize_window()

attractions = []
reviews = []

try:
    business_index = 1

    for url in target_urls:
        browser.execute_script("window.open('" + url + "', '_parent')")
        time.sleep(5)

        browser.execute_script("document.getElementsByClassName('logo_slogan')[0].innerHTML = JSON.stringify(window.__WEB_CONTEXT__.pageManifest.redux.api.responses).toString()")

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        main_window = browser.current_window_handle

        try:
            check_last_page = '.pageNumbers .pageNum:last-child'
            page_list = range(int(soup.select(check_last_page)[0].text))
        except:
            page_list = range(1)

        ########################################################################################################################

        header_block = soup.find('div', {"class": "contentWrapper"})

        name = header_block.find('h1', {"class", "ui_header"}).text

        stars = header_block.find('span', {"class", "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
        stars = str(int(stars) / 10)

        review_count = header_block.find('span', {"class", "reviewCount"}).text.replace(' Reviews', '').replace(' Review', '')

        try:
            popularity = header_block.find('span', {"class", "header_popularity"}).text
        except:
            popularity = None

        try:
            tags = header_block.find('span', {"class", "animal_tag"}).find('span', {"class", "detail"}).text
            tags = [x.strip() for x in tags.split(',')]
        except:
            tags = []

        try:
            category_list = []
            categories = header_block.find('span', {"class", "attractionCategories"}).find_all('a')
            for category in categories:
                if category.text != 'More':
                    category_list.append(category.text)
            categories = category_list
        except:
            categories = []

        categories.extend(tags)

        ########################################################################################################################
        
        photo_block = soup.find('div', {"class": "attractions_large"})

        try:
            photo_url = photo_block.find('img', {"class", "basicImg"}).get('src')
            photo_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', photo_url)[0]
        except:
            photo_url = None

        ########################################################################################################################

        about = None
        suggested_duration = None
        hours = []

        about_block = soup.find('div', {"class": "ppr_priv_location_detail_about_card"})

        about_rows = about_block.find_all('div', {"class": "attractions-attraction-detail-about-card-AttractionDetailAboutCard__section--1_Efg"})
        about_rows = about_rows[1:]

        for about_row in about_rows:
            about_row_span = about_row.find('span')
            if about_row_span.has_attr('class'):
                if about_row_span.get('class')[1] == 'clock':
                    browser.execute_script("document.getElementsByClassName('public-location-hours-LocationHours__hoursLink--2wAQh')[0].click()")
                    soup = BeautifulSoup(browser.page_source, 'html.parser')

                    try:
                        hours_array = soup.find_all('div', {"class": "public-location-hours-AllHoursList__daysAndTimesRow--2CcRX"})
                        x = 0
                        while x < len(hours_array):
                            if x % 2 == 1:
                                hours.append(hours_array[x-1].text + " | " + hours_array[x].text)
                            x += 1
                    except:
                        hours = []
                        
                    browser.execute_script("document.getElementsByClassName('_3yn85ktl _1UnOCDRu')[0].click()")
                    soup = BeautifulSoup(browser.page_source, 'html.parser')
                elif about_row_span.get('class')[1] == 'duration':
                    suggested_duration = about_row.text.replace('Suggested Duration:', '')
            else:
                about_read_more = about_block.find('span', {"class", "attractions-attraction-detail-about-card-Description__readMore--2pd33"})

                if about_read_more:                        
                    browser.execute_script("document.getElementsByClassName('attractions-attraction-detail-about-card-Description__readMore--2pd33')[0].click()")
                    time.sleep(5)
            
                    soup = BeautifulSoup(browser.page_source, 'html.parser')

                    about = soup.find('div', {"class": "attractions-attraction-detail-about-card-Description__modalText--1oJCY"}).text

                    browser.execute_script("document.getElementsByClassName('_2EFRp_bb _3ptEwvMl')[0].click()")
                else:
                    about = about_row_span.text

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        ########################################################################################################################

        contact_block = soup.find('div', {"class": "ppr_priv_location_detail_contact_card"})

        try:
            address = contact_block.find('span', {"class": "address"}).text
        except:
            address = None

        try:
            browser.execute_script("document.getElementsByClassName('detail_section website')[0].getElementsByClassName('taLnk')[0].click()")
            time.sleep(5)
            browser.switch_to.window(browser.window_handles[1])

            website = browser.current_url

            browser.close()
            browser.switch_to.window(main_window)
        except:
            website = None

        try:
            contact_number = contact_block.find('div', {"class": "contactType phone is-hidden-mobile"}).text
        except:
            contact_number = None

        try:
            location_url = contact_block.find('img', {"class": "mapImg"}).get('src')

            parsed = urlparse(location_url)
            location = parse_qs(parsed.query)['center'][0].split(',')
            latitude = location[0]
            longitude = location[1]
        except:
            latitude = None
            longitude = None

        try:
            award = soup.find('div', {"class": "attractions-attraction-detail-about-card-Award__award--3yckF"}).text
        except:
            award = None
            
        content = soup.find('div', {"class": "logo_slogan"}).text

        try:
            email_address = re.findall('"email":"(?s)(.*)","address_obj":{', content)[0]
        except:
            email_address = None

        ########################################################################################################################
        
        popular_mentions = []

        review_filter_block = soup.find('div', {"class": "ppr_priv_location_reviews_container_resp"})

        mentions = review_filter_block.find_all('span', {"class": "ui_tagcloud"})

        for mention in mentions:
            popular_mentions.append(mention.text.strip())

        popular_mentions = popular_mentions[1:]

        attraction = {
            'business_id': business_index,
            'name': name,
            'about': about,
            'photo_url': photo_url,
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
            'stars': stars,
            'review_count': review_count,
            'is_open': 1,
            'attributes': {
                'popularity': popularity,
                'award': award,
                'suggested_duration': suggested_duration,
                'popular_mentions': popular_mentions
            },
            'categories': categories,
            'hours': hours,
            'website': website,
            'email_address': email_address,
            'contact_number': contact_number
        }

        review_index = 0
        review_list = []
            
        for current_page in page_list:
            current_page += 1
            browser.execute_script('var elements = document.getElementsByClassName("ulBlueLinks"); for (var i = 0; i < elements.length; i++) { var element = elements[i]; if (element.innerText == "More") { element.click(); } }')
            time.sleep(5)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            review_blocks = soup.find_all('div', {"class": "review-container"})

            ########################################################################################################################

            for review_block in review_blocks:
                review_index += 1
                reviewer_name = review_block.find('div', {"class": "info_text"}).find('div').text
                review_title = review_block.find('a', {"class": "title"}).text
                review_text = review_block.find('p', {"class": "partial_entry"}).text
                review_date = review_block.find('span', {"class": "ratingDate"}).get('title')

                try:
                    checkin_date = review_block.find('div', {"class": "prw_reviews_stay_date_hsx"}).text.replace('Date of experience: ','')
                except:
                    checkin_date = None

                stars = review_block.find('span', {"class": "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
                stars = str(int(stars) / 10)

                review = {
                    'review_id': review_index,
                    'business_id': business_index,
                    'reviewer_name': reviewer_name,
                    'title': review_title,
                    'text': review_text,
                    'tip': None,
                    'date': review_date,
                    'trip_type': None,
                    'checkin_date': checkin_date,
                    'stars': stars
                }

                review_list.append(review)

            if review_index == 500:
                break

            if current_page < len(page_list):
                browser.execute_script("document.getElementsByClassName('ui_button nav next primary')[0].click()")
            time.sleep(5)

        attractions.append(attraction)
        reviews.extend(review_list)
        
        business_index += 1

except Exception as e:
    print(traceback.format_exc())
finally:
    browser.quit()

    with open('data/attractions.json', 'w', encoding='utf-8') as f:
        json.dump(attractions, f, ensure_ascii=False, indent=4)

    with open('data/reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)