from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
if os.path.exists("env.py"):
    import env
import pymongo
from pymongo import TEXT
import logging
import datetime
import markdown
import random


#
# Setting up logging and create the file if it does not exist
#
logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{',
    filename='logs.log',
    filemode='a'
)
f = open("logs.log", "w+")
logging.info('app.py initalized!')


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


# Initializing variables
MONGO_URI = os.environ.get("MONGO_URI")
DATABASE = "TheInterviewMasterDeck"


# Get Datetime
date_today = datetime.datetime.now()


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
mongo_collection = mongo_database["questions"]
# Checks if text search index has already been created. If not, create one
index_name = 'question_1'
if index_name not in mongo_collection.index_information():
    mongo_collection.create_index(name='question_1', keys=[
                                  ('question', TEXT)], default_language='none')


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


# Index
@ app.route("/")
def index():
    mongo_collection = mongo_database["settings"]
    doc_instructions = mongo_collection.find_one({"id": "instructions"})
    instructions = markdown.markdown(doc_instructions['text'])
    return render_template("index.html", instructions=instructions)


# End User - Start
@ app.route("/start")
def start():
    mongo_collection = mongo_database["questions"]
    all_cards = mongo_collection.find({"visible": "Yes"})
    objects = []
    for object in all_cards:
        objects.append(object)
    random.shuffle(objects)
    return render_template("start.html", cards=objects)


# Admin
@ app.route("/admin", methods=["GET", "POST"])
def admin():
    settings = ''
    mongo_collection = mongo_database["admin"]
    #
    # Login functionality for admin
    #
    # Functionality will log if attempt has been successful
    # Template will adapt based on admin_logged variable
    #
    if request.method == "POST" and session.get('logged_in') == None:
        existing_user = mongo_collection.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                logging.info('Admin Login attempt successful')
                flash("Welcome, {}".format(existing_user["name"]))
                session["admin"] = existing_user["name"]
                session["email"] = existing_user["email"]
                session["logged_in"] = True
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
    mongo_collection = mongo_database["settings"]
    settings = mongo_collection.find_one({"id": "instructions"})
    return render_template("admin.html", admin_logged=session.get('logged_in'), admin_session=session, settings=settings)


# Logout
@ app.route("/admin_logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    logging.info('Admin Logout')
    session.pop("logged_in")
    return redirect(url_for("admin"))


# Admin - Cards Overview
@ app.route("/admin_cards", methods=["GET", "POST"])
def admin_cards():
    # Check if admin is logged in
    if session.get('logged_in') == True:
        mongo_collection = mongo_database["questions"]
        cards = list(mongo_collection.find({"visible": "Yes"}))
        cards_not_visible = list(
            mongo_collection.find({"visible": {'$ne': 'Yes'}}))
        return render_template("admin_cards.html", cards=cards, cards_not_visible=cards_not_visible, datetime=date_today.strftime("%x"), admin_logged=session.get('logged_in'), admin_session=session)
    else:
        return admin()


# Admin - Add new card
@ app.route("/admin_new_card", methods=["GET", "POST"])
def admin_new_card():
    if request.method == "POST":
        if session.get('logged_in') == True:
            mongo_collection = mongo_database["questions"]
            new_admin_card_details = {
                "id": request.form.get("id"),
                "question": request.form.get("question"),
                "tip": request.form.get("tip"),
                "visible": request.form.get("visible"),
                "added_date": request.form.get("date")
            }
            mongo_collection.insert_one(new_admin_card_details)
            flash("New Questions Card added!")
            logging.info('Admin has added a new card')
            return redirect(url_for("admin_cards"))
        else:
            return admin()


# Admin - Update Questions Card Page
@ app.route("/admin_card_update/<card_id>", methods=["GET", "POST"])
def admin_card_update(card_id):
    mongo_collection = mongo_database["questions"]
    card = mongo_collection.find_one({"id": card_id})
    return render_template("admin_card_update.html", card=card, datetime=date_today.strftime("%x"), admin_logged=session.get('logged_in'), admin_session=session)


# Admin - Update Questions Card Execute
@ app.route("/admin_card_update_execute/<card_id>", methods=["GET", "POST"])
def admin_card_update_execute(card_id):
    if request.method == "POST":
        if session.get('logged_in') == True:
            mongo_collection = mongo_database["questions"]
            submit = {
                "id": request.form.get("id"),
                "question": request.form.get("question"),
                "tip": request.form.get("tip"),
                "visible": request.form.get("visible_update"),
                "added_date": request.form.get("date")
            }
            mongo_collection.replace_one({"_id": ObjectId(card_id)}, submit)
            flash("Questions Card Modified")
            logging.info('Card has been modified')
            return redirect(url_for("admin_cards"))
        else:
            return admin()


# Admin - Delete Questions Card
@ app.route("/admin_card_delete/<card_id>", methods=["GET", "POST"])
def admin_card_delete(card_id):
    if request.method == "GET":
        if session.get('logged_in') == True:
            mongo_collection = mongo_database["questions"]
            mongo_collection.delete_one({"_id": ObjectId(card_id)})
            flash("Questions Card has been deleted")
            logging.info('Card has been deleted')
            return redirect(url_for("admin_cards"))
        else:
            index()


# Admin - Update Settings
@ app.route("/instructions_update", methods=["GET", "POST"])
def instructions_update():
    if session.get('logged_in') == True:
        mongo_collection = mongo_database["settings"]
        mongo_collection.replace_one({"id": "instructions"}, {"id": "instructions",
                                                              "text": request.form.get("instructions")})
        flash("Instructions updated")
        logging.info('Instructions updated')
    return admin()

# User - Search Card by Keyword


@ app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        mongo_collection = mongo_database["questions"]
        query = request.args.get("keyword")
        result = mongo_collection.find({"$text": {"$search": query}})
        objects = []
        for object in result:
            objects.append(object)
        return render_template("search.html", cards=objects)
    else:
        return start()


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
