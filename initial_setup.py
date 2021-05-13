import os
if os.path.exists("env.py"):
    import env
import pymongo
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# MongoDB Setup
MONGO_URI = os.environ.get("MONGO_URI")
DATABASE = "TheInterviewMasterDeck"
COLLECTION = "Admin"


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s") % e


conn = mongo_connect(MONGO_URI)
mongo_database = conn[DATABASE]


# Get Datetime
date_today = datetime.datetime.now()


dblist = conn.list_database_names()
print(' ')
print('The')
print(' ___       _                  _               __  __           _            ')
print('|_ _|_ __ | |_ ___ _ ____   _(_) _____      _|  \/  | __ _ ___| |_ ___ _ __ ')
print(" | || '_ \| __/ _ \ '__\ \ / / |/ _ \ \ /\ / / |\/| |/ _` / __| __/ _ \ '__|")
print(' | || | | | ||  __/ |   \ V /| |  __/\ V  V /| |  | | (_| \__ \ ||  __/ |   ')
print('|___|_| |_|\__\___|_|    \_/ |_|\___| \_/\_/ |_|  |_|\__,_|___/\__\___|_|   ')
print('                                                                       Deck')
print('')
print("Checking Database...")
if DATABASE in dblist:
    print("\U0001F44D", "Database 'TheInterviewMasterDeck' found!")
    collist = mongo_database.list_collection_names()
    if "admin" in collist:
        print("\U0001F44D", "The collection 'admin' found!")

    # Find Default Admin
    mongo_collection = mongo_database["admin"]
    try:
        doc = mongo_collection.find_one({"id": 0})
    except:
        print("Error accessing the database")

    if doc:
        print("\U0001F44D", "Setup is already complete! Default admin account detected!")
        exit()
    if not doc:
        print("\U0001F449",
              "No default admin account detected. Will create this one now...")
        print('')
        print('')
        print("\U0001F9D1", "Details of the Admin account")
        print('')
        admin_name = input("-> Enter your Name: ")
        admin_email = input("-> Enter your Email: ")
        admin_password = input("-> Enter your Password: ")
        admin_password2 = input("-> Confirm your Password: ")
        print('')
        if admin_password == admin_password2:
            new_doc = {
                "id": 0,
                "name": admin_name,
                "email": admin_email,
                "password": generate_password_hash(admin_password)
            }
            try:
                mongo_collection.insert_one(new_doc)
                print("\U0001F44F", "Your admin account has been created!")
            except:
                print("Error accessing the database")

            mongo_collection = mongo_database["questions"]
            new_doc = {
                "id": 1,
                "question": "Edit Me Question",
                "tip": "Edit Me Tip.",
                "visible": "Yes",
                "added_date": date_today.strftime("%x")
            }
            try:
                mongo_collection.insert_one(new_doc)
                print("\U0001F44F",
                      "'questions' collection created & added default record!")
            except:
                print("Error accessing the database")

            mongo_collection = mongo_database["settings"]
            new_doc = {
                "id": "instructions",
                "text": "Edit me with Instructions",
            }
            try:
                mongo_collection.insert_one(new_doc)
                print("\U0001F44F",
                      "'settings' collection created & added default record!")
            except:
                print("Error accessing the database")
            print('')
            print("\U0001F37E",
                  "Setup Complete. You may now log in to http://<App>/admin")
        else:
            print('Password does not match! Please try again! Exiting...')
else:
    print("Database 'TheInterviewMasterDeck' not found. Please create a Database called 'TheInterviewMasterDeck' with a collection called 'admin' first before continuing. Exiting...")

conn.close()
