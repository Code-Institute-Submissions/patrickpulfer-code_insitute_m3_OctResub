import os
if os.path.exists("env.py"):
    import env
import pymongo
import datetime

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
    print("\U0001F44D", "Database 'TheInterviewMasterDeck' Exists!")
    collist = mongo_database.list_collection_names()
    if "admin" in collist:
        print("\U0001F44D", "The collection 'admin' already exists.")
    else:
        print("\U0001F449", "The tables does not yet exists. Will create those now...")
        mongo_collection = mongo_database["admin"]
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
                "name": admin_name,
                "email": admin_email,
                "password": admin_password
            }
            try:
                mongo_collection.insert_one(new_doc)
                print("\U0001F44F", "Admin created!")
            except:
                print("Error accessing the database")
            mongo_collection = mongo_database["users"]
            new_doc = {
                "id": 1,
                "name": "User",
                "email": "user@email.com",
                "registration_date": date_today.strftime("%x"),
                "last_login_date": date_today.strftime("%x")
            }
            try:
                mongo_collection.insert_one(new_doc)
                print("\U0001F44F", "Users table created with generic user!")
            except:
                print("Error accessing the database")
            mongo_collection = mongo_database["questions"]
            new_doc = {
                "id": 1,
                "question": "Can you tell me about yourself?",
                "tip": "When talking about yourself, focus on the professional YOU and how relevant you are for the job.",
                "added_date": date_today.strftime("%x"),
            }
            try:
                mongo_collection.insert_one(new_doc)
                print("\U0001F44F", "Questions table created with default record!")
            except:
                print("Error accessing the database")

        else:
            print('Password does not match! Exiting...')
            conn.close()
else:
    print("Database 'TheInterviewMasterDeck' does not exist. Please create one first before proceeding")
