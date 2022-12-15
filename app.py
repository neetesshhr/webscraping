# importing Flask and other modules
from flask import Flask, request, render_template

# Flask constructor
app = Flask(__name__)

# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":
        first_name = request.form.get("fname")
        last_name = request.form.get("lname")
        bday = request.form.get("birthday")
        full_name = "<h1> Welcome</h1> <h2>{} {} with birthday {}</h2>".format(first_name, last_name, bday)
        return full_name
    return render_template("form.html")


if __name__=='__main__':
    app.run()
