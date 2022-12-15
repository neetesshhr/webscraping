# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# import datetime
from bs4 import BeautifulSoup
import requests




def hotel_price(name, address, rooms, adults_and_children, check_in, check_out):
    url='https://nl.hotels.com/search.do?q-destination={} {}&q-check-in={}&q-check-out={}&q-rooms{}{}'.format(name, address, check_in,check_out, rooms, adults_and_children)
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, stream=True)
    soup = BeautifulSoup(r.text, "html.parser")
    price = soup.find("span", class_="_2R4dw5")
    print(url)
    if price is None:
        price = soup.find("div", {"class": "uitk-text uitk-type-500 uitk-type-bold uitk-text-default-theme"})
    return price

def hotel_content(name, address, rooms, adults_and_children, check_in, check_out):
    url='https://nl.hotels.com/search.do?q-destination={} {}&q-check-in={}&q-check-out={}&q-rooms{}{}'.format(name, address, check_in,check_out, rooms, adults_and_children)
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, stream=True)
    soup = BeautifulSoup(r.text, "html.parser")
    content = soup.find("div", {"class": "_3NQzWW"})
    if content is None:
        content = soup.find("div", {"class": "uitk-card-content-section uitk-card-content-section-padded uitk-spacing uitk-spacing-margin-blockend-three uitk-spacing-padding-inline-six uitk-spacing-padding-block-six uitk-card uitk-card-roundcorner-all uitk-card-has-primary-theme"})
    content_price = soup.find("div", {"class": "uitk-text uitk-type-500 uitk-type-bold uitk-text-default-theme"})
    content_price = content_price.text
    # content_room = soup.find("div", {"class":"uitk-spacing uitk-spacing-margin-blockend-two"})
    content_room = soup.find("div",class_ = "uitk-spacing SimpleContainer")
    content_room = "<h1> The room options available are </h1> <br/> {} <br/> <a href='{}'>Click Here</a> for more details<hr/><br/> <h2>The price is</h2>{}".format(content_room, url,content_price)
    return content_room


# <div class="uitk-text uitk-type-500 uitk-type-bold uitk-text-default-theme">€&nbsp;102</div>
a = hotel_content("Marriot Hotel", "London", 1, 2, "2022-12-13", "2022-12-17")
