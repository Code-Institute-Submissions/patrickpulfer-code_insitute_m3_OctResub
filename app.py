from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
import os
if os.path.exists("env.py"):
    import env
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import logging

# Setting up Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
    # filename='logs.log
    # filemode='a'
)
logging.info('app.py initalized!')


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


# MongoDB Setup
MONGO_URI = os.environ.get("MONGO_URI")
DATABASE = "TheInterviewMasterDeck"


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        logging.info('MongoDB Connected!')
        return conn
    except pymongo.errors.ConnectionFailure as e:
        logging.critical('Could not connect to MongoDB: %s', e)


# Initial MongoDB connection
conn = mongo_connect(MONGO_URI)
mongo_database = conn[DATABASE]
logging.info('MongoDB Server version: %s', conn.server_info()["version"])


# Logging and exit if main database is not detected
dblist = conn.list_database_names()
if DATABASE in dblist:
    logging.info("Database 'TheInterviewMasterDeck' detected!")
else:
    logging.critical("Database 'TheInterviewMasterDeck' NOT detected!")
    exit()


#
# App Routings
#

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    mongo_collection = mongo_database["admin"]
    admin_logged = 0
    #
    # Login functionality for admin
    #
    # Functionality will log if attempt has been successful
    # Template will adapt based on admin_logged variable
    #
    if request.method == "POST":

        existing_user = mongo_collection.find_one(
            {"email": request.form.get("email").lower()})
        print(request.form.get("email").lower())
        print('Existing User: ', existing_user)
        flash("Welcome back, " + existing_user["name"])
        print(existing_user["name"])

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                logging.info('Admin Login attempt successful')
                session["admin"] = existing_user["name"]
                session["email"] = existing_user["email"]
                admin_logged = 1
            else:
                # password does not match
                logging.warning(
                    'Admin Login attempt failed with wrong password')
                flash("Incorrect Email and/or Password")
                return redirect(url_for("admin"))

        else:
            # username doesn't exist
            flash("Incorrect Email and/or Password")
            logging.warning('Admin Login attempt failed with incorrect email')
            return redirect(url_for("admin"))

    return render_template("admin.html", admin_logged=admin_logged)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
