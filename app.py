from flask import Flask, render_template, request, flash
import os
if os.path.exists("env.py"):
    import env
import pymongo


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# MongoDB Setup
MONGO_URI = os.environ.get("MONGO_URI")
DATABASE = "milestone2"
COLLECTION = "Admin"


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        print("Mongo is connected")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s") % e


conn = mongo_connect(MONGO_URI)
coll = conn[DATABASE][COLLECTION]


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
