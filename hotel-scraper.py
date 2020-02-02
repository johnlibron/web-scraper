from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import re
import time
import json
import traceback
import string
 
target_urls = [
    "https://www.tripadvisor.com.ph/Hotel_Review-g608518-d11687524-Reviews-Bai_Hotel_Cebu-Mandaue_Cebu_Island_Visayas.html"
]

browser = webdriver.Chrome()

hotels = []
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

        header_blocks = soup.find_all('div', {"class": "hotels-hotel-review-atf-info-parts-ATFInfo__wrapper--2_Y5L"})

        for header_block in header_blocks:
            name = header_block.find('h1', {"class", "hotels-hotel-review-atf-info-parts-Heading__heading--2ZOcD"}).text

            rating = header_block.find('span', {"class", "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
            rating = str(int(rating) / 10)

            review_count = header_block.find('span', {"class", "hotels-hotel-review-atf-info-parts-Rating__reviewCount--1sk1X"}).text.replace(' reviews', '').replace(' review', '')

            try:
                popularity = header_block.find('div', {"class", "hotels-hotel-review-atf-info-parts-PopIndex__popIndex--1Nei0"}).text
            except:
                popularity = None

            try:
                address = header_block.find('span', {"class", "public-business-listing-ContactInfo__ui_link--1_7Zp public-business-listing-ContactInfo__level_4--3JgmI"}).text
            except:
                address = None

            try:
                contact_number = header_block.find('div', {"class", "hotels-hotel-review-atf-info-parts-BusinessListingEntry__phone--1e9vv"}).text
            except:
                contact_number = None

        ########## PHOTO BLOCKS ##########
        
        photo_blocks = soup.find_all('div', {"class": "hotels-media-album-parts-MediaCarousel__parentContainer--1KNrt"})

        for photo_block in photo_blocks:
            photo_url = photo_block.find('div', {"class", "ZVAUHZqh"}).get('style')
            photo_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', photo_url)[0]

        ########## ABOUT BLOCKS ##########

        about = None
        rating_location = None
        rating_cleanliness = None
        rating_service = None
        rating_value = None
        property_amenities = []
        room_features = []
        room_types = []
        hotel_style = []
        languages_spoken = []

        about_blocks = soup.find_all('div', {"class": "hotels-hotel-review-about-with-photos-layout-LayoutStrategy__columns--1uvt4"})

        for about_block in about_blocks:

            try:
                about = about_block.find('div', {"class": "cPQsENeY"}).text
            except:
                about = None

            rating_blocks = about_block.find_all('div', {"class": "hotels-hotel-review-about-with-photos-Reviews__subratingRow--2u0CJ"})

            for rating_block in rating_blocks:
                text_name = rating_block.find('div', {"class": "hotels-hotel-review-about-with-photos-Reviews__subratingLabel--H8ZI0"}).text.lower()
                rating_value = rating_block.find('span', {"class": "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
                rating_value = str(int(rating_value) / 10)

                if text_name == 'location':
                    rating_location = rating_value
                elif text_name == 'cleanliness':
                    rating_cleanliness = rating_value
                elif text_name == 'service':
                    rating_service = rating_value
                elif text_name == 'value':
                    rating_value = rating_value

            good_to_know_blocks = about_block.find_all('div', {"class": "ui_column is-6"})

            for good_to_know_block in good_to_know_blocks:
                title_text = good_to_know_block.find('div', {"class": "hotels-hr-about-layout-Subsection__title--2a0Ik"}).text.lower()

                if title_text == 'languages spoken':
                    try:
                        item = good_to_know_block.find('div', {"class": "hotels-hr-about-layout-TextItem__textitem--2JToc"}).text
                        
                        more_languages = good_to_know_block.find('span', {"class": "hotels-hotel-review-about-csr-LanguagesSpoken__moreLangs--SaYJI"})

                        if more_languages:
                            item = item.replace(more_languages.text, '')

                            action = ActionChains(browser)
                            element_to_hover_over = browser.find_element(By.CLASS_NAME, 'hotels-hotel-review-about-csr-LanguagesSpoken__moreLangs--SaYJI')
                            action.move_to_element(element_to_hover_over).perform()

                            soup = BeautifulSoup(browser.page_source, 'html.parser')

                            item = item + ", " + soup.find('div', {"class": "hotels-hotel-review-about-csr-LanguagesSpoken__tooltipContent--k_zhC"}).text

                        languages_spoken = [x.strip() for x in item.split(',')]
                    except:
                        languages_spoken = []

                if title_text == 'hotel style':
                    try:
                        items = good_to_know_block.find_all('div', {"class": "hotels-hr-about-layout-TextItem__textitem--2JToc"})

                        for item in items:
                            hotel_style.append(item.text)
                    except:
                        hotel_style = []

                if title_text == 'hotel class':
                    try:
                        title_text = good_to_know_block.find_all('div', {"class": "hotels-hr-about-layout-Subsection__title--2a0Ik"})[1:][0].text.lower()
                        items = good_to_know_block.find_all('div', {"class": "hotels-hr-about-layout-TextItem__textitem--2JToc"})[1:]

                        if title_text == 'hotel style':
                            for item in items:
                                hotel_style.append(item.text)
                    except:
                        hotel_style = []

            soup = BeautifulSoup(browser.page_source, 'html.parser')

            about_read_more = about_block.find('div', {"class", "hotels-hr-about-amenities-AmenityGroup__showMore--pPz2S"})

            if about_read_more:
                browser.execute_script("document.getElementsByClassName('hotels-hr-about-amenities-AmenityGroup__showMore--pPz2S')[0].click()")
        
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                time.sleep(5)
                
                categories = soup.find_all('div', {"class": "hotels-hr-about-amenities-AmenitiesModal__group--3nudN"})

                category_index = 0

                for category in categories:
                    amenities = category.find_all('div', {"class": "hotels-hr-about-amenities-Amenity__amenity--3fbBj"})

                    temp = []

                    for amenity in amenities:
                        temp.append(amenity.text)

                    if category_index == 0:
                        property_amenities = temp
                    elif category_index == 1:
                        room_features = temp
                    elif category_index == 2:
                        room_types = temp

                    category_index += 1
                
                browser.execute_script("document.getElementsByClassName('_2EFRp_bb')[0].click()")

                soup = BeautifulSoup(browser.page_source, 'html.parser')
            else:
                categories = soup.find_all('div', {"class": "hotels-hr-about-amenities-AmenityGroup__amenitiesList--3MdFn"})

                category_index = 0

                for category in categories:
                    amenities = category.find_all('div', {"class": "hotels-hr-about-amenities-Amenity__amenity--3fbBj"})

                    temp = []

                    for amenity in amenities:
                        temp.append(amenity.text)

                    if category_index == 0:
                        property_amenities = temp
                    elif category_index == 1:
                        room_features = temp
                    elif category_index == 2:
                        room_types = temp

                    category_index += 1


        ########## ABOUT HOTEL BLOCKS ##########

        price_range = None
        also_known_as = []
        formerly_known_as = []
        number_of_rooms = None

        about_hotel_blocks = soup.find_all('div', {"class": "ssr-init-26f hotels-hotel-review-layout-Section__plain--3fYKb"})

        for about_hotel_block in about_hotel_blocks:
            title_container = about_hotel_block.find_all('div', {"class": "hotels-hotel-review-about-addendum-AddendumItem__title--2QuyD"})
            item_container = about_hotel_block.find_all('div', {"class": "hotels-hotel-review-about-addendum-AddendumItem__content--iVts5"})

            index = 0
            
            for title in title_container:
                title_text = title.text.lower()

                if title_text == 'price range':
                    price_range = item_container[index].text.strip()
                elif title_text == 'also known as':
                    also_known_as = item_container[index].text
                    also_known_as = [string.capwords(x.strip()) for x in also_known_as.split(',')]
                elif title_text == 'formerly known as':
                    formerly_known_as = item_container[index].text
                    formerly_known_as = [string.capwords(x.strip()) for x in formerly_known_as.split(',')]
                elif title_text == 'number of rooms':
                    number_of_rooms = item_container[index].text

                index += 1

        ########## REVIEW FILTER BLOCKS ##########
        
        popular_mentions = []

        review_filter_blocks = soup.find_all('div', {"class": "location-review-review-list-parts-SearchFilter__button_wrap--2l_Kd"})

        for review_filter_block in review_filter_blocks:

            mentions = review_filter_block.find_all('button', {"class": "location-review-review-list-parts-SearchFilter__word_button_secondary--2p0YL"})

            for mention in mentions:
                popular_mentions.append(mention.text)

        hotel = {
            'travel_id': travel_index,
            'name': name,
            'also_known_as': also_known_as,
            'formerly_known_as': formerly_known_as,
            'about': about,
            'photo_url': photo_url,
            'rating': rating,
            'ratings': {
                'location': rating_location,
                'cleanliness': rating_cleanliness,
                'service': rating_service,
                'value': rating_value
            },
            'review_count': review_count,
            'popularity': popularity,
            'price_range': price_range,
            'property_amenities': property_amenities,
            'room_features': room_features,
            'room_types': room_types,
            'hotel_style': hotel_style,
            'languages_spoken': languages_spoken,
            'number_of_rooms': number_of_rooms,
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
            'address': address,
            'contact_number': contact_number,
            'website': None
        }

        hotels.append(hotel)

        review_index = 0
            
        for current_page in page_list:
            current_page += 1
            browser.execute_script('var elements = document.getElementsByClassName("ulBlueLinks"); for (var i = 0; i < elements.length; i++) { var element = elements[i]; if (element.innerText == "Read more") { element.click(); } }')
            time.sleep(3)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            review_blocks = soup.find_all('div', {"class": "hotels-community-tab-common-Card__card--ihfZB hotels-community-tab-common-Card__section--4r93H"})

            ########## REVIEW BLOCKS ##########

            for review_block in review_blocks:
                review_index += 1
                reviewer_name = review_block.find('a', {"class": "social-member-event-MemberEventOnObjectBlock__member--35-jC"}).text
                review_title = review_block.find('div', {"class": "location-review-review-list-parts-ReviewTitle__reviewTitle--2GO9Z"}).text
                review_text = review_block.find('q', {"class": "location-review-review-list-parts-ExpandableReview__reviewText--gOmRC"}).text
                review_date = review_block.find('div', {"class": "social-member-event-MemberEventOnObjectBlock__event_type--3njyv"}).text.replace(reviewer_name + ' wrote a review ','')
                
                try:
                    review_date = datetime.strptime(review_date, "%b %Y").strftime("%b %Y")
                except:
                    today = datetime.now()
                    review_date = today.strftime("%b %Y")

                try:
                    trip_type = review_block.find('span', {"class": "location-review-review-list-parts-TripType__trip_type--3w17i"}).text.replace('Trip type: ','')
                except:
                    trip_type = None

                try:
                    stay_date = review_block.find('span', {"class": "location-review-review-list-parts-EventDate__event_date--1epHa"}).text.replace('Date of stay: ','')
                except:
                    stay_date = None

                try:
                    room_tip = review_block.find('div', {"class": "location-review-review-list-parts-InlineRoomTip__tipline--1NsZ-"}).text.replace('Room Tip: ','')
                except:
                    room_tip = None

                rating = review_block.find('span', {"class": "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
                rating = str(int(rating) / 10)

                review = {
                    'review_id': review_index,
                    'travel_id': travel_index,
                    'user_name': reviewer_name,
                    'title': review_title,
                    'text': review_text,
                    'room_tip': room_tip,
                    'date': review_date,
                    'trip_type': trip_type,
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

    with open('data/hotels.json', 'w', encoding='utf-8') as f:
        json.dump(hotels, f, ensure_ascii=False, indent=4)

    with open('data/reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)