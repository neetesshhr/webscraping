from datetime import time
import time
import datetime
import queue
from threading import Thread
from bs4 import BeautifulSoup  # allows us to search website html for prices
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, request
from chromedriver_py import binary_path
import chromedriver_autoinstaller as chromedriver

chromedriver.install()

# from chromedriver_py import binary_path  # wont be needed if you install chromedriver in path

app = Flask(__name__)

app.secret_key = 'the random string'
controller_ip="0.0.0.0"
##controller_ip = "20.90.251.166"# change this if needed to ip of computer housing the controller

current_server = "UK" #change this to what ever country the server your using is in (EU,US,UK)


class select_server:
    def server_EU(self):  # Netherlands
        check_ip = request.remote_addr  # The IP address that the EU web scraper is receiving a request from
        if controller_ip != check_ip:  # Deny request if the IP address of the controller does not match
            return "Access denied (Received query from unauthorised ip address)"
        else:
            time_start = time.time()  # FOR TESTING PURPOSES
            print("Received Request at: " + str(time_start))  # FOR TESTING PURPOSES

            # The details that was received from the controller
            name = request.args.get('name')  # all of these get get the values of values from the request url
            address = request.args.get('address')
            check_in = request.args.get('check_in')
            check_out = request.args.get('check_out')
            rooms = request.args.get('rooms')
            adults = request.args.get('adults')
            children = request.args.get('children')
            debug = request.args.get('debug')#optional
            allocation = request.args.get('allocation')
            if allocation is None:
                room_allocate = None
            else:
                room_allocate = allocation.split(",")
            location = "EU"  # this will change for each of the servers(e.g EU server --> location = "EU"
            all_ages = request.args.get('ages')
            all_ages_backup = all_ages
            ages = []
            if all_ages is not None:
                if "," in all_ages:
                    all_ages = all_ages.split(",")  # splits at , to get list with all the ages in order
                    ages = all_ages
                else:
                    ages.append(all_ages)
            search = {"destination": address, "location": location, "hotel name": name, "check in": check_in,
                      "check out": check_out, "adults": adults, "children": children, "ages": ages,
                      "backup": all_ages_backup, "rooms": rooms,
                      "room allocate": room_allocate}

            def hotels(driver, hello, que, search):  # Hotels
                time_start_hotels = time.time()  # FOR TESTING PURPOSES
                print("Hotels web scraping initiated at: {}".format( str(time_start_hotels)))  # FOR TESTING PURPOSES
                allocating = allocation.split(",")
                list_adults = []
                list_children = []
                adults_and_children = ""

                print(all_ages_backup)
                ages = all_ages_backup.split(",")

                for i in range(len(allocating)):# breaks down allocation parameter to get adults and children in each room
                    list_adults.append(allocating[i].split(".")[0].replace("A", ""))
                    list_children.append(allocating[i].split(".")[1].replace("C", ""))

                child_counter = 0
                for roomNum in range(int(rooms)):
                    adults_and_children += "&q-room-{}-adults={}".format(str(roomNum), list_adults)[
                        roomNum] + "&q-room-{}-children={}".format(str(roomNum), list_children[roomNum])
                    for childNum in range(int(list_children[roomNum])):
                        adults_and_children += "&q-room-{}-child{}-age={}".format(str(roomNum), str(childNum), ages[child_counter]) 
                        child_counter += 1

                driver.get(
                    'https://nl.hotels.com/search.do?q-destination={}{}&q-check-in={}&q-check-out={}&q-rooms{}{}'.format(name, address, check_in,check_out, rooms, adults_and_children))

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                try:# hotels.com price locators on the page
                    hotel_price = soup.find('span', {'class': '_2R4dw5'}).text
                except AttributeError:
                    hotel_price = soup.find('span', {'class': '_2R4dw5'}).text
                # Looking for the price in hotel

                driver.quit()  # Close the web browser

                time_end_hotels = time.time()  # FOR TESTING PURPOSES
                time_taken_hotels = time_end_hotels - time_start_hotels  # FOR TESTING PURPOSES
                time_taken_hotels = " Time taken: " + str(time_taken_hotels)  # FOR TESTING PURPOSES
                que.put({"Hotels": hotel_price + time_taken_hotels})  # FOR TESTING PURPOSES
                # que.put({"Hotels": hotel_price}) # Original
                return hotel_price  # returns hotel price

            def booking_com(driver, apple, que, search):  # function for scraping booking.com
                time_start_booking = time.time()



                def get_search_details(search):

                    destination, location, check_in, check_out, adults, children, num_rooms, ages, ages_string = search[
                                                                                                                     "hotel name"] + " " + \
                                                                                                                 search[
                                                                                                                     "destination"], \
                                                                                                                 search[
                                                                                                                     "location"], \
                                                                                                                 search[
                                                                                                                     "check in"], \
                                                                                                                 search[
                                                                                                                     "check out"], \
                                                                                                                 search[
                                                                                                                     "adults"], \
                                                                                                                 search[
                                                                                                                     "children"], \
                                                                                                                 search[
                                                                                                                     "rooms"], \
                                                                                                                 search[
                                                                                                                     "ages"], \
                                                                                                                 search[
                                                                                                                     "backup"]  # gets the values from dictionary
                    year_in, month_in, day_in = check_in.split(
                        "-")  # splits date (e.g 2021-09-21) into year(2021), month(09) and day(21)
                    check_in_day = day_in
                    check_in_month = month_in
                    check_in_year = year_in
                    year_out, month_out, day_out = check_out.split("-")
                    check_out_day = day_out
                    check_out_month = month_out
                    check_out_year = year_out
                    ages = []
                    if ages_string is not None:# splits string to put all ages into a list
                        if "," in ages_string:
                            all_ages = ages_string.split(",")  # splits at , to get list with all the ages in order
                            ages = all_ages
                        else:
                            ages.append(ages_string)
                    child_age = ages
                    total_children = "group_children=" + str(children)  # creates part of url for children
                    if children == "" or int(children) == 0:
                        children = 0
                    else:
                        for i in range(len(child_age)):
                            temp = child_age[i]
                            temp = str(temp)
                            total_children += "&age=" + temp
                    children = 2
                    children = int(children)
                    if (children) > 0:
                        url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&{}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                destination, check_in_year, check_in_month, check_in_day, check_out_year, check_out_month, check_out_day, adults, total_children, num_rooms
                              )
                    else:
                        url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&group_children={}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                destination, check_in_year, check_in_month, check_in_day, check_out_year, check_out_month, check_out_day, adults, total_children, children, num_rooms

                              )
                    driver.get(url)  # opens link in web browser

                def main2(search):
                    get_search_details(search)
                    print('the source adderrresss is  {}'.format(driver.page_source))
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    # locator for prices on booking.com
                    price = soup.find("div", {"class": "bui-price-display__value prco-inline-block-maker-helper"})
                    if price is None:
                        price = soup.find("span", {"class": "b2e4e409fd _2de857cfd1"})
                    print(price.text)
                    price = price.text.strip()
                    driver.quit()
                    return price


                room_info = main2(search)
                time_end_booking = time.time()
                time_taken_booking = time_end_booking - time_start_booking
                time_taken_booking = " Time taken: " + str(time_taken_booking)

                que.put({"Booking": room_info + time_taken_booking})  # adds result to result queue

            def expedia(driver, apple, que, search):  # function for scraping expedia
                time_start_expedia = time.time()



                def get_search_details(search):

                    destination, location, hotel_name, check_in, check_out, adults, children, rooms, ages, room_allocate = \
                        search[
                            "destination"], \
                        search[
                            "location"], \
                        search[
                            "hotel name"], \
                        search[
                            "check in"], \
                        search[
                            "check out"], \
                        search[
                            "adults"], \
                        search[
                            "children"], \
                        search[
                            "rooms"], \
                        search[
                            "ages"], search["room allocate"]  # gets the values from dictionary

                    child_age = ages
                    total_children = ""
                    if room_allocate is None:# will only happen if there is only 1 room
                        total_children = "children="  # creates part of url for children
                        if children == "":
                            children = 0
                        else:
                            for i in range(len(child_age)):
                                if i == 0:
                                    total_children += "1_" + child_age[0]
                                else:
                                    total_children += "%2C1_" + child_age[i]
                    adult_string = ""
                    children_string = ""
                    if room_allocate is None:
                        adult_string = str(adults)
                    else:
                        if len(room_allocate) > 1:  # need to add another else
                            if "." in room_allocate[0]:
                                first_room = room_allocate[0].split(".")
                                adult_string += str(first_room[0].replace("A", ""))
                                child_num = int(first_room[1].replace("C", ""))
                                for i in range(child_num):
                                    if i == 0:
                                        children_string += "1_" + child_age[i]
                                        child_age.remove(child_age[i])
                                    else:
                                        children_string += "%2C1_" + child_age[i - 1]
                                        child_age.remove(child_age[i - 1])
                                for i in range(1, len(room_allocate)):
                                    if "." in room_allocate[i]:
                                        current_room = room_allocate[i].split(".")
                                        adult_string += "%2C" + str(current_room[0].replace("A", ""))
                                        child_num = int(current_room[1].replace("C", ""))
                                        for j in range(child_num):
                                            children_string += f"%2C{i + 1}_" + child_age[j]
                                            child_age.remove(child_age[j])
                                    else:
                                        adult_string += "%2C" + str(room_allocate[i].replace("A", ""))

                            else:
                                adult_string += "%2C" + str(room_allocate[0].replace("A", ""))


                        else:
                            if "." in room_allocate[0]:
                                first_room = room_allocate[0].split(".")
                                adult_string += str(first_room[0].replace("A", ""))
                                child_num = int(first_room[1].replace("C", ""))
                                for i in range(child_num):
                                    if i == 0:
                                        children_string += "1_" + child_age[0]
                                    else:
                                        children_string += "%2C1_" + child_age[i]
                    children =2 
                    children = int(children)
                    if (children) > 0:
                        if total_children == "":
                            url = "https://www.expedia.co.uk/Hotel-Search?adults={}&children={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, children_string, check_in, check_in, destination, check_out, hotel_name, check_in)
                        else:
                            url = "https://www.expedia.co.uk/Hotel-Search?adults={}&{}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, total_children, check_in, check_in, destination, check_out, hotel_name, check_in)
                    else:
                        url = "https://www.expedia.co.uk/Hotel-Search?adults={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, check_in, check_in, destination, check_out, hotel_name, check_in)

                    url_ending = "euro.expedia.net"  # we want UK prices so we change .co.uk to .co.uk
                    url = url.replace("www.expedia.co.uk", url_ending)
                    print(url)
                    driver.get(url)  # opens link in web browser

                def main2(search):
                    get_search_details(search)
                    print('the source adderrresss is  {}'.format(driver.page_source))
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    price = ""
                    # locator for price on expedia
                    price = soup.find("div", {"class": "uitk-type-600 uitk-type-bold"})
                    if price is None:
                        price = soup.find("span", {"data-stid": "price-lockup-text"})
                        if price is None:
                            price = ""
                        else:
                            price = price.text
                    elif price is not None:
                        price = price.text
                    else:
                        price = ""

                    driver.quit()
                    return price

                room_info = main2(search)
                time_end_expedia = time.time()
                time_taken_expedia = time_end_expedia - time_start_expedia
                time_taken_expedia = " Time taken: " + str(time_taken_expedia)
                que.put({"Expedia": room_info + time_taken_expedia})  # adds result to result queue

            # print(user_agent)
            options = Options()
            options.add_argument('--headless')  # cannot get results on headless
            options.add_argument('--disable-gpu')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument("--proxy-server='direct://'")
            options.add_argument("--proxy-bypass-list=*")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--log-level=3")
            options.add_argument('--allow-running-insecure-content')
            options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            # options.binary_location = '/Applications/Google Chrome   Canary.app/Contents/MacOS/Google Chrome Canary'`

            driver1 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
            driver2 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
            driver3 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))

            que = queue.Queue()

            thread_list = list()
            browserThread = Thread(target=expedia, args=(driver1, 'https://www.google.com', que, search))
            thread_list.append(browserThread)
            browserThread2 = Thread(target=hotels, args=(driver2, 'https://www.google.com', que, search))
            thread_list.append(browserThread2)
            browserThread3 = Thread(target=booking_com, args=(driver3, 'https://www.google.com', que, search))
            thread_list.append(browserThread3)
            browserThread.start()
            browserThread2.start()
            browserThread3.start()
            for t in thread_list:
                t.join()

            booking_price = ""
            hotels_price = ""
            expedia_price = ""

            for item in que.queue:
                for key, value in item.items():
                    if key == "Booking":
                        # booking_price = value
                        booking_price = key + " " + value
                    if key == "Hotels":
                        # hotels_price = value
                        hotels_price = key + " " + value
                    if key == "Expedia":
                        # expedia_price = value
                        expedia_price = key + " " + value

            if hotels_price == "":
                hotels_price = "Hotels: N/A"
            if booking_price == "":
                booking_price = "Booking: N/A"
            if expedia_price == "":
                expedia_price = "Expedia: N/A"

            all_price = booking_price + "-" + hotels_price + "-" + expedia_price
            time_end = time.time()
            total_time = " Total Time elapsed: ", time_end - time_start
            all_price_and_time = str(all_price) + " " + str(total_time)
            print(all_price_and_time)
            return all_price_and_time  # This will return to the controller

    def server_US(self):  # United Kingdom
        check_ip = request.remote_addr  # gets the ip of the device sending the request
        ip_validation = False
        if ip_validation == True:  # only needed for testing as you wont need this unless making changes
            if controller_ip != check_ip:
                return "Access Denied"
            else:
                name = request.args.get('name')  # all of these get get the values of values from the request url
                address = request.args.get('address')
                check_in = request.args.get('check_in')
                check_out = request.args.get('check_out')
                rooms = request.args.get('rooms')
                adults = request.args.get('adults')
                children = request.args.get('children')
                debug = request.args.get('debug')
                allocation = request.args.get('allocation')
                if allocation is None:  # should only be used if rooms > 1 so we can specify which room every person is in
                    room_allocate = None
                else:
                    room_allocate = allocation.split(",")
                location = "US"  # this will change for each of the servers(e.g EU server --> location = "EU"
                all_ages = request.args.get(
                    'ages')  # ages in request url should be like "ages=4,5,6" where 4 is the age of the first child for example
                all_ages_backup = all_ages
                ages = []
                if all_ages is not None:
                    if "," in all_ages:
                        all_ages = all_ages.split(",")  # splits at , to get list with all the ages in order
                        ages = all_ages
                    else:
                        ages.append(all_ages)
                search = {"destination": address, "location": location, "hotel name": name, "check in": check_in,
                          "check out": check_out, "adults": adults, "children": children, "ages": ages,
                          "backup": all_ages_backup, "rooms": rooms,
                          "room allocate": room_allocate}  # dictionary with search details that is passed to other functions
                time_start = time.time()  # this is just to test time taken to finish, can remove later

                def hotels(driver, hello, que, search):  # Hotels
                    time_start_hotels = time.time()  # FOR TESTING PURPOSES
                    print("Hotels web scraping initiated at: " + str(time_start_hotels))  # FOR TESTING PURPOSES
                    allocating = allocation.split(",")
                    list_adults = []
                    list_children = []
                    adults_and_children = ""

                    print(all_ages_backup)
                    ages = all_ages_backup.split(",")
                    for i in range(len(allocating)):
                        list_adults.append(allocating[i].split(".")[0].replace("A", ""))
                        list_children.append(allocating[i].split(".")[1].replace("C", ""))

                    child_counter = 0
                    for roomNum in range(int(rooms)):
                        adults_and_children += "&q-room-" + str(roomNum) + "-adults=" + list_adults[
                            roomNum] + "&q-room-" + str(roomNum) + "-children=" + list_children[roomNum]
                        for childNum in range(int(list_children[roomNum])):
                            adults_and_children += "&q-room-" + str(roomNum) + "-child-" + str(childNum) + "-age=" + \
                                                   ages[
                                                       child_counter]
                            child_counter += 1

                    # print("list of adults: ", list_adults)
                    # print("list of children: ", list_children)
                    # print(adults_and_children)
                    # url for EU

                    driver.get(
                        'https://nl.hotels.com/search.do?q-destination={} {}&q-check-in={}&q-check-out={}&q-rooms{}{}'.format(name, address, check_in,check_out, rooms, adults_and_children))
                    new_url = driver.current_url
                    new_url += "&pos=HCOM_US&locale=en_US"
                    driver.get(new_url)
                    final_url = driver.current_url.split(".hotels")
                    final_url[0] = "https://"
                    final_url = "hotels".join(final_url)
                    driver.get(final_url)

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    check_in_day = int(check_in.split("-")[
                                           2])  # these parts are to find out if the duration of the stay = 1 as the price is located differently
                    check_in_month = int(
                        check_in.split("-")[1])  # on the page compared to if the duration of the stay > 1
                    check_in_year = int(check_in.split("-")[0])
                    check_in_date = datetime.date(check_in_year, check_in_month, check_in_day)

                    check_out_day = int(check_out.split("-")[2])
                    check_out_month = int(check_out.split("-")[1])
                    check_out_year = int(check_out.split("-")[0])
                    check_out_date = datetime.date(check_out_year, check_out_month, check_out_day)

                    check_date = check_out_date - check_in_date
                    print(check_date.days)
                    # Looking for the price in hotel
                    if check_date.days == 1:
                        try:
                            hotel_price = soup.find('span', {'class': '_2R4dw5'}).text
                        except:
                            hotel_price = ''
                    else:
                        try:
                            hotel_price = soup.find('span', {'class': 'CaUeSb'}).text.split()[1]
                            print(hotel_price)
                        except:
                            hotel_price = ''

                    driver.quit()  # Close the web browser
                    time_end_hotels = time.time()  # FOR TESTING PURPOSES
                    time_taken_hotels = time_end_hotels - time_start_hotels  # FOR TESTING PURPOSES
                    time_taken_hotels = " Time taken: " + str(time_taken_hotels)  # FOR TESTING PURPOSES
                    que.put({"Hotels": hotel_price + time_taken_hotels})  # FOR TESTING PURPOSES
                    # que.put({"Hotels": hotel_price}) # Original
                    return hotel_price  # returns hotel price

                def booking_com(driver, apple, que, search):  # function for scraping booking.com
                    time_start_booking = time.time()



                    def get_search_details(search):

                        destination, location, check_in, check_out, adults, children, num_rooms, ages, ages_string = \
                        search[
                            "hotel name"] + " " + \
                        search[
                            "destination"], \
                        search[
                            "location"], \
                        search[
                            "check in"], \
                        search[
                            "check out"], \
                        search[
                            "adults"], \
                        search[
                            "children"], \
                        search[
                            "rooms"], \
                        search[
                            "ages"], \
                        search[
                            "backup"]  # gets the values from dictionary
                        year_in, month_in, day_in = check_in.split(
                            "-")  # splits date (e.g 2021-09-21) into year(2021), month(09) and day(21)
                        check_in_day = day_in
                        check_in_month = month_in
                        check_in_year = year_in
                        year_out, month_out, day_out = check_out.split("-")
                        check_out_day = day_out
                        check_out_month = month_out
                        check_out_year = year_out
                        ages = []
                        if ages_string is not None:
                            if "," in ages_string:
                                all_ages = ages_string.split(",")  # splits at , to get list with all the ages in order
                                ages = all_ages
                            else:
                                ages.append(ages_string)
                        child_age = ages
                        total_children = "group_children=" + str(children)  # creates part of url for children
                        if children == "" or int(children) == 0:
                            children = 0
                        else:
                            for i in range(len(child_age)):
                                temp = child_age[i]
                                temp = str(temp)
                                total_children += "&age=" + temp
                        children = 2
                        children = int(children)
                        if (children) > 0:
                            url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&{}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                       destination, check_in_year, check_in_month, check_in_day, check_out_year,check_out_month,check_out_day,adults,total_children,num_rooms
                                  )
                        else:
                            url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&group_children={}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                        destination,check_in_year,check_in_month,check_in_day,check_out_year, check_out_month,check_out_day,adults,children,num_rooms
                                  )
                        driver.get(url)  # opens link in web browser

                    def main2(search):
                        get_search_details(search)
                        print('the source adderrresss is  {}'.format(driver.page_source))
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        # locator for prices on booking.com
                        price = soup.find("div", {"class": "bui-price-display__value prco-inline-block-maker-helper"})
                        if price is None:
                            price = soup.find("span", {"class": "b2e4e409fd _2de857cfd1"})
                        print(price.text)
                        price = price.text.strip()
                        driver.quit()
                        return price

                    room_info = main2(search)
                    time_end_booking = time.time()
                    time_taken_booking = time_end_booking - time_start_booking
                    time_taken_booking = " Time taken: " + str(time_taken_booking)

                    que.put({"Booking": room_info + time_taken_booking})  # adds result to result queue

                def expedia(driver, apple, que, search):  # function for scraping expedia.com
                    time_start_expedia = time.time()



                    def get_search_details(search):

                        destination, location, hotel_name, check_in, check_out, adults, children, rooms, ages, room_allocate = \
                            search[
                                "destination"], \
                            search[
                                "location"], \
                            search[
                                "hotel name"], \
                            search[
                                "check in"], \
                            search[
                                "check out"], \
                            search[
                                "adults"], \
                            search[
                                "children"], \
                            search[
                                "rooms"], \
                            search[
                                "ages"], search["room allocate"]  # gets the values from dictionary

                        child_age = ages
                        total_children = ""
                        if room_allocate is None:
                            total_children = "children="  # creates part of url for children
                            if children == "":
                                children = 0
                            else:
                                for i in range(len(child_age)):
                                    if i == 0:
                                        total_children += "1_" + child_age[0]
                                    else:
                                        total_children += "%2C1_" + child_age[i]
                        adult_string = ""
                        children_string = ""
                        if room_allocate is None:
                            adult_string = str(adults)
                        else:
                            if len(room_allocate) > 1:  # need to add another else
                                if "." in room_allocate[0]:
                                    first_room = room_allocate[0].split(".")
                                    adult_string += str(first_room[0].replace("A", ""))
                                    child_num = int(first_room[1].replace("C", ""))
                                    for i in range(child_num):
                                        if i == 0:
                                            children_string += "1_" + child_age[i]
                                            child_age.remove(child_age[i])
                                        else:
                                            children_string += "%2C1_" + child_age[i - 1]
                                            child_age.remove(child_age[i - 1])
                                    for i in range(1, len(room_allocate)):
                                        if "." in room_allocate[i]:
                                            current_room = room_allocate[i].split(".")
                                            adult_string += "%2C" + str(current_room[0].replace("A", ""))
                                            child_num = int(current_room[1].replace("C", ""))
                                            for j in range(child_num):
                                                children_string += f"%2C{i + 1}_" + child_age[j]
                                                child_age.remove(child_age[j])
                                        else:
                                            adult_string += "%2C" + str(room_allocate[i].replace("A", ""))

                                else:
                                    adult_string += "%2C" + str(room_allocate[0].replace("A", ""))


                            else:
                                if "." in room_allocate[0]:
                                    first_room = room_allocate[0].split(".")
                                    adult_string += str(first_room[0].replace("A", ""))
                                    child_num = int(first_room[1].replace("C", ""))
                                    for i in range(child_num):
                                        if i == 0:
                                            children_string += "1_" + child_age[0]
                                        else:
                                            children_string += "%2C1_" + child_age[i]
                        children =2
                        children = int(children)
                        if (children) > 0:
                            if total_children == "":
                                url = "https://www.expedia.co.uk/Hotel-Search?adults={}&children={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, children_string, check_in, check_in, destination, check_out, hotel_name, check_in)
                            else:
                                url = "https://www.expedia.co.uk/Hotel-Search?adults={}&{}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, total_children, check_in, check_in, destination, check_out, hotel_name, check_in)
                        else:
                            url = "https://www.expedia.co.uk/Hotel-Search?adults={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, check_in, check_in, destination, check_out, hotel_name, check_in)

                        url_ending = "www.expedia.com"  # we want US prices so we change .co.uk to .com
                        url = url.replace("www.expedia.co.uk", url_ending)
                        print(url)
                        driver.get(url)  # opens link in web browser


                    def main2(search):
                        get_search_details(search)
                        print('the source adderrresss is  {}'.format(driver.page_source))
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        price = ""
                        # locator for price on expedia
                        price = soup.find("div",
                                          {"class": "uitk-cell pwa-theme--grey-700 uitk-type-100 uitk-type-bold"})
                        if price is None:
                            price = "None"
                        else:
                            price = price.text.split(" ", 1)
                            print(price[0])
                            price = price[0]

                        driver.quit()
                        return price

                    room_info = main2(search)
                    time_end_expedia = time.time()
                    time_taken_expedia = time_end_expedia - time_start_expedia
                    time_taken_expedia = " Time taken: " + str(time_taken_expedia)
                    que.put({"Expedia": room_info + time_taken_expedia})  # adds result to result queue

                options = Options()
                # need to change user agent if using headless or else you will get blocked
                options.add_argument('--headless')  # headless option
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--no-sandbox')
                options.add_argument("--proxy-server='direct://'")
                options.add_argument("--proxy-bypass-list=*")
                options.add_argument('--ignore-certificate-errors')
                options.add_argument("--log-level=3")
                options.add_argument('--allow-running-insecure-content')
                options.add_argument(
                    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")  # user agent
                options.add_argument('--disable-software-rasterizer')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)                
                driver1 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
                driver2 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
                driver3 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install())) # browser for booking.com
                que = queue.Queue()
                thread_list = list()  # threads that allow all functions to run in parallel instead of sequentially
                browserThread = Thread(target=expedia, args=(driver1, 'https://www.google.com', que, search))
                thread_list.append(browserThread)
                browserThread2 = Thread(target=hotels, args=(driver2, 'https://www.google.com', que, search))
                thread_list.append(browserThread2)
                browserThread3 = Thread(target=booking_com, args=(driver3, 'https://www.google.com', que, search))
                thread_list.append(browserThread3)
                browserThread.start()  # start threads
                browserThread2.start()
                browserThread3.start()
                for t in thread_list:
                    t.join()

                booking_price = ""
                hotels_price = ""
                expedia_price = ""

                for item in que.queue:
                    for key, value in item.items():
                        if key == "Booking":
                            # booking_price = value
                            booking_price = key + " " + value
                        if key == "Hotels":
                            # hotels_price = value
                            hotels_price = key + " " + value
                        if key == "Expedia":
                            # expedia_price = value
                            expedia_price = key + " " + value

                if hotels_price == "":  # if prices werent found for any of the websites then "N/A" is returned for that website
                    hotels_price = "Hotels: N/A"
                if booking_price == "":
                    booking_price = "Booking: N/A"
                if expedia_price == "":
                    expedia_price = "Expedia: N/A"

                all_price = booking_price + "-" + hotels_price + "-" + expedia_price
                time_end = time.time()
                total_time = " Total Time elapsed: ", time_end - time_start
                all_price_and_time = str(all_price) + " " + str(total_time)
                print(all_price_and_time)
                return all_price_and_time  # This will return to the controller

        else:
            name = request.args.get('name')  # all of these get get the values of values from the request url
            address = request.args.get('address')
            check_in = request.args.get('check_in')
            check_out = request.args.get('check_out')
            rooms = request.args.get('rooms')
            adults = request.args.get('adults')
            children = request.args.get('children')
            debug = request.args.get('debug')
            allocation = request.args.get('allocation')
            if allocation is None:
                room_allocate = None
            else:
                room_allocate = allocation.split(",")
            location = "US"  # this will change for each of the servers(e.g EU server --> location = "EU"
            all_ages = request.args.get('ages')
            all_ages_backup = all_ages
            ages = []
            if all_ages is not None:
                if "," in all_ages:
                    all_ages = all_ages.split(",")  # splits at , to get list with all the ages in order
                    ages = all_ages
                else:
                    ages.append(all_ages)
            search = {"destination": address, "location": location, "hotel name": name, "check in": check_in,
                      "check out": check_out, "adults": adults, "children": children, "ages": ages,
                      "backup": all_ages_backup, "rooms": rooms,
                      "room allocate": room_allocate}  # dictionary with search details that is passed to other functions
            time_start = time.time()  # this is just to test time taken to finish, can remove later

            def hotels(driver, hello, que, search):  # Hotels
                time_start_hotels = time.time()  # FOR TESTING PURPOSES
                print("Hotels web scraping initiated at: " + str(time_start_hotels))  # FOR TESTING PURPOSES
                allocating = allocation.split(",")
                list_adults = []
                list_children = []
                adults_and_children = ""

                for i in range(len(allocating)):
                    list_adults.append(allocating[i].split(".")[0].replace("A", ""))
                    list_children.append(allocating[i].split(".")[1].replace("C", ""))

                child_counter = 0
                print(all_ages_backup)
                ages = all_ages_backup.split(",")
                print(ages)
                for roomNum in range(int(rooms)):
                    adults_and_children += "&q-room-" + str(roomNum) + "-adults=" + list_adults[
                        roomNum] + "&q-room-" + str(roomNum) + "-children=" + list_children[roomNum]
                    for childNum in range(int(list_children[roomNum])):
                        adults_and_children += "&q-room-" + str(roomNum) + "-child-" + str(childNum) + "-age=" + \
                                               ages[child_counter]
                        child_counter += 1

                # print("list of adults: ", list_adults)
                # print("list of children: ", list_children)
                # print(adults_and_children)
                # url for US

                driver.get(
                    'https://nl.hotels.com/search.do?q-destination={} {}&q-check-in={}&q-check-out={}&q-rooms{}{}'.format(name, address, check_in,check_out, rooms, adults_and_children))
                new_url = driver.current_url
                new_url += "&pos=HCOM_US&locale=en_US"
                driver.get(new_url)
                final_url = driver.current_url.split(".hotels")
                final_url[0] = "https://"
                final_url = "hotels".join(final_url)
                driver.get(final_url)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                check_in_day = int(check_in.split("-")[
                                       2])  # these parts are to find out if the duration of the stay = 1 as the price is located differently
                check_in_month = int(
                    check_in.split("-")[1])  # on the page compared to if the duration of the stay > 1
                check_in_year = int(check_in.split("-")[0])
                check_in_date = datetime.date(check_in_year, check_in_month, check_in_day)

                check_out_day = int(check_out.split("-")[2])
                check_out_month = int(check_out.split("-")[1])
                check_out_year = int(check_out.split("-")[0])
                check_out_date = datetime.date(check_out_year, check_out_month, check_out_day)

                check_date = check_out_date - check_in_date
                print(check_date.days)
                # Looking for the price in hotel
                if check_date.days == 1:
                    try:
                        hotel_price = soup.find('span', {'class': '_2R4dw5'}).text
                    except:
                        hotel_price = ''
                else:
                    try:
                        hotel_price = soup.find('span', {'class': 'CaUeSb'}).text.split()[1]
                        print(hotel_price)
                    except:
                        hotel_price = ''

                driver.quit()  # Close the web browser
                time_end_hotels = time.time()  # FOR TESTING PURPOSES
                time_taken_hotels = time_end_hotels - time_start_hotels  # FOR TESTING PURPOSES
                time_taken_hotels = " Time taken: " + str(time_taken_hotels)  # FOR TESTING PURPOSES
                que.put({"Hotels": hotel_price + time_taken_hotels})  # FOR TESTING PURPOSES
                # que.put({"Hotels": hotel_price}) # Original
                return hotel_price  # returns hotel price

            def booking_com(driver, apple, que, search):  # function for scraping booking.com
                time_start_booking = time.time()



                def get_search_details(search):

                    destination, location, check_in, check_out, adults, children, num_rooms, ages, ages_string = search[
                                                                                                                     "hotel name"] + " " + \
                                                                                                                 search[
                                                                                                                     "destination"], \
                                                                                                                 search[
                                                                                                                     "location"], \
                                                                                                                 search[
                                                                                                                     "check in"], \
                                                                                                                 search[
                                                                                                                     "check out"], \
                                                                                                                 search[
                                                                                                                     "adults"], \
                                                                                                                 search[
                                                                                                                     "children"], \
                                                                                                                 search[
                                                                                                                     "rooms"], \
                                                                                                                 search[
                                                                                                                     "ages"], \
                                                                                                                 search[
                                                                                                                     "backup"]  # gets the values from dictionary
                    year_in, month_in, day_in = check_in.split(
                        "-")  # splits date (e.g 2021-09-21) into year(2021), month(09) and day(21)
                    check_in_day = day_in
                    check_in_month = month_in
                    check_in_year = year_in
                    year_out, month_out, day_out = check_out.split("-")
                    check_out_day = day_out
                    check_out_month = month_out
                    check_out_year = year_out
                    ages = []
                    if ages_string is not None:
                        if "," in ages_string:
                            all_ages = ages_string.split(",")  # splits at , to get list with all the ages in order
                            ages = all_ages
                        else:
                            ages.append(ages_string)
                    child_age = ages
                    total_children = "group_children=" + str(children)  # creates part of url for children
                    if children == "" or int(children) == 0:
                        children = 0
                    else:
                        for i in range(len(child_age)):
                            temp = child_age[i]
                            temp = str(temp)
                            total_children += "&age=" + temp
                    children =2 
                    children = int(children)
                    if int(children) > 0:
                        url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&{}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                    destination,check_in_year,check_in_month,check_in_day,check_out_year,check_out_month,check_out_day,adults,total_children,num_rooms
                              )
                    else:
                        url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&group_children={}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                    destination,check_in_year,check_in_month,check_in_day,check_out_year,check_out_month,check_out_day,adults,children,num_rooms
                              )
                    driver.get(url)  # opens link in web browser

                def main2(search):
                    get_search_details(search)
                    print('the source adderrresss is  {}'.format(driver.page_source))
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    # locator for prices on booking.com
                    price = soup.find("div", {"class": "bui-price-display__value prco-inline-block-maker-helper"})
                    if price is None:
                        price = soup.find("span", {"class": "b2e4e409fd _2de857cfd1"})
                    print(price.text)
                    price = price.text.strip()
                    driver.quit()
                    return price
                    
                room_info = main2(search)
                time_end_booking = time.time()
                time_taken_booking = time_end_booking - time_start_booking
                time_taken_booking = " Time taken: " + str(time_taken_booking)

                que.put({"Booking": room_info + time_taken_booking})  # adds result to result queue

            def expedia(driver, apple, que, search):  # function for scraping expedia
                time_start_expedia = time.time()



                def get_search_details(search):

                    destination, location, hotel_name, check_in, check_out, adults, children, rooms, ages, room_allocate = \
                        search[
                            "destination"], \
                        search[
                            "location"], \
                        search[
                            "hotel name"], \
                        search[
                            "check in"], \
                        search[
                            "check out"], \
                        search[
                            "adults"], \
                        search[
                            "children"], \
                        search[
                            "rooms"], \
                        search[
                            "ages"], search["room allocate"]  # gets the values from dictionary

                    child_age = ages
                    total_children = ""
                    if room_allocate is None:
                        total_children = "children="  # creates part of url for children
                        if children == "":
                            children = 0
                        else:
                            for i in range(len(child_age)):
                                if i == 0:
                                    total_children += "1_" + child_age[0]
                                else:
                                    total_children += "%2C1_" + child_age[i]
                    adult_string = ""
                    children_string = ""
                    if room_allocate is None:
                        adult_string = str(adults)
                    else:
                        if len(room_allocate) > 1:  # need to add another else
                            if "." in room_allocate[0]:
                                first_room = room_allocate[0].split(".")
                                adult_string += str(first_room[0].replace("A", ""))
                                child_num = int(first_room[1].replace("C", ""))
                                for i in range(child_num):
                                    if i == 0:
                                        children_string += "1_" + child_age[i]
                                        child_age.remove(child_age[i])
                                    else:
                                        children_string += "%2C1_" + child_age[i - 1]
                                        child_age.remove(child_age[i - 1])
                                for i in range(1, len(room_allocate)):
                                    if "." in room_allocate[i]:
                                        current_room = room_allocate[i].split(".")
                                        adult_string += "%2C" + str(current_room[0].replace("A", ""))
                                        child_num = int(current_room[1].replace("C", ""))
                                        for j in range(child_num):
                                            children_string += f"%2C{i + 1}_" + child_age[j]
                                            child_age.remove(child_age[j])
                                    else:
                                        adult_string += "%2C" + str(room_allocate[i].replace("A", ""))

                            else:
                                adult_string += "%2C" + str(room_allocate[0].replace("A", ""))


                        else:
                            if "." in room_allocate[0]:
                                first_room = room_allocate[0].split(".")
                                adult_string += str(first_room[0].replace("A", ""))
                                child_num = int(first_room[1].replace("C", ""))
                                for i in range(child_num):
                                    if i == 0:
                                        children_string += "1_" + child_age[0]
                                    else:
                                        children_string += "%2C1_" + child_age[i]
                    children = 2
                    children = int(children)
                    if (children) > 0:
                        if total_children == "":
                            url = "https://www.expedia.co.uk/Hotel-Search?adults={}&children={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, children_string, check_in, check_in, destination, check_out, hotel_name, check_in)
                        else:
                            url = "https://www.expedia.co.uk/Hotel-Search?adults={}&{}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, total_children, check_in, check_in, destination, check_out, hotel_name, check_in)
                    else:
                        url = "https://www.expedia.co.uk/Hotel-Search?adults={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, check_in, check_in, destination, check_out, hotel_name, check_in)

                    url_ending = "www.expedia.com"  # we want US prices so we change .co.uk to .com
                    url = url.replace("www.expedia.co.uk", url_ending)
                    print(url)
                    driver.get(url)  # opens link in web browser

                def main2(search):
                    get_search_details(search)
                    print('the source adderrresss is  {}'.format(driver.page_source))
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    price = ""
                    # locator for price on expedia
                    price = soup.find("div", {"class": "uitk-cell pwa-theme--grey-700 uitk-type-100 uitk-type-bold"})
                    if price is None:
                        price = "None"
                    else:
                        price = price.text.split(" ", 1)
                        price = price[0]

                    driver.quit()
                    return price

                room_info = main2(search)
                time_end_expedia = time.time()
                time_taken_expedia = time_end_expedia - time_start_expedia
                time_taken_expedia = " Time taken: " + str(time_taken_expedia)
                que.put({"Expedia": room_info + time_taken_expedia})  # adds result to result queue

            options = Options()
            # need to change user agent if using headless or else you will get blocked
            options.add_argument('--headless')  # headless option
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument("--proxy-server='direct://'")
            options.add_argument("--proxy-bypass-list=*")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--log-level=3")
            options.add_argument('--allow-running-insecure-content')
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")  # user agent
            options.add_argument('--disable-software-rasterizer')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            driver1 = webdriver.Chrome(executable_path=binary_path, options=options)  # browser for expedia
            driver2 = webdriver.Chrome(executable_path=binary_path, options=options)  # browser for hotels.com
            driver3 = webdriver.Chrome(executable_path=binary_path, options=options)  # browser for booking.com
            que = queue.Queue()
            thread_list = list()  # threads that allow all functions to run in parallel instead of sequentially
            browserThread = Thread(target=expedia, args=(driver1, 'https://www.google.com', que, search))
            thread_list.append(browserThread)
            browserThread2 = Thread(target=hotels, args=(driver2, 'https://www.google.com', que, search))
            thread_list.append(browserThread2)
            browserThread3 = Thread(target=booking_com, args=(driver3, 'https://www.google.com', que, search))
            thread_list.append(browserThread3)
            browserThread.start()  # start threads
            browserThread2.start()
            browserThread3.start()
            for t in thread_list:
                t.join()

            #
            booking_price = ""
            hotels_price = ""
            expedia_price = ""

            for item in que.queue:
                for key, value in item.items():
                    if key == "Booking":
                        # booking_price = value
                        booking_price = key + " " + value
                    if key == "Hotels":
                        # hotels_price = value
                        hotels_price = key + " " + value
                    if key == "Expedia":
                        # expedia_price = value
                        expedia_price = key + " " + value

            if hotels_price == "":  # if prices werent found for any of the websites then "N/A" is returned for that website
                hotels_price = "Hotels: N/A"
            if booking_price == "":
                booking_price = "Booking: N/A"
            if expedia_price == "":
                expedia_price = "Expedia: N/A"

            all_price = booking_price + "-" + hotels_price + "-" + expedia_price
            time_end = time.time()
            total_time = " Total Time elapsed: ", time_end - time_start
            all_price_and_time = str(all_price) + " " + str(total_time)
            print(all_price_and_time)
            return all_price_and_time  # This will return to the controller

    def server_UK(self):  # United Kingdom
        check_ip = request.remote_addr  # gets the ip of the device sending the request
        ip_validation = False
        if ip_validation == True:  # only needed for testing as you wont need this unless making changes
            if controller_ip != check_ip:
                return "Access Denied"
            else:
                name = request.args.get('name')  # all of these get get the values of values from the request url
                address = request.args.get('address')
                check_in = request.args.get('check_in')
                check_out = request.args.get('check_out')
                rooms = request.args.get('rooms')
                adults = request.args.get('adults')
                children = request.args.get('children')
                debug = request.args.get('debug')
                allocation = request.args.get('allocation')
                if allocation is None:
                    room_allocate = None
                else:
                    room_allocate = allocation.split(",")
                location = "UK"  # this will change for each of the servers(e.g EU server --> location = "EU"
                all_ages = request.args.get('ages')
                all_ages_backup = all_ages
                ages = []
                if all_ages is not None:
                    if "," in all_ages:
                        all_ages = all_ages.split(",")  # splits at , to get list with all the ages in order
                        ages = all_ages
                    else:
                        ages.append(all_ages)
                search = {"destination": address, "location": location, "hotel name": name, "check in": check_in,
                          "check out": check_out, "adults": adults, "children": children, "ages": ages,
                          "backup": all_ages_backup, "rooms": rooms,
                          "room allocate": room_allocate}  # dictionary with search details that is passed to other functions
                time_start = time.time()  # this is just to test time taken to finish, can remove later

                def hotels(driver, hello, que, search):  # Hotels
                    time_start_hotels = time.time()  # FOR TESTING PURPOSES
                    print("Hotels web scraping initiated at: " + str(time_start_hotels))  # FOR TESTING PURPOSES
                    allocating = allocation.split(",")
                    list_adults = []
                    list_children = []
                    adults_and_children = ""

                    print(all_ages_backup)
                    ages = all_ages_backup.split(",")
                    for i in range(len(allocating)):
                        list_adults.append(allocating[i].split(".")[0].replace("A", ""))
                        list_children.append(allocating[i].split(".")[1].replace("C", ""))

                    child_counter = 0
                    for roomNum in range(int(rooms)):
                        adults_and_children += "&q-room-" + str(roomNum) + "-adults=" + list_adults[
                            roomNum] + "&q-room-" + str(
                            roomNum) + "-children=" + list_children[roomNum]
                        for childNum in range(int(list_children[roomNum])):
                            adults_and_children += "&q-room-" + str(roomNum) + "-child-" + str(childNum) + "-age=" + \
                                                   ages[child_counter]
                            child_counter += 1

                    print("list of adults: ", list_adults)
                    print("list of children: ", list_children)
                    print(adults_and_children)
                    # url for UK
                    driver.get(
                        'https://uk.hotels.com/search.do?q-destination={} {}&q-check-in={}&q-check-out={}&q-rooms{}{}'.format(name, address, check_in,check_out, rooms, adults_and_children))
                    new_url = driver.current_url
                    print(new_url)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    try:
                        hotel_price = soup.find('span', {'class': '_2R4dw5'}).text
                    except AttributeError:
                        hotel_price = soup.find('span', {'class': '_2R4dw5'}).text
                    # Looking for the price in hotel

                    driver.quit()  # Close the web browser

                    time_end_hotels = time.time()  # FOR TESTING PURPOSES
                    time_taken_hotels = time_end_hotels - time_start_hotels  # FOR TESTING PURPOSES
                    time_taken_hotels = " Time taken: " + str(time_taken_hotels)  # FOR TESTING PURPOSES
                    que.put({"Hotels": hotel_price + time_taken_hotels})  # FOR TESTING PURPOSES
                    # que.put({"Hotels": hotel_price}) # Original
                    return hotel_price  # returns hotel price

                def booking_com(driver, apple, que, search):  # function for scraping booking.com
                    time_start_booking = time.time()



                    def get_search_details(search):

                        destination, location, check_in, check_out, adults, children, num_rooms, ages, ages_string = \
                        search[
                            "hotel name"] + " " + \
                        search[
                            "destination"], \
                        search[
                            "location"], \
                        search[
                            "check in"], \
                        search[
                            "check out"], \
                        search[
                            "adults"], \
                        search[
                            "children"], \
                        search[
                            "rooms"], \
                        search[
                            "ages"], \
                        search[
                            "backup"]  # gets the values from dictionary
                        year_in, month_in, day_in = check_in.split(
                            "-")  # splits date (e.g 2021-09-21) into year(2021), month(09) and day(21)
                        check_in_day = day_in
                        check_in_month = month_in
                        check_in_year = year_in
                        year_out, month_out, day_out = check_out.split("-")
                        check_out_day = day_out
                        check_out_month = month_out
                        check_out_year = year_out
                        ages = []
                        if ages_string is not None:
                            if "," in ages_string:
                                all_ages = ages_string.split(",")  # splits at , to get list with all the ages in order
                                ages = all_ages
                            else:
                                ages.append(ages_string)
                        child_age = ages
                        total_children = "group_children=" + str(children)  # creates part of url for children
                        if children == "" or int(children) == 0:
                            children = 0
                        else:
                            for i in range(len(child_age)):
                                temp = child_age[i]
                                temp = str(temp)
                                total_children += "&age=" + temp
                        children = 2
                        children = int(children)
                        if (children) > 0:
                            url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&{}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                                destination,check_in_year,check_in_month,check_in_day,check_out_year,check_out_month,check_out_day,adults,total_children,num_rooms
                                  )
                        else:
                            url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&group_children={}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                        destination,check_in_year,check_in_month,check_in_day,check_out_year,check_out_month,check_out_day,adults,children,num_rooms
                                  )
                        driver.get(url)  # opens link in web browser

                    def main2(search):
                        get_search_details(search)
                        print('the source adderrresss is  {}'.format(driver.page_source))
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        # locator for prices on booking.com
                        price = soup.find("div", {"class": "bui-price-display__value prco-inline-block-maker-helper"})
                        if price is None:
                            price = soup.find("span", {"class": "b2e4e409fd _2de857cfd1"})
                        print(price.text)
                        price = price.text.strip()
                        driver.quit()
                        return price

                    room_info = main2(search)
                    time_end_booking = time.time()
                    time_taken_booking = time_end_booking - time_start_booking
                    time_taken_booking = " Time taken: " + str(time_taken_booking)

                    que.put({"Booking": room_info + time_taken_booking})  # adds result to result queue

                def expedia(driver, apple, que, search):  # function for scraping expedia
                    time_start_expedia = time.time()



                    def get_search_details(search):

                        destination, location, hotel_name, check_in, check_out, adults, children, rooms, ages, room_allocate = \
                            search[
                                "destination"], \
                            search[
                                "location"], \
                            search[
                                "hotel name"], \
                            search[
                                "check in"], \
                            search[
                                "check out"], \
                            search[
                                "adults"], \
                            search[
                                "children"], \
                            search[
                                "rooms"], \
                            search[
                                "ages"], search["room allocate"]  # gets the values from dictionary

                        child_age = ages
                        total_children = ""
                        if room_allocate is None:
                            total_children = "children="  # creates part of url for children
                            if children == "":
                                children = 0
                            else:
                                for i in range(len(child_age)):
                                    if i == 0:
                                        total_children += "1_" + child_age[0]
                                    else:
                                        total_children += "%2C1_" + child_age[i]
                        adult_string = ""
                        children_string = ""
                        if room_allocate is None:
                            adult_string = str(adults)
                        else:
                            if len(room_allocate) > 1:  # need to add another else
                                if "." in room_allocate[0]:
                                    first_room = room_allocate[0].split(".")
                                    adult_string += str(first_room[0].replace("A", ""))
                                    child_num = int(first_room[1].replace("C", ""))
                                    for i in range(child_num):
                                        if i == 0:
                                            children_string += "1_" + child_age[i]
                                            child_age.remove(child_age[i])
                                        else:
                                            children_string += "%2C1_" + child_age[i - 1]
                                            child_age.remove(child_age[i - 1])
                                    for i in range(1, len(room_allocate)):
                                        if "." in room_allocate[i]:
                                            current_room = room_allocate[i].split(".")
                                            adult_string += "%2C" + str(current_room[0].replace("A", ""))
                                            child_num = int(current_room[1].replace("C", ""))
                                            for j in range(child_num):
                                                children_string += f"%2C{i + 1}_" + child_age[j]
                                                child_age.remove(child_age[j])
                                        else:
                                            adult_string += "%2C" + str(room_allocate[i].replace("A", ""))

                                else:
                                    adult_string += "%2C" + str(room_allocate[0].replace("A", ""))


                            else:
                                if "." in room_allocate[0]:
                                    first_room = room_allocate[0].split(".")
                                    adult_string += str(first_room[0].replace("A", ""))
                                    child_num = int(first_room[1].replace("C", ""))
                                    for i in range(child_num):
                                        if i == 0:
                                            children_string += "1_" + child_age[0]
                                        else:
                                            children_string += "%2C1_" + child_age[i]
                        children = 2
                        children = int(children)
                        if (children) > 0:
                            if total_children == "":
                                url = "https://www.expedia.co.uk/Hotel-Search?adults={}&children={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, children_string, check_in, check_in, destination, check_out, hotel_name, check_in)
                            else:
                                url = "https://www.expedia.co.uk/Hotel-Search?adults={}&{}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, total_children, check_in, check_in, destination, check_out, hotel_name, check_in)
                        else:
                            url = "https://www.expedia.co.uk/Hotel-Search?adults={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, check_in, check_in, destination, check_out, hotel_name, check_in)

                        url_ending = "www.expedia.co.uk"  # we want UK prices so we change .co.uk to .co.uk
                        url = url.replace("www.expedia.co.uk", url_ending)
                        print(url)
                        driver.get(url)  # opens link in web browser

                    def main2(search):
                        get_search_details(search)
                        print('the source adderrresss is  {}'.format(driver.page_source))
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        price = ""
                        # locator for price on expedia
                        price = soup.find("div", {"class": "uitk-type-600 uitk-type-bold"})
                        if price is None:
                            price = soup.find("span", {"data-stid": "price-lockup-text"})
                            if price is None:
                                price = ""
                            else:
                                price = price.text
                        elif price is not None:
                            price = price.text
                        else:
                            price = ""

                        driver.quit()
                        return price

                    room_info = main2(search)
                    time_end_expedia = time.time()
                    time_taken_expedia = time_end_expedia - time_start_expedia
                    time_taken_expedia = " Time taken: " + str(time_taken_expedia)
                    que.put({"Expedia": room_info + time_taken_expedia})  # adds result to result queue

                options = Options()
                # need to change user agent if using headless or else you will get blocked
                options.add_argument('--headless')  # headless option
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--no-sandbox')
                options.add_argument("--proxy-server='direct://'")
                options.add_argument("--proxy-bypass-list=*")
                options.add_argument('--ignore-certificate-errors')
                options.add_argument("--log-level=3")
                options.add_argument('--allow-running-insecure-content')
                options.add_argument(
                    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")  # user agent
                options.add_argument('--disable-software-rasterizer')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                driver1 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
                driver2 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
                driver3 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install())) # browser for booking.com
                que = queue.Queue()
                thread_list = list()  # threads that allow all functions to run in parallel instead of sequentially
                browserThread = Thread(target=expedia, args=(driver1, 'https://www.google.com', que, search))
                thread_list.append(browserThread)
                browserThread2 = Thread(target=hotels, args=(driver2, 'https://www.google.com', que, search))
                thread_list.append(browserThread2)
                browserThread3 = Thread(target=booking_com, args=(driver3, 'https://www.google.com', que, search))
                thread_list.append(browserThread3)
                browserThread.start()  # start threads
                browserThread2.start()
                browserThread3.start()
                for t in thread_list:
                    t.join()

                booking_price = ""
                hotels_price = ""
                expedia_price = ""

                for item in que.queue:
                    for key, value in item.items():
                        if key == "Booking":
                            # booking_price = value
                            booking_price = key + " " + value
                        if key == "Hotels":
                            # hotels_price = value
                            hotels_price = key + " " + value
                        if key == "Expedia":
                            # expedia_price = value
                            expedia_price = key + " " + value

                if hotels_price == "":  # if prices werent found for any of the websites then "N/A" is returned for that website
                    hotels_price = "Hotels: N/A"
                if booking_price == "":
                    booking_price = "Booking: N/A"
                if expedia_price == "":
                    expedia_price = "Expedia: N/A"

                all_price = booking_price + "-" + hotels_price + "-" + expedia_price
                time_end = time.time()
                total_time = " Total Time elapsed: ", time_end - time_start
                all_price_and_time = str(all_price) + " " + str(total_time)
                print(all_price_and_time)
                return all_price_and_time  # This will return to the controller
        else:
            name = request.args.get('name')  # all of these get get the values of values from the request url
            address = request.args.get('address')
            check_in = request.args.get('check_in')
            check_out = request.args.get('check_out')
            rooms = request.args.get('rooms')
            adults = request.args.get('adults')
            children = request.args.get('children')
            debug = request.args.get('debug')
            allocation = request.args.get('allocation')
            if allocation is None:
                room_allocate = None
            else:
                room_allocate = allocation.split(",")
            location = "UK"  # this will change for each of the servers(e.g EU server --> location = "EU"
            all_ages = request.args.get('ages')
            all_ages_backup = all_ages
            ages = []
            if all_ages is not None:
                if "," in all_ages:
                    all_ages = all_ages.split(",")  # splits at , to get list with all the ages in order
                    ages = all_ages
                else:
                    ages.append(all_ages)
            search = {"destination": address, "location": location, "hotel name": name, "check in": check_in,
                      "check out": check_out, "adults": adults, "children": children, "ages": ages,
                      "backup": all_ages_backup, "rooms": rooms,
                      "room allocate": room_allocate}  # dictionary with search details that is passed to other functions
            time_start = time.time()  # this is just to test time taken to finish, can remove later

            def hotels(driver, hello, que, search):  # Hotels
                time_start_hotels = time.time()  # FOR TESTING PURPOSES
                print("Hotels web scraping initiated at: " + str(time_start_hotels))  # FOR TESTING PURPOSES
                allocating = allocation.split(",")
                list_adults = []
                list_children = []
                adults_and_children = ""

                print(all_ages_backup)
                print("allocating")
                print(allocating)
                ages = all_ages_backup.split(",")
                for i in range(len(allocating)):
                    list_adults.append(allocating[i].split(".")[0].replace("A", ""))
                    list_children.append(allocating[i].split(".")[1].replace("C", ""))

                child_counter = 0
                for roomNum in range(int(rooms)):
                    adults_and_children += "&q-room-" + str(roomNum) + "-adults=" + list_adults[
                        roomNum] + "&q-room-" + str(
                        roomNum) + "-children=" + list_children[roomNum]
                    for childNum in range(int(list_children[roomNum])):
                        adults_and_children += "&q-room-" + str(roomNum) + "-child-" + str(childNum) + "-age=" + ages[
                            child_counter]
                        child_counter += 1

                print("list of adults: ", list_adults)
                print("list of children: ", list_children)
                print(adults_and_children)
                # url for UK
                driver.get(
                    'https://uk.hotels.com/search.do?q-destination=' + name + " " + address + "&q-check-in=" + check_in + "&q-check-out=" + check_out + "&q-rooms=" + rooms + adults_and_children)
                new_url = driver.current_url
                print(new_url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                try:
                    hotel_price = soup.find('span', {'class': '_2R4dw5'}).text
                except AttributeError:
                    hotel_price = soup.find('span', {'class': '_2R4dw5'}).text
                # Looking for the price in hotel

                driver.quit()  # Close the web browser

                time_end_hotels = time.time()  # FOR TESTING PURPOSES
                time_taken_hotels = time_end_hotels - time_start_hotels  # FOR TESTING PURPOSES
                time_taken_hotels = " Time taken: " + str(time_taken_hotels)  # FOR TESTING PURPOSES
                que.put({"Hotels": hotel_price + time_taken_hotels})  # FOR TESTING PURPOSES
                # que.put({"Hotels": hotel_price}) # Original
                return hotel_price  # returns hotel price

            def booking_com(driver, apple, que, search):  # function for scraping booking.com
                time_start_booking = time.time()

                # def main2(search):
                #     get_search_details(search)
                #     soup = BeautifulSoup(driver.page_source, "html.parser")
                #     # locator for prices on booking.com
                #     price = soup.find("div", {"class": "bui-price-display__value prco-inline-block-maker-helper"})
                #     if price is None:
                #         price = soup.find("span", {"class": "b2e4e409fd _2de857cfd1"})
                #     print(price.text)
                #     price = price.text.strip()
                #     driver.quit()
                #     return price

                def get_search_details(search):
                    datetime.datetime.now()


                    hotel_name,destination, location, check_in, check_out, adults, children, num_rooms, ages, ages_string,  = search[
                                                                                                                     "hotel name"] ,\
                                                                                                                 search[
                                                                                                                     "destination"], \
                                                                                                                 search[
                                                                                                                     "location"], \
                                                                                                                 search[
                                                                                                                     "check in"], \
                                                                                                                 search[
                                                                                                                     "check out"], \
                                                                                                                 search[
                                                                                                                     "adults"], \
                                                                                                                 search[
                                                                                                                     "children"], \
                                                                                                                 search[
                                                                                                                     "rooms"], \
                                                                                                                 search[
                                                                                                                     "ages"], \
                                                                                                                 search[
                                                                                                                     "backup"]  # gets the values from dictionary

                    # destination, location, hotel_name, check_in, check_out, adults, children, rooms, ages, ages = \
                    #     search[
                    #         "destination"], \
                    #     search[
                    #         "location"], \
                    #     search[
                    #         "hotel name"], \
                    #     search[
                    #         "check in"], \
                    #     search[
                    #         "check out"], \
                    #     search[
                    #         "adults"], \
                    #     search[
                    #         "children"], \
                    #     search[
                    #         "rooms"], \
                    #     search[
                    #         "ages"], search["backup"]  # gets the values from dictionary
                    check_in = datetime.datetime.now()
                    year_in, month_in, day_in = str(check_in).split("-")  # splits date (e.g 2021-09-21) into year(2021), month(09) and day(21)
                    check_in_day = day_in
                    check_in_month = month_in
                    check_in_year = year_in
                    check_out = datetime.datetime.today() + datetime.timedelta(days=2)
                    year_out, month_out, day_out = str(check_out).split("-")
                    check_out_day = day_out
                    check_out_month = month_out
                    check_out_year = year_out
                    ages = []
                    print("Type of age string is : {}".format(ages_string))
                    if ages_string is not None:
                        if "," in ages_string:
                            all_ages = str(ages_string).split(",")  # splits at , to get list with all the ages in order
                            ages = all_ages
                        else:
                            ages.append(ages_string)
                    child_age = ages
                    total_children = "group_children=" + str(children)
                    
                    print("Type of children in booking: ",type(children))  # creates part of url for children
                    children = 2
                    children = int(children)
                    
                    if str(children) == "" or int(children) == 0:
                        
                        children = 0
                    else:
                        for i in range(len(child_age)):
                            temp = child_age[i]
                            temp = str(temp)
                            total_children += "&age={}".format(temp)
                    children = 2
                    children = int(children)
                    if (children) > 0:
                        url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&{}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                    destination,check_in_year,check_in_month,check_in_day,check_out_year,check_out_month,check_out_day,adults,total_children,num_rooms
                              )
                    else:
                        url = "https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB&sid=44053b754f64b58cfdde1ddc395974a0&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AqnamocGwAIB0gIkNGEyODNlYTYtYTM2Yi00M2Y3LWE2YjItM2RmYWFlMTM5ZWI22AIF4AIB%3Bsid%3D44053b754f64b58cfdde1ddc395974a0%3Bsb_price_type%3Dtotal%26%3B&ss={}&is_ski_area=0&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&group_children={}&no_rooms={}&b_h4u_keep_filters=&from_sf=1&dest_id=&dest_type=&search_pageview_id=1be740bf37ad0063&search_selected=false".format(
                                    destination,check_in_year,check_in_month,check_in_day,check_out_year,check_out_month,check_out_day,adults,children,num_rooms
                              )
                    driver.get(url)  # opens link in web browser
                
                def main2(search):
                    get_search_details(search)
                    soup = BeautifulSoup(driver3.page_source, "html.parser")
                    # locator for prices on booking.com
                    # price = soup.find("div", {"class": "bui-price-display__value prco-inline-block-maker-helper"})
                    #search_results_table > div:nth-child(2) > div > div > div > div.d4924c9e74 > div:nth-child(3) > div.d20f4628d0 > div.b978843432 > div > div.d7449d770c.a081c98c6f > div.e41894cca1 > div > div.fd1924b122.d4741ba240 > span > div > span.fcab3ed991.fbd1d3018c.e729ed5ab6")
                    # price = soup.select("#search_results_table > div:nth-child(2) > div")
                    price = soup.find("span", {"data-testid":"price-and-discounted-price"})
                    if price is None:
                        price = soup.find("span", {"class": "b2e4e409fd _2de857cfd1"})
                    print(price.text)
                    price = price.text.strip()
                    driver.quit()
                    return price

                room_info = main2(search)
                time_end_booking = time.time()
                time_taken_booking = time_end_booking - time_start_booking
                time_taken_booking = " Time taken: {}".format( str(time_taken_booking))

                que.put({"Booking": room_info + time_taken_booking})  # adds result to result queue

            def expedia(driver, apple, que, search):  # function for scraping expedia
                time_start_expedia = time.time()

                # def main2(search):
                #     get_search_details(search)
                #     soup = BeautifulSoup(driver.page_source, "html.parser")
                #     price = ""
                #     # locator for price on expedia
                #     price = soup.find("div", {"class": "uitk-type-600 uitk-type-bold"})
                #     if price is None:
                #         price = soup.find("span", {"data-stid": "price-lockup-text"})
                #         if price is None:
                #             price = ""
                #         else:
                #             price = price.text
                #     elif price is not None:
                #         price = price.text
                #     else:
                #         price = ""

                #     driver.quit()
                #     return price

                def get_search_details(search):
                    datetime.datetime.now()

                    destination, location, hotel_name, check_in, check_out, adults, children, rooms, ages, room_allocate = \
                        search[
                            "destination"], \
                        search[
                            "location"], \
                        search[
                            "hotel name"], \
                        search[
                            "check in"], \
                        search[
                            "check out"], \
                        search[
                            "adults"], \
                        search[
                            "children"], \
                        search[
                            "rooms"], \
                        search[
                            "ages"], search["room allocate"]  # gets the values from dictionary

                    child_age = ages
                    print("childerrnnnnnnnnnssss{}".format(children))
                    total_children = ""
                    if room_allocate is None:
                        total_children = "children="  # creates part of url for children
                        if children == "":
                            children = 0
                        else:
                            for i in range(len(child_age)):
                                if i == 0:
                                    total_children += "1_{}".format(child_age[0])
                                else:
                                    total_children += "%2C1_{}".format(child_age[i])
                    adult_string = ""
                    children_string = ""
                    if room_allocate is None:
                        adult_string = str(adults)
                    else:
                        if len(room_allocate) > 1:  # need to add another else
                            if "." in room_allocate[0]:
                                first_room = room_allocate[0].split(".")
                                adult_string += str(first_room[0].replace("A", ""))
                                child_num = int(first_room[1].replace("C", ""))
                                for i in range(child_num):
                                    if i == 0:
                                        children_string += "1_{}".format(child_age[i])
                                        child_age.remove(child_age[i])
                                    else:
                                        children_string += "%2C1_" + child_age[i - 1]
                                        child_age.remove(child_age[i - 1])
                                for i in range(1, len(room_allocate)):
                                    if "." in room_allocate[i]:
                                        current_room = room_allocate[i].split(".")
                                        adult_string += "%2C{}".format(str(current_room[0].replace("A", "")))
                                        child_num = int(current_room[1].replace("C", ""))
                                        for j in range(child_num):
                                            children_string += "%2C{}_{}".format(i+1, child_age[j])
                                            child_age.remove(child_age[j])
                                    else:
                                        adult_string += "%2C{}".format(str(room_allocate[i].replace("A", "")))
                            else:
                                adult_string += "%2C{}".format(str(room_allocate[0].replace("A", "")))

                        else:
                            if "." in room_allocate[0]:
                                first_room = room_allocate[0].split(".")
                                adult_string += str(first_room[0].replace("A", ""))
                                child_num = int(first_room[1].replace("C", ""))
                                for i in range(child_num):
                                    if i == 0:
                                        children_string += "1_{}".format(child_age[0])
                                    else:
                                        children_string += "%2C1_{}".format(child_age[i])

                    print("before type of childrennnsssssss areeee {}".format(type(children)))                     
                    children = 2
                    children = int(children)  
                    print("new type of childrennnsssssss areeee {}".format(type(children))) 
                    if(children) > 0:
                        adult_string = 2
                        children_string=2
                        if total_children == "":
                            url = "https://www.expedia.co.uk/Hotel-Search?adults={}&children={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, children_string, check_in, check_in, destination, check_out, hotel_name, check_in)
                        else:
                            url = "https://www.expedia.co.uk/Hotel-Search?adults={}&children={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, total_children, check_in, check_in, destination, check_out, hotel_name, check_in)
                    else:
                        url = "https://www.expedia.co.uk/Hotel-Search?adults={}&d1={}&d2={}&destination={}&directFlights=false&endDate={}&guestRating=&hotelName={}&localDateFormat=d%2FM%2Fyyyy&partialStay=false&regionId=&semdtl=&sort=RECOMMENDED&startDate={}&theme=&useRewards=false&userIntent=".format(adult_string, check_in, check_in, destination, check_out, hotel_name, check_in)

                    url_ending = "www.expedia.co.uk"  # we want UK prices so we change .co.uk to .co.uk
                    url = url.replace("www.expedia.co.uk", url_ending)
                    print(url)
                    driver.get(url)  # opens link in web browser

                    
                def main2(search):
                    get_search_details(search)
                    # print('the source adderrresss is  {}'.format(driver.page_source))
                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    price = ""
                    # locator for price on expedia
                    price = soup.find("div", {"class": "uitk-type-600 uitk-type-bold"})
                    if price is None:
                        price = soup.find("span", {"data-stid": "price-lockup-text"})
                        if price is None:
                            price = ""
                        else:
                            price = price.text
                    elif price is not None:
                        price = price.text
                    else:
                        price = ""

                    driver.quit()
                    return price

                room_info = main2(search)
                time_end_expedia = time.time()
                time_taken_expedia = time_end_expedia - time_start_expedia
                time_taken_expedia = " Time taken: " + str(time_taken_expedia)
                que.put({"Expedia": (str(room_info)) + time_taken_expedia})  # adds result to result queue

            options = Options()
            # need to change user agent if using headless or else you will get blocked
            options.add_argument('--headless')  # headless option
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument("--proxy-server='direct://'")
            options.add_argument("--proxy-bypass-list=*")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--log-level=3")
            options.add_argument('--allow-running-insecure-content')
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")  # user agent
            options.add_argument('--disable-software-rasterizer')
            options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            driver1 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
            driver2 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
            driver3 = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))  # browser for booking.com
            que = queue.Queue()
            thread_list = list()  # threads that allow all functions to run in parallel instead of sequentially
            browserThread = Thread(target=expedia, args=(driver1, 'https://www.google.com', que, search))
            thread_list.append(browserThread)
            browserThread2 = Thread(target=hotels, args=(driver2, 'https://www.google.com', que, search))
            thread_list.append(browserThread2)
            browserThread3 = Thread(target=booking_com, args=(driver3, 'https://www.google.com', que, search))
            thread_list.append(browserThread3)
            browserThread.start()  # start threads
            browserThread2.start()
            browserThread3.start()
            for t in thread_list:
                t.join()

            #
            booking_price = ""
            hotels_price = ""
            expedia_price = ""

            for item in que.queue:
                for key, value in item.items():
                    if key == "Booking":
                        # booking_price = value
                        booking_price = key + " " + value
                    if key == "Hotels":
                        # hotels_price = value
                        hotels_price = key + " " + value
                    if key == "Expedia":
                        # expedia_price = value
                        expedia_price = key + " " + value

            if hotels_price == "":  # if prices werent found for any of the websites then "N/A" is returned for that website
                hotels_price = "Hotels: N/A"
            if booking_price == "":
                booking_price = "Booking: N/A"
            if expedia_price == "":
                expedia_price = "Expedia: N/A"

            all_price = booking_price + "-" + hotels_price + "-" + expedia_price
            time_end = time.time()
            total_time = " Total Time elapsed: ", time_end - time_start
            all_price_and_time = str(all_price) + " " + str(total_time)
            print(all_price_and_time)
            return all_price_and_time  # This will return to the controller


@app.route("/", methods=['GET', 'POST'])
def scrape():
    if current_server == "US":
        select = select_server()
        return select.server_US()

    if current_server == "UK":
        select = select_server()
        return select.server_UK()

    if current_server == "EU":
        select = select_server()
        return select.server_EU()



if __name__ == '__main__':
    from waitress import serve

    serve(app, host='0.0.0.0', port=5678)
    # app.run(debug=True, port=5678, host='0.0.0.0')