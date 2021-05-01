from flask import Flask, render_template, request, flash
import os
if os.path.exists("env.py"):
    import env
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
COLLECTION = "Admin"


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        logging.info('MongoDB Connected!')
        return conn
    except pymongo.errors.ConnectionFailure as e:
        logging.critical('Could not connect to MongoDB: %s', e)
        print("Could not connect to MongoDB: %s") % e


conn = mongo_connect(MONGO_URI)
coll = conn[DATABASE][COLLECTION]
logging.info('MongoDB Server version: %s', conn.server_info()["version"])


dblist = conn.list_database_names()
if DATABASE in dblist:
    print("The database exists.")
else:
    print('no')


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
