from bs4 import BeautifulSoup
from selenium import webdriver
import re
import time
import json
import traceback
 
target_urls = [
    "https://www.tripadvisor.com.ph/Restaurant_Review-g298461-d16966329-Reviews-A_Mesa_Seafood_Tapas_Bar-Lapu_Lapu_Mactan_Island_Cebu_Island_Visayas.html"
]

browser = webdriver.Chrome()

restaurants = []
reviews = []

try:
    travel_index = 1

    for url in target_urls:
        browser.execute_script("window.open('" + url + "', '_parent')")

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        try:
            check_last_page = '.pageNumbers .pageNum:last-child'
            page_list = range(int(soup.select(check_last_page)[0].text))
        except:
            page_list = range(1)

        ########## HEADER BLOCKS ##########

        header_blocks = soup.find_all('div', {"class": "ppr_priv_resp_rr_top_info"})

        for header_block in header_blocks:
            name = header_block.find('h1', {"class", "ui_header"}).text

            rating = header_block.find('span', {"class", "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
            rating = str(int(rating) / 10)

            review_count = header_block.find('span', {"class", "reviewCount"}).text.replace(' reviews', '').replace(' review', '')

            try:
                popularity = header_block.find('span', {"class", "header_popularity"}).text
            except:
                popularity = None

            try:
                tags = header_block.find('div', {"class", "prw_restaurants_restaurant_detail_tags"}).text
                tags = [x.strip() for x in tags.split(',')]
            except:
                tags = []

            try:
                street_address = header_block.find('span', {"class", "street-address"}).text
            except:
                street_address = None

            try:
                extended_address = header_block.find('span', {"class", "extended-address"}).text.replace(',', '').strip()
            except:
                extended_address = None
            
            try:
                locality = re.split(r'(^[^\d]+)', header_block.find('span', {"class", "locality"}).text)[1:]
                city = locality[0].strip().replace(',', '').strip()
                postal_code = locality[1].replace(',', '').strip()
            except:
                city = None
                postal_code = None

            country = header_block.find('span', {"class", "country-name"}).text

        ########## PHOTO BLOCKS ##########
        
        photo_blocks = soup.find_all('div', {"class": "mosaic_photos"})

        for photo_block in photo_blocks:
            photo_url = photo_block.find('img', {"class", "basicImg"}).get('data-lazyurl')

        ########## RATING BLOCKS ##########

        rating_blocks = soup.find_all('div', {"class": "restaurants-detail-overview-cards-RatingsOverviewCard__ratingQuestionRow--5nPGK"})

        rating_food = None
        rating_service = None
        rating_value = None
        rating_atmosphere = None

        for rating_block in rating_blocks:

            icon_name = rating_block.find('span', {"class": "restaurants-detail-overview-cards-RatingsOverviewCard__ratingIcon--27ecu"}).get('class')[1]
            rating_value = rating_block.find('span', {"class": "restaurants-detail-overview-cards-RatingsOverviewCard__ratingBubbles--1kQYC"}).find('span').get('class')[1].replace('bubble_','')
            rating_value = str(int(rating_value) / 10)

            if icon_name == 'restaurants':
                rating_food = rating_value
            elif icon_name == 'bell':
                rating_service = rating_value
            elif icon_name == 'wallet-fill':
                rating_value = rating_value
            elif icon_name == 'ambience':
                rating_atmosphere = rating_value

        ########## ABOUT BLOCKS ##########

        has_about = False

        price_range = None
        special_diets = []
        cuisines = []
        meals = []
        features = []

        about_blocks = soup.find_all('div', {"class": "restaurants-detail-overview-cards-DetailsSectionOverviewCard__detailCard--WpImp"})

        for about_block in about_blocks:

            about_read_more = about_block.find('a', {"class", "restaurants-detail-overview-cards-DetailsSectionOverviewCard__viewDetails--ule3z"})

            if about_read_more:
                browser.execute_script("document.getElementsByClassName('restaurants-detail-overview-cards-DetailsSectionOverviewCard__viewDetails--ule3z')[0].click()")
        
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                time.sleep(5)

                try:
                    about = soup.select(".restaurants-detail-overview-cards-DetailsSectionOverviewCard__desktopAboutText--VY6hs")[0].text
                except:
                    about = None
                
                categories = soup.find_all('div', {"class": "restaurants-detail-overview-cards-DetailsSectionOverviewCard__categoryTitle--2RJP_"})
                categories_text = soup.find_all('div', {"class": "restaurants-detail-overview-cards-DetailsSectionOverviewCard__tagText--1OH6h"})

                category_index = 0

                for category in categories:
                    category = category.text.lower()
                    if category == 'price range':
                        price_range = categories_text[category_index].text
                    if category == 'special diets':
                        special_diets = categories_text[category_index].text
                        special_diets = [x.strip() for x in special_diets.split(',')]
                    if category == 'cuisines':
                        cuisines = categories_text[category_index].text
                        cuisines = [x.strip() for x in cuisines.split(',')]
                    if category == 'meals':
                        meals = categories_text[category_index].text
                        meals = [x.strip() for x in meals.split(',')]
                    if category == 'features':
                        features = categories_text[category_index].text
                        features = [x.strip() for x in features.split(',')]

                    category_index += 1

                has_about = True

                browser.execute_script("document.getElementsByClassName('_2EFRp_bb')[0].click()")

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        if not has_about:
            about_blocks = soup.find_all('div', {"class": "restaurants-details-card-DetailsCard__cardBackground--2tGEZ"})

            for about_block in about_blocks:
                
                try:
                    about = about_block.find('div', {"class": "restaurants-details-card-DesktopView__desktopAboutText--1VvQH"}).text
                except:
                    about = None

                categories = about_block.find_all('div', {"class": "restaurants-details-card-TagCategories__categoryTitle--28rB6"})
                categories_text = about_block.find_all('div', {"class": "restaurants-details-card-TagCategories__tagText--Yt3iG"})

                category_index = 0

                for category in categories:
                    category = category.text.lower()
                    if category == 'price range':
                        price_range = categories_text[category_index].text
                    if category == 'special diets':
                        special_diets = categories_text[category_index].text
                        special_diets = [x.strip() for x in special_diets.split(',')]
                    if category == 'cuisines':
                        cuisines = categories_text[category_index].text
                        cuisines = [x.strip() for x in cuisines.split(',')]
                    if category == 'meals':
                        meals = categories_text[category_index].text
                        meals = [x.strip() for x in meals.split(',')]
                    if category == 'features':
                        features = categories_text[category_index].text
                        features = [x.strip() for x in features.split(',')]

                    category_index += 1

        if not price_range and len(tags) > 0:
            price_range = tags[0]

        if len(tags) > 0:
            tags = tags[1:]

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        ########## CONTACT BLOCKS ##########

        email = None
        contact_number = None

        contact_blocks = soup.find_all('div', {"class": "restaurants-detail-overview-cards-LocationOverviewCard__cardColumn--2ALwF"})

        for contact_block in contact_blocks:
            contact_rows = contact_block.find_all('div', {"class": "restaurants-detail-overview-cards-LocationOverviewCard__contactRow--3LF7z"})

            for contact in contact_rows:
                icon = contact.find('span', {"class": "ui_icon"})

                if icon:
                    icon_name = icon.get('class')[1]

                    if icon_name == 'email':
                        email = contact.find('a').get('href').replace('mailto:', '').replace('?subject=?', '')
                    if icon_name == 'phone':
                        contact_number = contact.find('a').get('href').replace('tel:', '')

        ########## REVIEW FILTER BLOCKS ##########
        
        popular_mentions = []

        review_filter_blocks = soup.find_all('div', {"class": "ui_tagcloud_group"})

        for review_filter_block in review_filter_blocks:

            mentions = review_filter_block.find_all('span', {"class": "ui_tagcloud"})

            for mention in mentions:
                popular_mentions.append(mention.text.strip())

            popular_mentions = popular_mentions[1:]

        restaurant = {
            'travel_id': travel_index,
            'name': name,
            'about': about,
            'photo_url': photo_url,
            'rating': rating,
            'ratings': {
                'food': rating_food,
                'service': rating_service,
                'value': rating_value,
                'atmosphere': rating_atmosphere
            },
            'review_count': review_count,
            'popularity': popularity,
            'price_range': price_range,
            'special_diets': special_diets,
            'cuisines': cuisines,
            'meals': meals,
            'features': features,
            'tags': tags,
            'popular_mentions': popular_mentions,
            'hours': {
                'Monday': [],
                'Tuesday': [],
                'Wednesday': [],
                'Thursday': [],
                'Friday': [],
                'Saturday': [],
                'Sunday': []
            },
            'latitude': '',
            'longitude': '',
            'address': {
                'street_address': street_address,
                'extended_address': extended_address,
                'city': city,
                'postal_code': postal_code,
                'country': country
            },
            'email_address': email,
            'contact_number': contact_number,
            'website': None
        }

        restaurants.append(restaurant)

        review_index = 0
            
        for current_page in page_list:
            current_page += 1
            browser.execute_script('var elements = document.getElementsByClassName("ulBlueLinks"); for (var i = 0; i < elements.length; i++) { var element = elements[i]; if (element.innerText == "More") { element.click(); } }')
            time.sleep(5)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            review_blocks = soup.find_all('div', {"class": "review-container"})

            ########## REVIEW BLOCKS ##########

            for review_block in review_blocks:
                review_index += 1
                reviewer_name = review_block.find('div', {"class": "info_text"}).find('div').text
                review_title = review_block.find('a', {"class": "title"}).text
                review_text = review_block.find('p', {"class": "partial_entry"}).text
                review_date = review_block.find('span', {"class": "ratingDate"}).get('title')

                try:
                    stay_date = review_block.find('div', {"class": "prw_reviews_stay_date_hsx"}).text.replace('Date of visit: ','')
                except:
                    stay_date = None

                rating = review_block.find('span', {"class": "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
                rating = str(int(rating) / 10)

                review = {
                    'review_id': review_index,
                    'travel_id': travel_index,
                    'user_name': reviewer_name,
                    'title': review_title,
                    'text': review_text,
                    'date': review_date,
                    'stay_date': stay_date,
                    'rating': rating
                }

                reviews.append(review)

            if review_index == 500:
                break

            if current_page < len(page_list):
                browser.execute_script("document.getElementsByClassName('ui_button nav next primary')[0].click()")
            time.sleep(5)
        
        travel_index += 1

except Exception as e:
    print(traceback.format_exc())
finally:
    browser.quit()

    with open('data/restaurants.json', 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)

    with open('data/reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)