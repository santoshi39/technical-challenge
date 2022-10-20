'''
MONGO DB connection file with Pymongo
-Mongoclient connection string with username and password, db names and collection names.
-Includes all db related methods.
- easier to change or add db connections.
'''

from pymongo import MongoClient

# mongo db details
client = MongoClient(
    "mongodb+srv://jlr_test_user:JLR1234test@cluster0.cfdrtf8.mongodb.net/test?retryWrites=true&w=majority")
db = client["testdb"]
users_collection = db["users"]
data = db["data"]

# fetch data based on uploaded date(user selection)


def get_dbdata(udate):
    cursor = data.find({'uploaded_on': udate}, {'_id': False})
    res = list(cursor)
    return res

# fetch user details based on username


def get_userdetails(username):
    user_details = users_collection.find_one(
        {"username": username})
    return user_details

# insert userdetails : new user


def insert_userdetails(new_user, userId):
    users_collection.insert_one({"emailId": new_user['emailId'], "username": new_user["username"], "role": new_user['role'],
                                 "password": new_user['password'], 'userId': userId})

# Insert rows of excel file as mongo documents


def insert_data(records):
    data.insert_many(records)

# get the count of users based on role


def get_role_count(role):
    users_collection.count_documents({"roles": role})
