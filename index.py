import requests
from bs4 import BeautifulSoup
hotelname = "Hyatt Regency Kathmandu"
hotelurlname = hotelname.replace(" ", "%20")
hotelsearch = hotelname.replace(" ", "+")
url2 = "https://uk.hotels.com/Hotel-Search?adults=2&d1=2022-12-29&d2=2022-12-30&destination={}&endDate=2022-12-30&latLong=%2C&regionId=null&selected=&semdtl=&sort=RECOMMENDED&startDate=2022-12-29&theme=&useRewards=false&userIntent=".format(hotelurlname)
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36' 
headers= {"User-Agent": user_agent}
print(url2)
ahref = []

aappen = []
r = requests.get(url2, stream=True)
soup = BeautifulSoup(r.text, "html.parser")
    # print(r.text)
# price = soup.find("span", {"data-testid":"price-and-discounted-price"})
# data-stid="property-listing-results"
ale = soup.find_all("div", {"data-stid": "section-results"})
print(ale)

# for item in soup.find_all("div", {"class": "uitk-spacing-margin-blockstart-three"}):
#     if item.find("{}".format(hotelsearch)) != -1 :             
#         aappen.append('{}'.format(item.find("a", {"data-stid": "open-hotel-information", 'href': True})))

# print(aappen)  