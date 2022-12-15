from datetime import time
import pymongo
import uuid
import ssl
import time
import requests

from pymongo import MongoClient
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from flask import Flask, request, flash, redirect, render_template, url_for, jsonify, make_response
from flask_pymongo import PyMongo

app = Flask(__name__)

app.secret_key = 'the random string'
app.config['MONGO_DBNAME'] = 'Hotels'
app.config['MONGO_URI'] = 'mongodb+srv://Kumar:testPassword@testcluster.ndvc4.mongodb.net/test' 
mongo = PyMongo(app)
myclient = pymongo.MongoClient("mongodb+srv://Kumar:testPassword@testcluster.ndvc4.mongodb.net/test", ssl_cert_reqs=ssl.CERT_NONE) # Mine

mydb = myclient["Hotels"] # Creating a database
mycol_result = mydb["Result"] # Creating a collection in the database

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def getServer():
    server = request.args.get('server')
    price = ""
    print("Server: ", server, "was chosen")
    if server == "EU":
        time_start = time.time()
        price = server_EU().split("-")
        print(price)
        price_booking = price[0]
        price_hotels = price[1].replace(".", ",") # Hotels.com for some reason uses "." instead of "," for their prices
        price_expedia = price[2]
        flash(price_hotels, 'hotels')
        flash(price_booking, 'booking')
        flash(price_expedia, 'expedia')

        time_end = time.time()
        print("Time elapsed: ", time_end - time_start, "Server: ", server)
        return redirect(url_for('widget_template'))
    elif server == "US":
        time_start = time.time()
        price = server_US().split("-")
        print(price)
        price_booking = price[0]
        price_hotels = price[1].replace(".", ",") # Hotels.com for some reason uses "." instead of "," for their prices
        price_expedia = price[2]
        flash(price_hotels, 'hotels')
        flash(price_booking, 'booking')
        flash(price_expedia, 'expedia')
        time_end = time.time()
        print("Time elapsed: ", time_end - time_start, "Server: ", server)
        return redirect(url_for('widget_template'))
    elif server == "UK":
        time_start = time.time()
        price = server_UK()
        flash(price)
        time_end = time.time()
        print("Time elapsed: ", time_end - time_start, "Server: ", server)
        return redirect(url_for('widget_template'))
    else:
        return "No Server Selected"


def server_EU(): # Netherlands
    eu_server = "http://20.56.90.161:5678/"
    name = request.args.get('name')
    address = request.args.get('address')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    rooms = request.args.get('rooms')
    if len(rooms) == 0:
        rooms = 1
    adults = request.args.get('adults')
    if len(adults) == 0:
        adults = 1
    children = request.args.get('children')
    if len(children) == 0:
        children = 0
    url_req = eu_server + "?name=" + name + "&address=" + address + "&check_in=" + check_in + "&check_out=" + check_out + "&rooms=" + rooms + "&adults=" + adults + "&children=" + children
    hotel_results = requests.get(url_req)
    
    return hotel_results.text
    

def server_UK(): # United Kingdom
    name = request.args.get('name')
    address = request.args.get('address')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    rooms = request.args.get('rooms')
    adults = request.args.get('adults')
    children = request.args.get('children')
    id = uuid.uuid1()

    options = Options()
    options.add_argument('--headless') # cannot get results on headless
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--log-level=3")  
    options.add_argument('--allow-running-insecure-content')
    driver = Firefox(options=options)           

    driver.get('https://uk.hotels.com/search.do?q-destination='+ name + " " + address) # I need to open a pre search page of a hotel on tripadvisor otherwise I cannot find the element ID
    new_url = driver.current_url.replace("?tab=description&ZSX=0&SYE=3&q-room-0-children=0&q-room-0-adults=2", "")
    new_url += "?q-check-in=" + check_in + "&q-check-out=" + check_out + "&q-rooms=1&q-room-0-adults=" + adults + "&q-room-0-children=" + children
    for childNum in range(int(children)):
        new_url += "&q-room-0-child-" + str(childNum)+ "-age=10"
    driver.get(new_url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        hotel_price = soup.find('span', {'class': '_2R4dw5 _17vI-J'}).text
    except:
        hotel_price = ''
    try:
        hotel_rating = soup.find('span', {'class': '_1biq31 _11XjrQ _1Zann2'}).text
    except:
        try:
            hotel_rating = soup.find('span', {'class': '_1biq31 _2APCnh _1Zann2'}).text
        except:
            hotel_rating = ''
    try:
        hotel_reviews = soup.find('button', {'class': '_1HtKl_'}).get('aria-label').replace("See all ", "")
    except:
        hotel_reviews = ''

    hotel_results = {"_id": id, "name": name, "address": address,"rooms": rooms, "adults": adults, "children": children, "check-in_date": check_in, "check-out_date": check_out, "price": hotel_price, "rating": hotel_rating, "reviews": hotel_reviews}
    #print(hotel_results)
    driver.quit()
    insert_col = mycol_result.insert_one(hotel_results)
    return hotel_price

def server_US(): # United States

    us_server = "http://34.134.137.221:5000"
    server = request.args.get('server')
    name = request.args.get('name')
    address = request.args.get('address')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    rooms = request.args.get('rooms')
    if len(rooms) == 0:
        rooms = 1
    adults = request.args.get('adults')
    if len(adults) == 0:
        adults = 1
    children = request.args.get('children')
    if len(children) == 0:
        children = 0
    url_req = us_server + "?name=" + name + "&address=" + address + "&check_in=" + check_in + "&check_out=" + check_out + "&rooms=" + rooms + "&adults=" + adults + "&children=" + children + "&server=" + server
    hotel_price = requests.get(url_req)
    print(hotel_price)
    
    return hotel_price.text
   


@app.route("/widget_template", methods=['GET', 'POST'])
def widget_template():
    return render_template('main2.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5678)

