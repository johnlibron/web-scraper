import json
import re
import string
import time
import traceback

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
 
target_urls = []

browser = webdriver.Chrome()
browser.maximize_window()

hotels = []
reviews = []

try:
    business_index = 1

    for url in target_urls:
        browser.execute_script("window.open('" + url + "', '_parent')")
        time.sleep(5)
        
        # browser.execute_script("document.getElementsByClassName('hotels-hotel-review-atf-info-parts-SaveButton__savesText--1raLE')[0].innerText = JSON.stringify(window.__WEB_CONTEXT__.pageManifest.urqlCache).toString()")

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        main_window = browser.current_window_handle

        try:
            check_last_page = '.pageNumbers .pageNum:last-child'
            page_list = range(int(soup.select(check_last_page)[0].text))
        except:
            page_list = range(1)

        ########################################################################################################################

        header_block = soup.find('div', {"class": "hotels-hotel-review-atf-info-parts-ATFInfo__wrapper--2_Y5L"})

        name = header_block.find('h1', {"class", "hotels-hotel-review-atf-info-parts-Heading__heading--2ZOcD"}).text

        try:
            stars = header_block.find('span', {"class", "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
            stars = str(int(stars) / 10)
        except:
            stars = None

        try:
            review_count = header_block.find('span', {"class", "hotels-hotel-review-atf-info-parts-Rating__reviewCount--1sk1X"}).text.replace(' reviews', '').replace(' review', '')
        except:
            review_count = None

        try:
            popularity = header_block.find('div', {"class", "hotels-hotel-review-atf-info-parts-PopIndex__popIndex--1Nei0"}).text
        except:
            popularity = None

        try:
            address = header_block.find('span', {"class", "public-business-listing-ContactInfo__ui_link--1_7Zp public-business-listing-ContactInfo__level_4--3JgmI"}).text
        except:
            address = None

        try:
            browser.execute_script("document.getElementsByClassName('internet')[0].click()")
            time.sleep(5)
            browser.switch_to.window(browser.window_handles[1])

            website = browser.current_url

            browser.close()
            browser.switch_to.window(main_window)
        except:
            website = None
            
        # content = soup.find('span', {"class": "hotels-hotel-review-atf-info-parts-SaveButton__savesText--1raLE"}).text

        # try:
        #     businessAdvantage = re.findall('","businessAdvantage":{"contactLinks":[(?s)(.*)"],"clickTrackingUrl"', content)
        #     print(businessAdvantage)
        #     # email_address = re.findall('"emailParts":["(?s)(.*)"],"clickTrackingUrl"', content)[0]
        #     email_address = None
        # except:
        #     print(traceback.format_exc())
        #     email_address = None

        try:
            contact_number = header_block.find('div', {"class", "hotels-hotel-review-atf-info-parts-BusinessListingEntry__phone--1e9vv"}).text
        except:
            contact_number = None

        ########################################################################################################################
        
        photo_block = soup.find('div', {"class": "hotels-media-album-parts-MediaCarousel__parentContainer--1KNrt"})

        try:
            photo_url = photo_block.find('div', {"class", "ZVAUHZqh"}).get('style')
            photo_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', photo_url)[0]
        except:
            photo_url = None

        ########################################################################################################################

        about = None
        award = None
        rating_location = None
        rating_cleanliness = None
        rating_service = None
        rating_value = None
        categories = []
        property_amenities = []
        room_features = []
        room_types = []
        hotel_style = []
        languages_spoken = []

        about_block = soup.find('div', {"class": "hotels-hotel-review-about-with-photos-layout-LayoutStrategy__columns--1uvt4"})

        try:
            about = about_block.find('div', {"class": "cPQsENeY"}).text
        except:
            about = None

        try:
            award = about_block.find('div', {"class": "hotels-hotel-review-about-csr-Awards__award_text--1J0t2"}).text
        except:
            award = None

        try:
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
        except:
            rating_location = None
            rating_cleanliness = None
            rating_service = None
            rating_value = None

        try:
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
        except:
            languages_spoken = []
            hotel_style = []

        try:
            about_read_more = about_block.find('div', {"class", "hotels-hr-about-amenities-AmenityGroup__showMore--pPz2S"})

            if about_read_more:
                browser.execute_script("document.getElementsByClassName('hotels-hr-about-amenities-AmenityGroup__showMore--pPz2S')[0].click()")
        
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                time.sleep(5)

                category_block = soup.find('div', {"class", "hotels-hr-about-amenities-AmenitiesModal__container--3YXY-"})
                
                categories_block = category_block.find_all('div', {"class": "hotels-hr-about-amenities-AmenitiesModal__group--3nudN"})

                category_index = 0

                for category in categories_block:
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
                categories_block = about_block.find_all('div', {"class": "hotels-hr-about-amenities-AmenityGroup__amenitiesList--3MdFn"})

                category_index = 0

                for category in categories_block:
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

            categories.extend(property_amenities)
            categories.extend(room_features)
            categories.extend(room_types)
        except:
            categories = []

        ########################################################################################################################        

        contact_block = soup.find('div', {"class": "ppr_priv_location_react"})

        try:
            location_url = contact_block.find('img', {"class": "hotels-hotel-review-location-StaticMap__map--3L4sb"}).get('src')

            parsed = urlparse(location_url)
            location = parse_qs(parsed.query)['center'][0].split(',')
            latitude = location[0]
            longitude = location[1]
        except:
            latitude = None
            longitude = None

        ########################################################################################################################

        price_range = None
        also_known_as = []
        formerly_known_as = []
        number_of_rooms = None

        about_hotel_block = soup.find('div', {"class": "hotels-hotel-review-layout-Section__plain--3fYKb"})

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

        ########################################################################################################################
        
        popular_mentions = []

        try:
            review_filter_block = soup.find('div', {"class": "location-review-review-list-parts-SearchFilter__button_wrap--2l_Kd"})

            mentions = review_filter_block.find_all('button', {"class": "location-review-review-list-parts-SearchFilter__word_button_secondary--2p0YL"})

            for mention in mentions:
                popular_mentions.append(mention.text)
        except:
            popular_mentions = []

        hotel = {
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
                'also_known_as': also_known_as,
                'formerly_known_as': formerly_known_as,
                'popularity': popularity,
                'price_range': price_range,
                'award': award,
                'ratings': {
                    'location': rating_location,
                    'cleanliness': rating_cleanliness,
                    'service': rating_service,
                    'value': rating_value
                },
                'hotel_style': hotel_style,
                'languages_spoken': languages_spoken,
                'number_of_rooms': number_of_rooms,
                'popular_mentions': popular_mentions
            },
            'categories': categories,
            'hours': None,
            'website': website,
            'email_address': None,
            'contact_number': contact_number
        }

        review_index = 0
        review_list = []
            
        for current_page in page_list:
            current_page += 1
            browser.execute_script('var elements = document.getElementsByClassName("ulBlueLinks"); for (var i = 0; i < elements.length; i++) { var element = elements[i]; if (element.innerText == "Read more") { element.click(); } }')
            time.sleep(3)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            review_blocks = soup.find_all('div', {"class": "hotels-community-tab-common-Card__card--ihfZB hotels-community-tab-common-Card__section--4r93H"})

            ########################################################################################################################

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
                    checkin_date = review_block.find('span', {"class": "location-review-review-list-parts-EventDate__event_date--1epHa"}).text.replace('Date of stay: ','')
                except:
                    checkin_date = None

                try:
                    tip = review_block.find('div', {"class": "location-review-review-list-parts-InlineRoomTip__tipline--1NsZ-"}).text.replace('Room Tip: ','')
                except:
                    tip = None

                try:
                    stars = review_block.find('span', {"class": "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
                    stars = str(int(stars) / 10)
                except:
                    stars = None
                
                review = {
                    'review_id': review_index,
                    'business_id': business_index,
                    'reviewer_name': reviewer_name,
                    'title': review_title,
                    'text': review_text,
                    'tip': tip,
                    'date': review_date,
                    'trip_type': trip_type,
                    'checkin_date': checkin_date,
                    'stars': stars
                }

                review_list.append(review)

            if review_index == 500:
                break

            if current_page < len(page_list):
                browser.execute_script("document.getElementsByClassName('ui_button nav next primary')[0].click()")
            time.sleep(5)

        hotels.append(hotel)
        reviews.extend(review_list)
        
        business_index += 1

except Exception as e:
    print(traceback.format_exc())
finally:
    browser.quit()

    with open('data/hotels.json', 'w', encoding='utf-8') as f:
        json.dump(hotels, f, ensure_ascii=False, indent=4)

    with open('data/reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)