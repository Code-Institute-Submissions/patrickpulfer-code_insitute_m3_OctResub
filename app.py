import os
import pymongo
import logging
import datetime
import markdown
import random
from pymongo import TEXT
from flask import (
    Flask, flash,
    render_template,
    redirect,
    request,
    session,
    url_for
)
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


"""
Logging mechanism to log actions to logs.log file
"""
logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{',
    filename='logs.log',
    filemode='a'
)
f = open("logs.log", "w+")
logging.info('Main application has been initialized!')


"""
Check if environment variables are set
"""
if os.environ.get("MONGO_URI") and os.environ.get("SECRET_KEY"):
    MONGO_URI = os.environ.get("MONGO_URI")
    app.secret_key = os.environ.get("SECRET_KEY")
    logging.info('Environmental variables found and loaded')
else:
    logging.critical('Environmental variables NOT FOUND!')
    logging.critical('Ensure environmental variables are set before running again!')
    exit()


"""
Setting initial variables
"""
DATABASE = "TheInterviewMasterDeck"
date_today = datetime.datetime.now()


def mongo_connect(url):
    """ Function to perform initial MongoDB connection
    :type url:
    :param url:
    """
    try:
        conn = pymongo.MongoClient(url)
        logging.info('MongoDB Connected successfully!')
        return conn
    except pymongo.errors.ConnectionFailure as e:
        logging.critical('Could not connect to MongoDB: %s', e)


"""
Initialization block:
    1. Will connect to MongoDB using the environmental variable
    2. Will create a search index if not yet created
    3. Will detect if database has been setup
"""
conn = mongo_connect(MONGO_URI)
mongo_database = conn[DATABASE]
logging.info('MongoDB Server version: %s', conn.server_info()["version"])
mongo_collection = mongo_database["questions"]
# Checks if text search index has already been created. If not, create one
index_name = 'question_1'
if index_name not in mongo_collection.index_information():
    logging.info(
        'MongoDB Text Search index has not yet been created... creating.')
    mongo_collection.create_index(
        name='question_1',
        keys=[('question', TEXT)],
        default_language='none'
    )
else:
    logging.info(
        'MongoDB Text Search index has already been created... skipping.')
dblist = conn.list_database_names()
if DATABASE in dblist:
    logging.info("Database 'TheInterviewMasterDeck' detected in MongoDB!")
else:
    logging.critical("Database 'TheInterviewMasterDeck' NOT detected!")
    logging.critical("Ensure you have followed https://github.com/patrickpulfer/code_insitute_m3#steps")
    exit()


"""
App Routings
"""


@ app.route("/")
def index():
    """ 
    End User Index Page
    """
    mongo_collection = mongo_database["settings"]
    doc_instructions = mongo_collection.find_one({"id": "instructions"})
    instructions = markdown.markdown(doc_instructions['text'])
    return render_template("index.html", instructions=instructions)


@ app.route("/start")
def start():
    """ 
    End User Start the Game Page
    """
    mongo_collection = mongo_database["questions"]
    all_cards = mongo_collection.find({"visible": "Yes"})
    objects = []
    for object in all_cards:
        objects.append(object)
    random.shuffle(objects)
    return render_template("start.html", cards=objects)


@ app.route("/admin", methods=["GET", "POST"])
def admin():
    """ 
    Admin Page function:
        1. Will attempt login procedures (compare admin & password hash) if user is not yet logged in and method is POST
        2. Will display the admin console if admin is logged in
    """
    settings = ''
    mongo_collection = mongo_database["admin"]
    if request.method == "POST" and session.get('logged_in') == None:
        existing_user = mongo_collection.find_one(
            {"email": request.form.get("email").lower()})
        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                logging.info('Admin Login attempt successful')
                flash("Welcome, {}".format(existing_user["name"]))
                session["admin"] = existing_user["name"]
                session["email"] = existing_user["email"]
                session["logged_in"] = True
            else:
                logging.warning(
                    'Admin Login attempt failed with wrong password')
                flash("Incorrect Email and/or Password")
                return redirect(url_for("admin"))
        else:
            flash("Incorrect Email and/or Password")
            logging.warning('Admin Login attempt failed with incorrect email')
            return redirect(url_for("admin"))
    mongo_collection = mongo_database["settings"]
    settings = mongo_collection.find_one({"id": "instructions"})
    return render_template(
        "admin.html",
        admin_logged=session.get('logged_in'),
        admin_session=session,
        settings=settings
    )


