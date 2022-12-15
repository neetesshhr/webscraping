from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import datetime
from bs4 import BeautifulSoup
import requests
import urllib.request
# import urllib3

# options = webdriver.ChromeOptions() 

# options.add_argument("start-maximized")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
headers= {"User-Agent": user_agent}

def bookings_price(check_in, check_out, destination, adults, total_children, num_rooms):

    # url2 = "https://www.booking.com/searchresults.en-gb.html?ss=Hyatt+Regency+Kathmandu&ssne=Nepal&ssne_untouched=Nepal&efdco=1&label=gen173nr-1BCAEoggI46AdIM1gEaKsBiAEBmAEJuAEZyAEM2AEB6AEBiAIBqAIDuAKg1-KcBsACAdICJGUyYjg5NzIzLWNiODUtNDNiNy1iMjQ4LTcyZmU0ZmI3NDAxNtgCBeACAQ&sid=b46a04375703e46584178f363b4bd2https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1FCAEoggI46AdIM1gEaKsBiAEBmAEJuAEZyAEM2AEB6AEB-AELiAIBqAIDuALc2uKcBsACAdICJDlkNmFiNDA2LTkzZDYtNDg1ZC05YzAxLTFmNmU5NDZkNTdkYdgCBuACAQ&lang=en-gb&sid=0028b15b49df734dca79ba302323cc98&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIM1gEaKsBiAEBmAEJuAEZyAEM2AEB6AEB-AELiAIBqAIDuALc2uKcBsACAdICJDlkNmFiNDA2LTkzZDYtNDg1ZC05YzAxLTFmNmU5NDZkNTdkYdgCBuACAQ%26sid%3D0028b15b49df734dca79ba302323cc98%26sb_price_type%3Dtotal%26%26&ss=Hyatt+Regency+Kathmandu%2C+Kathmandu%2C+Kathmandu+Valley%2C+Nepal&is_ski_area=&ssne=London&ssne_untouched=London&checkin_year=2022&checkin_month=12&checkin_monthday=14&checkout_year=2022&checkout_month=12&checkout_monthday=15&efdco=1&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&search_pageview_id=4381766eea700009&ac_suggestion_list_length=5&ac_suggestion_theme_list_length=0&ac_position=0&ac_langcode=en&ac_click_type=b&ac_meta=GhA0MzgxNzY2ZWVhNzAwMDA5IAAoATICZW46BUh5YXR0QABKAFAA&dest_id=706937&dest_type=hotel&place_id_lat=27.719467&place_id_lon=85.354004&search_pageview_id=4381766eea700009&search_selected=true&ss_raw=Hyattca&aid=304142&lang=en-gb&sb=1&src_elem=sb&src=index&dest_id=38456&dest_type=hotel&ac_position=0&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=34647590ac4305f1&ac_meta=GhAzNDY0NzU5MGFjNDMwNWYxIAAoATICZW46DlJlc2lkZW5jZSBJbm4gQABKAFAA&checkin=2022-12-14&checkout=2022-12-17&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure"
    # url3 = "https://www.booking.com/searchresults.en-gb.html?ss=Hotel+Yambu&ssne=Hotel+Yambu&ssne_untouched=Hotel+Yambucheckin=2022-12-21&checkout=2022-12-23"
    url2 = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1FCAEoggI46AdIM1gEaKsBiAEBmAEJuAEZyAEM2AEB6AEB-AELiAIBqAIDuALc2uKcBsACAdICJDlkNmFiNDA2LTkzZDYtNDg1ZC05YzAxLTFmNmU5NDZkNTdkYdgCBuACAQ&lang=en-gb&sid=0028b15b49df734dca79ba302323cc98&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIM1gEaKsBiAEBmAEJuAEZyAEM2AEB6AEB-AELiAIBqAIDuALc2uKcBsACAdICJDlkNmFiNDA2LTkzZDYtNDg1ZC05YzAxLTFmNmU5NDZkNTdkYdgCBuACAQ%26sid%3D0028b15b49df734dca79ba302323cc98%26sb_price_type%3Dtotal%26%26&ss=Hotel+Yambu&is_ski_area=&ssne=Hotel+Yambu&ssne_untouched=Hotel+Yambu&checkin_year=2022&checkin_month=12&checkin_monthday=15&checkout_year=2022&checkout_month=12&checkout_monthday=19&efdco=1&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&search_pageview_id=&ac_suggestion_list_length=&ac_suggestion_theme_list_length=0&ac_position=0&ac_langcode=en&ac_click_type=b&dest_id=&dest_type=hotel&place_id_lat=&place_id_lon=&search_pageview_id=&search_selected=true&ss_raw=Hotel+Yambhu"
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36' 
    headers= {"User-Agent": user_agent}
    r = requests.get(url2, headers=headers, stream=True)
    soup = BeautifulSoup(r.text, "html.parser")
    # print(r.text)
    price = soup.find("span", {"data-testid":"price-and-discounted-price"})
    # price = soup.find("div", {"class":"d20f4628d0"})
    return price

