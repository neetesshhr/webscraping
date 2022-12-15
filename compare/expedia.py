# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# import datetime
from bs4 import BeautifulSoup
from flask import Flask
import requests

# url = 'https://www.melon.com/mymusic/playlist/mymusicplaylistview_listSong.htm?plylstSeq=473505374'


 
# app = Flask(__name__)

# options = webdriver.ChromeOptions() 

# options.add_argument("start-maximized")
# # options.add_experimental_option("excludeSwitches", ["enable-automation"])
# # options.add_experimental_option('useAutomationExtension', False)
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-sh-usage')
# options.add_argument('--headless') 
# driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
# @app.route("/")
# def gfg():
def expedia_price(adult_string, children_string, check_in, check_out, destination, hotel_name):
    url = "https://www.expedia.co.uk/Hotel-Search?adults={}&children={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(
                adult_string, children_string, check_in, check_out, destination, check_out, hotel_name, check_in
         )
        # driver.get(url)
    r = requests.get(url,headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text,"html.parser")
        # soup = BeautifulSoup(driver.page_source, "html.parser")
        # print(driver.page_source)
    price = soup.find("div", {"class": "uitk-text uitk-type-600 uitk-type-bold uitk-text-emphasis-theme"})
    print(url)
    return price


def expedia_content(adult_string, children_string, check_in, check_out, destination, hotel_name):
    url = "https://www.expedia.co.uk/Hotel-Search?adults={}&children={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(
                adult_string, children_string, check_in, check_out, destination, check_out, hotel_name, check_in
            )
    r = requests.get(url,headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text,"html.parser")
    # content = soup.find("div", {"class": "uitk-card uitk-card-roundcorner-all uitk-card-has-primary-theme"})
    url2 = soup.find("a", {"data-stid": "open-hotel-information", 'href': True})
    url2 = url2['href']
    url2 = "https://www.expedia.co.uk/{}".format(url2)
    r2 = requests.get(url2,headers={"User-Agent":"Mozilla/5.0"}, stream=True)
    # print(url2)
    soup2= BeautifulSoup(r2.text, "html.parser")
    room_content = soup2.find("div", class_ = "uitk-spacing uitk-spacing-margin-blockstart-six uitk-spacing-padding-small-inline-three uitk-spacing-padding-medium-inline-unset")
    print(room_content)
    price = soup.find("div", {"class": "uitk-text uitk-type-600 uitk-type-bold uitk-text-emphasis-theme"})
    content = "<h1> {} </h1> For more <a href='{}'>Click here</a><br/><hr/><h2>The price is </h2>{}".format(room_content, url2, price.text)
    return content


# adult_string = 2
# children_string = 0
# check_in="2022-12-13"
# check_out="2022-12-15"
# destination="Nepal"
# hotel_name="Marriot"
# expedia_content(adult_string=adult_string, children_string=children_string, check_in=check_in, check_out=check_out, hotel_name=hotel_name, destination=destination)


    # <div class="uitk-text uitk-type-600 uitk-type-bold uitk-text-emphasis-theme">£172</div>


    # div class="uitk-card uitk-card-roundcorner-all uitk-card-has-primary-theme" 
    

# if __name__ == '__main__':
#     from waitress import serve

#     serve(app, host='0.0.0.0', port=5678)

