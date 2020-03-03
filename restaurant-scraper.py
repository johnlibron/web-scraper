import json
import re
import time
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse, parse_qs
 
target_urls = [
    "https://www.tripadvisor.com.ph/Restaurant_Review-g298461-d16966329-Reviews-A_Mesa_Seafood_Tapas_Bar-Lapu_Lapu_Mactan_Island_Cebu_Island_Visayas.html"
]

browser = webdriver.Chrome()
browser.maximize_window()

restaurants = []
reviews = []

try:
    business_index = 1

    for url in target_urls:
        browser.execute_script("window.open('" + url + "', '_parent')")
        time.sleep(5)

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        main_window = browser.current_window_handle

        try:
            check_last_page = '.pageNumbers .pageNum:last-child'
            page_list = range(int(soup.select(check_last_page)[0].text))
        except:
            page_list = range(1)

        ########################################################################################################################

        header_block = soup.find('div', {"class": "ppr_priv_resp_rr_top_info"})

        name = header_block.find('h1', {"class", "ui_header"}).text

        stars = header_block.find('span', {"class", "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
        stars = str(int(stars) / 10)

        review_count = header_block.find('span', {"class", "reviewCount"}).text.replace(' reviews', '').replace(' review', '')

        try:
            popularity = header_block.find('span', {"class", "header_popularity"}).text
        except:
            popularity = None

        try:
            categories = header_block.find('div', {"class", "prw_restaurants_restaurant_detail_tags"}).text
            categories = [x.strip() for x in categories.split(',')]
        except:
            categories = []

        open_hours = header_block.find('span', {"class", "public-location-hours-LocationHours__hoursOpenerText--42y6t"}).text
        hours = []

        if open_hours != '+ Add hours':
            browser.execute_script("document.getElementsByClassName('public-location-hours-LocationHours__hoursOpenerText--42y6t')[0].click()")
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

        ########################################################################################################################
        
        photo_block = soup.find('div', {"class": "mosaic_photos"})

        try:
            photo_url = photo_block.find('img', {"class", "basicImg"}).get('data-lazyurl')
        except:
            photo_url = None

        ########################################################################################################################
        
        try:
            award = soup.find('span', {"class": "restaurants-detail-overview-cards-RatingsOverviewCard__awardText--1Kl1_"}).text + " "
            award += soup.find('span', {"class": "restaurants-detail-overview-cards-RatingsOverviewCard__yearsText--m3NBd"}).text
        except:
            award = None

        ########################################################################################################################

        stars_blocks = soup.find_all('div', {"class": "restaurants-detail-overview-cards-RatingsOverviewCard__ratingQuestionRow--5nPGK"})

        stars_food = None
        stars_service = None
        stars_value = None
        stars_atmosphere = None

        for stars_block in stars_blocks:
            
            icon_name = stars_block.find('span', {"class": "restaurants-detail-overview-cards-RatingsOverviewCard__ratingIcon--27ecu"}).get('class')[1]
            stars = stars_block.find('span', {"class": "restaurants-detail-overview-cards-RatingsOverviewCard__ratingBubbles--1kQYC"}).find('span').get('class')[1].replace('bubble_','')
            stars = str(int(stars) / 10)

            if icon_name == 'restaurants':
                stars_food = stars
            elif icon_name == 'bell':
                stars_service = stars
            elif icon_name == 'wallet-fill':
                stars_value = stars
            elif icon_name == 'ambience':
                stars_atmosphere = stars

        ########################################################################################################################

        price_range = None
        special_diets = []
        cuisines = []
        meals = []
        features = []

        about_block = soup.find('div', {"class": "restaurants-detail-overview-cards-DetailsSectionOverviewCard__detailCard--WpImp"})

        try:
            about_read_more = about_block.find('a', {"class", "restaurants-detail-overview-cards-DetailsSectionOverviewCard__viewDetails--ule3z"})
        except:
            about_read_more = None
            
        if about_read_more:
            browser.execute_script("document.getElementsByClassName('restaurants-detail-overview-cards-DetailsSectionOverviewCard__viewDetails--ule3z')[0].click()")
            time.sleep(5)
    
            soup = BeautifulSoup(browser.page_source, 'html.parser')

            try:
                about = soup.find('div', {"class": "restaurants-detail-overview-cards-DetailsSectionOverviewCard__desktopAboutText--VY6hs"}).text
            except:
                about = None
            
            category_titles = soup.find_all('div', {"class": "restaurants-detail-overview-cards-DetailsSectionOverviewCard__categoryTitle--2RJP_"})
            tag_texts = soup.find_all('div', {"class": "restaurants-detail-overview-cards-DetailsSectionOverviewCard__tagText--1OH6h"})

            category_index = 0

            for category_title in category_titles:
                category_title = category_title.text.lower()
                if category_title == 'price range':
                    price_range = tag_texts[category_index].text
                if category_title == 'special diets':
                    special_diets = tag_texts[category_index].text
                    special_diets = [x.strip() for x in special_diets.split(',')]
                if category_title == 'cuisines':
                    cuisines = tag_texts[category_index].text
                    cuisines = [x.strip() for x in cuisines.split(',')]
                if category_title == 'meals':
                    meals = tag_texts[category_index].text
                    meals = [x.strip() for x in meals.split(',')]
                if category_title == 'features':
                    features = tag_texts[category_index].text
                    features = [x.strip() for x in features.split(',')]

                category_index += 1

            browser.execute_script("document.getElementsByClassName('_2EFRp_bb _3ptEwvMl')[0].click()")

        else:
            about_block = soup.find('div', {"class": "restaurants-details-card-DetailsCard__cardBackground--2tGEZ"})
                
            try:
                about = about_block.find('div', {"class": "restaurants-details-card-DesktopView__desktopAboutText--1VvQH"}).text
            except:
                about = None

            category_titles = about_block.find_all('div', {"class": "restaurants-details-card-TagCategories__categoryTitle--28rB6"})
            tag_texts = about_block.find_all('div', {"class": "restaurants-details-card-TagCategories__tagText--Yt3iG"})

            category_index = 0

            for category_title in category_titles:
                category_title = category_title.text.lower()
                if category_title == 'price range':
                    price_range = tag_texts[category_index].text
                if category_title == 'special diets':
                    special_diets = tag_texts[category_index].text
                    special_diets = [x.strip() for x in special_diets.split(',')]
                if category_title == 'cuisines':
                    cuisines = tag_texts[category_index].text
                    cuisines = [x.strip() for x in cuisines.split(',')]
                if category_title == 'meals':
                    meals = tag_texts[category_index].text
                    meals = [x.strip() for x in meals.split(',')]
                if category_title == 'features':
                    features = tag_texts[category_index].text
                    features = [x.strip() for x in features.split(',')]

                category_index += 1

        if not price_range and len(categories) > 0:
            price_range = categories[0]

        if len(categories) > 0:
            categories = categories[1:]

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        ########################################################################################################################

        email_address = None
        contact_number = None
        website = None

        contact_block = soup.find('div', {"class": "restaurants-detail-overview-cards-LocationOverviewCard__cardColumn--2ALwF"})

        contact_rows = contact_block.find_all('div', {"class": "restaurants-detail-overview-cards-LocationOverviewCard__contactRow--3LF7z"})

        for contact_row in contact_rows:

            contact_details = contact_row.find_all('div', {"class": "restaurants-detail-overview-cards-LocationOverviewCard__detailLink--iyzJI"})

            for contact_detail in contact_details:

                contact_icon = contact_detail.find('span', {"class": "ui_icon"})

                if contact_icon:
                    contact_icon_name = contact_icon.get('class')[1]

                    if contact_icon_name == 'email':
                        email_address = contact_detail.find('a').get('href').replace('mailto:', '').replace('?subject=?', '')
                    if contact_icon_name == 'phone':
                        contact_number = contact_detail.find('a').get('href').replace('tel:', '')
                    if contact_icon_name == 'laptop':
                        browser.execute_script("document.getElementsByClassName('laptop restaurants-detail-overview-cards-LocationOverviewCard__detailLinkIcon--T_k32')[0].click()")
                        time.sleep(5)
                        browser.switch_to.window(browser.window_handles[1])

                        website = browser.current_url

                        browser.close()
                        browser.switch_to.window(main_window)

        try:
            address = contact_block.find('span', {"class", "restaurants-detail-overview-cards-LocationOverviewCard__detailLinkText--co3ei"}).text
        except:
            address = None

        try:
            location_url = contact_block.find('img', {"class": "restaurants-detail-overview-cards-LocationOverviewCard__mapImage--22-Al"}).get('src')

            parsed = urlparse(location_url)
            location = parse_qs(parsed.query)['center'][0].split(',')
            latitude = location[0]
            longitude = location[1]
        except:
            latitude = None
            longitude = None

        ########################################################################################################################
        
        popular_mentions = []

        review_filter_block = soup.find('div', {"class": "ui_tagcloud_group"})

        mentions = review_filter_block.find_all('span', {"class": "ui_tagcloud"})

        for mention in mentions:
            popular_mentions.append(mention.text.strip())

        popular_mentions = popular_mentions[1:]

        restaurant = {
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
                'price_range': price_range,
                'award': award,
                'additional_stars': {
                    'food': stars_food,
                    'service': stars_service,
                    'value': stars_value,
                    'atmosphere': stars_atmosphere
                },
                'cuisines': cuisines,
                'special_diets': special_diets,
                'meals': meals,
                'features': features,
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
                    checkin_date = review_block.find('div', {"class": "prw_reviews_stay_date_hsx"}).text.replace('Date of visit: ','')
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

        restaurants.append(restaurant)
        reviews.extend(review_list)
        
        business_index += 1

except Exception as e:
    print(traceback.format_exc())
finally:
    browser.quit()

    with open('data/restaurants.json', 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)

    with open('data/reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)