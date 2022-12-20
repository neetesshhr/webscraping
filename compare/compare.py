from expedia import expedia_price, expedia_content
from bookings import bookings_price, bookings_content
from hotels import hotel_price, hotel_content
from flask import Flask, request, render_template
import time

app = Flask(__name__)
@app.route('/', methods = ["GET", "POST"])

def gfg():
    if request.method == "POST":
        adult_string = request.form.get("adults")
        children_string = request.form.get("childrens")
        adults_and_children = adult_string + children_string
        check_in =request.form.get("check_in")
        check_out = request.form.get("check_out")
        destination = request.form.get("destination")
        hotel_name = request.form.get("hotel_name")
        rooms = request.form.get("rooms")
        expediaPrice = expedia_price(adult_string, children_string, check_in, check_out, destination, hotel_name)
        print("The price for expedia is: {}".format(expediaPrice.text))
        expedia = expediaPrice.text.replace("£","")
        print("The replaced price is {}".format(expedia))
        # print(type(expediaPrice))
        # bookings= bookings_price(check_in, check_out, destination, adults=adult_string, total_children=children_string, num_rooms=rooms)
        hotels = hotel_price(hotel_name, destination, rooms, adults_and_children, check_in, check_out)
        print("Hotels{}".format(hotels))
        hotels = hotels.text
        
        # bookings = bookings.text
        print("hotels {},  expedia {} ".format(hotels, expedia))


        # bookings = ' '.join(bookings.split()[1:])
        hotels = ' '.join(hotels.split()[1:])

        expedia = int(expedia)
        # bookings = int(bookings)
        hotels = int(hotels)
  
        # best_value = min(expedia, bookings, hotels)

        # # if best_value == expedia:
        # #     print("expedia has the best value")
        content = []
        content.append({"<h1> Expedia </h1>":expedia_content(adult_string, children_string, check_in, check_out, destination, hotel_name), "<br/><h1>Hotels</h1>":hotel_content(hotel_name, destination, rooms, adults_and_children, check_in, check_out)})
        #     # print(e)
    
        # # elif best_value == bookings:
        #     print("bookings has best value")
        # content =  bookings_content(check_in, check_out, destination, adults=adult_string, total_children=children_string, num_rooms=rooms)
        # elif best_value == hotels:
        #     print("hotels are best ")
        # content = hotel_content(hotel_name, destination, rooms, adults_and_children, check_in, check_out)
        #     print(content)
        contents = '{}'.format(content)
        contents = contents.replace("[", "")
        return contents
        

    return render_template("form.html")

if __name__ == '__main__':
    app.run()