@ app.route("/admin_logout")
def logout():
    """ 
    Logout function
    """
    flash("You have been logged out")
    logging.info('Admin Logout')
    session.pop("logged_in")
    return redirect(url_for("admin"))


@ app.route("/admin_cards", methods=["GET", "POST"])
def admin_cards():
    """ 
    Admin Cards Overview Page:
        1. Will check if logged in, then show page
        2. Will get values from database for template render
    """
    if session.get('logged_in') == True:
        mongo_collection = mongo_database["questions"]
        cards = list(mongo_collection.find({"visible": "Yes"}))
        cards_not_visible = list(
            mongo_collection.find({"visible": {'$ne': 'Yes'}})
        )
        mongo_collection = mongo_database["settings"]
        cards_count = mongo_collection.find_one({"id": "cards_count"})
        cards_count = cards_count['integer']
        return render_template(
            "admin_cards.html",
            cards = cards,
            cards_not_visible = cards_not_visible,
            cards_count = cards_count,
            datetime = date_today.strftime("%x"),
            admin_logged = session.get('logged_in'),
            admin_session = session
        )
    else:
        return admin()


@ app.route("/admin_new_card", methods=["GET", "POST"])
def admin_new_card():
    """ 
    Question Card Creation:
        1. Will check if logged in and method is POST
        2. Will attempt to add the new card & update the card counter
    """
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
            mongo_collection = mongo_database["settings"]
            cards_count_collection = mongo_collection.find_one({"id": "cards_count"})
            cards_count_incrementing = cards_count_collection['integer'] + 1
            mongo_collection.replace_one(
                {"id": "cards_count"},
                {
                    "id": "cards_count",
                    "integer": cards_count_incrementing
                },
            )
            return redirect(url_for("admin_cards"))
        else:
            return admin()


@ app.route("/admin_card_update/<card_id>", methods=["GET", "POST"])
def admin_card_update(card_id):
    """ 
    Questions Card Update Form
    """
    mongo_collection = mongo_database["questions"]
    card = mongo_collection.find_one({"id": card_id})
    return render_template(
        "admin_card_update.html",
        card=card,
        datetime=date_today.strftime("%x"),
        admin_logged=session.get('logged_in'),
        admin_session=session
    )


@ app.route("/admin_card_update_execute/<card_id>", methods=["GET", "POST"])
def admin_card_update_execute(card_id):
    """
    Questions Card Update Execution:
        1. Will check if logged in and method is POST
        2. Will attempt to update the Question Card accordingly

        :type card_id:
        :param card_id:
    """
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
            flash("Questions Card %s has been updated." % request.form.get("id"))
            logging.info('Questions Card %s has been updated.' % request.form.get("id"))
            return redirect(url_for("admin_cards"))
        else:
            return admin()


@ app.route("/admin_card_delete/<card_id>", methods=["GET", "POST"])
def admin_card_delete(card_id):
    """ 
    Questions Card Update Form

    :type card_id:
    :param card_id:
    """
    if request.method == "GET":
        if session.get('logged_in') == True:
            mongo_collection = mongo_database["questions"]
            mongo_collection.delete_one({"_id": ObjectId(card_id)})
            flash("Questions Card with _id %s been deleted." % card_id)
            logging.info('Questions Card with _id %s been deleted.' % card_id)
            return redirect(url_for("admin_cards"))
        else:
            logging.info('Card deletion has been attempted without a session')
            index()


@ app.route("/instructions_update", methods=["GET", "POST"])
def instructions_update():
    """ 
    Instructions Update Form
    """
    if session.get('logged_in') == True:
        mongo_collection = mongo_database["settings"]
        mongo_collection.replace_one(
            {"id": "instructions"},
            {"id": "instructions", "text": request.form.get("instructions")}
        )
        flash("Instructions updated")
        logging.info('Instructions updated')
    return admin()


@ app.route("/search", methods=["GET", "POST"])
def search():
    """ 
    End User Question Card Search
    """
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
        port=int(os.environ.get("PORT", "5001")),
        debug=True
    )