def bookings_content(check_in, check_out, destination, adults, total_children, num_rooms):
    year_in,month_in,day_in = str(check_in).split("-")
    year_out, month_out, day_out = str(check_out).split("-")
    url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&{}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&&selected_currency=EUR&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                    destination,year_in,month_in,day_in,year_out,month_out,day_out,adults,total_children,num_rooms)   
    print(url)
    r = requests.get(url, headers=headers, stream=True)
    soup = BeautifulSoup(r.text, "html.parser")
    url2 = soup.find('a', class_= "e13098a59f", href= True)
    url2 = url2['href']
    print(url2)
    r2 = requests.get(url2, headers=headers, stream=True)
    soup2 = BeautifulSoup(r2.text, "html.parser")
    content = soup2.select("#hprt-table")
    price = soup.find("span", {"data-testid":"price-and-discounted-price"})
    content = "<h1>Room details: </h1><br/>{}<br/>For more <a href='{}'>Click here</a> <hr/> <h2>Price is: </h2> {}".format(content, url2, price.text)
    return content




# https://www.booking.com/index.html?label=gen173nr-1FCAEoggI46AdIM1gEaKsBiAEBmAExuAEZyAEM2AEB6AEB-AECiAIBqAIDuAKau9acBsACAdICJGQyM2NkOTQ1LWRkMzEtNDcwMy04YTUzLTYxN2QxZmJkZWVkN9gCBeACAQ&sid=0028b15b49df734dca79ba302323cc98&sb_price_type=total&changed_currency=1&selected_currency=EUR&top_currency=1

# <div class="uitk-text uitk-type-500 uitk-type-bold uitk-text-default-theme">€&nbsp;102</div>
# https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1FCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQH4AQuIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIG4AIB&sid=0aad5354057ba237ac2cb9fb85bb543b&tmpl=searchresults&checkin_month=12&checkin_monthday=13&checkin_year=2022&checkout_month=12&checkout_monthday=16&checkout_year=2022&class_interval=1&dtdisc=0&from_sf=1&group_adults=2&inac=0&index_postcard=0&label_click=undef&no_rooms=1&offset=0&postcard=0&room1=A%2CA&sb_price_type=total&search_pageview_id=1be740bf37ad0063&shw_aparth=1&slp_r_match=0&src=index&src_elem=sb&srpvid=8c4941037fa900e9&ss=nepal&ss_all=0&ssb=empty&sshis=0&changed_currency=1&selected_currency=EUR&top_currency=1

# destination = "Bali"
# check_in_year = 2022
# check_in_month = 12
# check_in_day = 13
# check_out_year = 2022
# check_out_month = 12
# check_out_day = 17
# adults = 2
# total_children = 0
# num_rooms = 1
# check_in = "{}-{}-{}".format(check_in_year, check_in_month, check_in_day)
# check_out = "{}-{}-{}".format(check_out_year, check_out_month, check_out_day)
# bookings_content(check_in = check_in, check_out=check_out, destination=destination, adults=adults, total_children=total_children, num_rooms=num_rooms)
a = bookings_price("222","22",22,22,22,22)
print(a)