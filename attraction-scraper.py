from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date
import re
import time
import json
import traceback
 
target_urls = [
    "https://www.tripadvisor.com.ph/Attraction_Review-g19743337-d14088497-Reviews-Cebu_Safari_Adventure_Park-Carmen_Cebu_Island_Visayas.html"
]

browser = webdriver.Chrome()
browser.maximize_window()

attractions = []
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

        header_blocks = soup.find_all('div', {"class": "contentWrapper"})

        for header_block in header_blocks:
            name = header_block.find('h1', {"class", "ui_header"}).text

            rating = header_block.find('span', {"class", "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
            rating = str(int(rating) / 10)

            review_count = header_block.find('span', {"class", "reviewCount"}).text.replace(' Reviews', '').replace(' Review', '')

            try:
                popularity = header_block.find('span', {"class", "header_popularity"}).text
            except:
                popularity = None

            try:
                tags = header_block.find('span', {"class", "animal_tag"}).find('span', {"class": "detail"}).text
                tags = [x.strip() for x in tags.split(',')]

                categories = header_block.find('span', {"class", "attractionCategories"}).find('div', {"class": "detail"}).text
                categories = [x.strip() for x in categories.split(',')]

                tags.extend(categories)
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

        for element in photo_blocks:
            photo_url = element.find('img', {"class", "basicImg"}).get('src')

        ########## ABOUT BLOCKS ##########

        about = None
        suggested_duration = None

        about_blocks = soup.find_all('div', {"class": "attractions-attraction-detail-about-card-AttractionDetailAboutCard__section--1_Efg"})

        for about_block in about_blocks:

            span_container = about_block.find('span')

            if span_container:
                if span_container.has_attr('class'):
                    if span_container.get('class')[1] == 'duration':
                        suggested_duration = about_block.text.replace('Suggested Duration:', '')
                else:
                    about_read_more = about_block.find('span', {"class", "attractions-attraction-detail-about-card-Description__readMore--2pd33"})

                    if about_read_more:                        
                        browser.execute_script("document.getElementsByClassName('attractions-attraction-detail-about-card-Description__readMore--2pd33')[0].click()")
                
                        soup = BeautifulSoup(browser.page_source, 'html.parser')
                        time.sleep(5)

                        about = soup.select(".attractions-attraction-detail-about-card-Description__modalText--1oJCY")[0].text

                        browser.execute_script("document.getElementsByClassName('_2EFRp_bb')[0].click()")
                    else:
                        about = span_container.text

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        ########## CONTACT BLOCKS ##########

        contact_blocks = soup.find_all('div', {"id": "taplc_location_detail_contact_card_ar_responsive_0"})

        for contact_block in contact_blocks:
            contact_info = contact_block.find('div', {"class": "contactInfo"})

            try:
                contact_number = contact_info.find('div', {"class": "detail_section phone"}).text
            except:
                contact_number = None

        ########## REVIEW FILTER BLOCKS ##########
        
        popular_mentions = []

        review_filter_blocks = soup.find_all('div', {"class": "location-review-review-list-parts-ReviewFilters__filters_wrap--y1t86"})

        for review_filter_block in review_filter_blocks:

            mentions = review_filter_block.find_all('button', {"class": "location-review-review-list-parts-SearchFilter__word_button_secondary--2p0YL"})

            for mention in mentions:
                popular_mentions.append(mention.text)

        attraction = {
            'travel_id': travel_index,
            'name': name,
            'about': about,
            'photo_url': photo_url,
            'rating': rating,
            'review_count': review_count,
            'popularity': popularity,
            'suggested_duration': suggested_duration,
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
            'contact_number': contact_number,
            'website': None
        }

        attractions.append(attraction)

        review_index = 0
            
        for current_page in page_list:
            current_page += 1
            browser.execute_script('var elements = document.getElementsByClassName("_36B4Vw6t"); for (var i = 0; i < elements.length; i++) { var element = elements[i]; if (element.innerText == "Read more") { element.click(); } }')
            time.sleep(3)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            review_blocks = soup.find_all('div', {"class": "location-review-card-Card__ui_card--2Mri0 location-review-card-Card__card--o3LVm location-review-card-Card__section--NiAcw"})

            ########## REVIEW BLOCKS ##########

            for review_block in review_blocks:
                review_index += 1
                reviewer_name = review_block.find('a', {"class": "ui_header_link social-member-event-MemberEventOnObjectBlock__member--35-jC"}).text
                review_title = review_block.find('a', {"class": "location-review-review-list-parts-ReviewTitle__reviewTitleText--2tFRT"}).text
                review_text = review_block.find('q', {"class": "location-review-review-list-parts-ExpandableReview__reviewText--gOmRC"}).text
                review_date = review_block.find('div', {"class": "social-member-event-MemberEventOnObjectBlock__event_type--3njyv"}).text.replace(reviewer_name + ' wrote a review ','')
                
                try:
                    trip_type = review_block.find('span', {"class": "location-review-review-list-parts-TripType__trip_type--3w17i"}).text.replace('Trip type: ','')
                except:
                    trip_type = None

                try:
                    event_date = review_block.find('span', {"class": "location-review-review-list-parts-EventDate__event_date--1epHa"}).text.replace('Date of experience: ','')
                except:
                    event_date = None

                rating = review_block.find('span', {"class": "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
                rating = str(int(rating) / 10)
                
                try:
                    review_date = datetime.strptime(review_date, "%b %Y")
                except:
                    today = date.today()
                    review_date = today.strftime("%b %Y")

                review = {
                    'review_id': review_index,
                    'travel_id': travel_index,
                    'user_name': reviewer_name,
                    'title': review_title,
                    'text': review_text,
                    'date': review_date,
                    'trip_type': trip_type,
                    'event_date': event_date,
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
    # browser.quit()

    with open('data/attractions.json', 'w', encoding='utf-8') as f:
        json.dump(attractions, f, ensure_ascii=False, indent=4)

    with open('data/reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)