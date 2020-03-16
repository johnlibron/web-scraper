import json
import re
import time
import traceback

from bs4 import BeautifulSoup
from datetime import datetime
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
        time.sleep(5)

        ########################################################################################################################
        
        about = None
        suggested_duration = None
        hours = []
        categories = []

        header_block = soup.find('div', {"class": "attractions-attraction-review-atf-AttractionReviewATFLayout__atf_left_column--1ogzd"})

        name = header_block.find('h1', {"class", "ui_header"}).text

        try:
            stars = header_block.find('span', {"class", "ui_bubble_rating"}).get('class')[1].replace('bubble_','')
            stars = str(int(stars) / 10)
        except:
            stars = None
        
        try:
            review_count = header_block.find('span', {"class", "attractions-attraction-review-header-attraction-review-header__reviewCount--3cEMP"}).text.replace(' Reviews', '').replace(' Review', '')
        except:
            review_count = None

        try:
            popularity = header_block.find('div', {"class", "attractions-attraction-review-header-attraction-review-header__popIndex--H1_nL"}).text
        except:
            popularity = None

        try:
            tags = header_block.find('span', {"class", "attractions-features-animals-FeaturesAnimals__animalTagText--L7OnX"}).text
            tags = [x.strip() for x in tags.split(',')]
        except:
            tags = []

        try:
            category_list = []
            categories = header_block.find_all('a', {"class", "attractions-attraction-review-header-AttractionLinks__dotted_link--Pt2MP"})
            for category in categories:
                text = category.text.strip()
                if text != 'More':
                    category_list.append(text)
            categories = category_list
        except:
            categories = []

        categories.extend(tags)

        about_block = header_block.find('div', {"class", "attractions-attraction-review-atf-overview-card-AttractionReviewATFOverviewCard__aboutCardWrapper--2S7nY"})

        try:
            about_more = header_block.find('span', {"class", "attractions-attraction-review-atf-overview-card-AttractionReviewATFOverviewCard__descriptionReadMore--S6hh4"})
            
            if about_more:
                browser.execute_script("document.getElementsByClassName('attractions-attraction-review-atf-overview-card-AttractionReviewATFOverviewCard__descriptionReadMore--S6hh4')[0].click()")
                soup = BeautifulSoup(browser.page_source, 'html.parser')

                about = soup.find('div', {"class", "attractions-attraction-detail-about-card-Description__modalText--1oJCY"}).text

                browser.execute_script("document.getElementsByClassName('_2EFRp_bb _3ptEwvMl')[0].click()")
                soup = BeautifulSoup(browser.page_source, 'html.parser')
            else:
                about = about_block.find('span').text
        except:
            about = None

        try:
            open_hours = header_block.find('div', {"class", "public-location-hours-LocationHours__hoursOpenerContainer---ULd_"})

            if open_hours:
                browser.execute_script("document.getElementsByClassName('public-location-hours-LocationHours__hoursOpenerText--42y6t')[0].click()")
                
                soup = BeautifulSoup(browser.page_source, 'html.parser')

                hours_array = soup.find_all('div', {"class": "public-location-hours-AllHoursList__daysAndTimesRow--2CcRX"})
                x = 0
                while x < len(hours_array):
                    if x % 2 == 1:
                        hours.append(hours_array[x-1].text + " | " + hours_array[x].text)
                    x += 1

                browser.execute_script("document.getElementsByClassName('_3yn85ktl _1UnOCDRu')[0].click()")
                soup = BeautifulSoup(browser.page_source, 'html.parser')
        except:
            hours = []

        try:
            icon_duration = about_block.find('span', {"class", "duration"})
            if icon_duration:
                suggested_duration = about_block.find('div', {"class", "attractions-attraction-detail-about-card-AboutSection__sectionWrapper--3PMQg"}).text.replace('Suggested Duration:', '')
        except:
            suggested_duration = None

        ########################################################################################################################
        
        photo_block = soup.find('div', {"class": "attractions-attraction-review-media-carousel-AttractionReviewMediaCarousel__media_carousel--3VBae"})

        try:
            photo_url = photo_block.find('div', {"class", "ZVAUHZqh"}).get('style')
            photo_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', photo_url)[0]
        except:
            photo_url = None

        ########################################################################################################################

        address = None
        website = None
        contact_number = None
        email_address = None

        contact_block = soup.find('div', {"class": "ppr_priv_nearby_location"})
        contact_rows = contact_block.find_all('div', {"class", "attractions-contact-card-ContactCard__contactRow--3Ih6v"})

        for contact_row in contact_rows:
            contact_row_span = contact_row.find('span', {"class", "ui_icon"})
            if contact_row_span.has_attr('class'):
                if contact_row_span.get('class')[1] == 'map-pin-fill':
                    address = contact_row.text
                elif contact_row_span.get('class')[1] == 'laptop':
                    website = contact_row.find('div', {"class", "_2wKz--mA"}).get('data-encoded-url')
                elif contact_row_span.get('class')[1] == 'phone':
                    contact_number = contact_row.text
                elif contact_row_span.get('class')[1] == 'email':
                    content = soup.find('div', {"class": "logo_slogan"}).text

                    try:
                        email_address = re.findall('"email":"(?s)(.*)","address"', content)[0]
                    except:
                        email_address = None

        try:
            location_url = contact_block.find('img', {"class": "attractions-attraction-review-location-StaticMap__map--3_EAL"}).get('src')

            parsed = urlparse(location_url)
            location = parse_qs(parsed.query)['center'][0].split(',')
            latitude = location[0]
            longitude = location[1]
        except:
            latitude = None
            longitude = None

        ########################################################################################################################
        
        popular_mentions = []

        try:
            review_filter_block = soup.find('div', {"class": "location-review-review-list-parts-SearchFilter__button_wrap--2l_Kd"})

            mentions = review_filter_block.find_all('button', {"class": "location-review-review-list-parts-SearchFilter__word_button_secondary--2p0YL"})

            for mention in mentions:
                popular_mentions.append(mention.text.strip())
        except:
            popular_mentions = []

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

        while True:
            browser.execute_script('var elements = document.getElementsByClassName("location-review-review-list-parts-ExpandableReview__ctaLine--24Qlb"); for (var i = 0; i < elements.length; i++) { var element = elements[i]; if (element.innerText == "Read more") { element.click(); } }')
            time.sleep(5)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            review_blocks = soup.find_all('div', {"class": "location-review-card-Card__ui_card--2Mri0 location-review-card-Card__card--o3LVm location-review-card-Card__section--NiAcw"})
            pagination = soup.find('div', {"class": "location-review-pagination-card-PaginationCard__wrapper--3epz_"})
            
            ########################################################################################################################

            for review_block in review_blocks:
                review_index += 1
                reviewer_name = review_block.find('a', {"class": "social-member-event-MemberEventOnObjectBlock__member--35-jC"}).text
                review_title = review_block.find('div', {"class": "location-review-review-list-parts-ReviewTitle__reviewTitle--2GO9Z"}).text
                review_text = review_block.find('q', {"class": "location-review-review-list-parts-ExpandableReview__reviewText--gOmRC"}).text
                
                try:
                    review_date = review_block.find('div', {"class": "social-member-event-MemberEventOnObjectBlock__event_type--3njyv"}).text.replace(reviewer_name + ' wrote a review ','')
                    review_date = datetime.strptime(review_date, "%b %Y").strftime("%b %Y")
                except:
                    review_date = datetime.now().strftime("%b %Y")

                try:
                    trip_type = review_block.find('span', {"class": "location-review-review-list-parts-TripType__trip_type--3w17i"}).text.replace('Trip type: ','')
                except:
                    trip_type = None

                try:
                    checkin_date = review_block.find('span', {"class": "location-review-review-list-parts-EventDate__event_date--1epHa"}).text.replace('Date of experience: ','')
                except:
                    checkin_date = None

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
                    'tip': None,
                    'date': review_date,
                    'trip_type': trip_type,
                    'checkin_date': checkin_date,
                    'stars': stars
                }

                review_list.append(review)

            if review_index == 500:
                break
            
            if not pagination:
                break

            next_button = pagination.find('a', {"class": "ui_button nav next primary"})
            
            if next_button:
                browser.execute_script("document.getElementsByClassName('ui_button nav next primary')[0].click()")
                time.sleep(5)

            next_button_disabled = pagination.find('span', {"class": "ui_button nav next primary disabled"})

            if next_button_disabled:
                break

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