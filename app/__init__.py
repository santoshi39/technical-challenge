'''
Main entry point for the app!
Includes all the apis for Register,Login,Logout,Upload,getData
Returns the respective responses required for frontend integration
'''


# import all the required packages/libraries
import datetime
from flask_cors import CORS
import hashlib
from flask import Flask, request, jsonify, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from .db_connection import *
from .models import id_generator
import pandas as pd
import json
from bson import json_util
from datetime import datetime, timedelta
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)
# initiate the flask app
app = Flask(__name__)
# set a secret key for token
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# initiate JWT - for authentitation and authorization
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key3939!'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=10)
CORS(app)

# test url


@app.route('/', methods=['GET'])
def intro():
    return "Welcome to Logic Layer"


# register-user
# input json : role,username,email,password
# return : user gets registered and the respective details will be saved in mongodb
@app.route("/api/register_user", methods=["POST"])
def register():
    try:
        new_user = request.get_json()  # json body request
        new_user["password"] = hashlib.sha256(
            new_user["password"].encode("utf-8")).hexdigest()  # encrpt password
        doc = get_userdetails(new_user['username'])  # check if user exists
        if not doc:
            # generate a new userId for new user
            userId = id_generator(new_user['role'])
            logger.info(f"user Id generated: {userId}")
            insert_userdetails(new_user, userId)  # insert new user in DB
            logger.info(f"user created succefully")
            return jsonify({'message': 'User created successfully'}), 200
    except Exception as e:
        logger.info(
            f"user registration failed with exception : {e}")
        return jsonify({'message': str(e)}), 401

# login user
# input json : username,password
# returns role of the user, username, jwt accesstoken


@app.route("/api/login", methods=["POST"])
def login():
    login_details = request.get_json()  # json body request
    try:
        # search for user in database
        user_from_db = get_userdetails(login_details['username'])
        if user_from_db:  # check if user exists in db
            encrpted_password = hashlib.sha256(
                login_details['password'].encode("utf-8")).hexdigest()  # encrypt the passowrd
            # check if the password is matching
            if encrpted_password == user_from_db['password']:
                access_token = create_access_token(
                    identity=user_from_db['username'])  # create jwt token
                session['username'] = login_details['username']
                logger.info(f"user created succefully")
                return jsonify({'username': login_details['username'], 'role': user_from_db['role'], 'access_token': access_token}), 200
            else:
                logger.info(f"user login failed : incorrect password")
                return jsonify({'message': 'password is incorrect'}), 401
        else:
            logger.info(f"user login failed : user doesn't extist")
            return jsonify({'message': 'User doesnot exist'}), 401
    except Exception as e:
        logger.info(f"user login failed with exception : {e}")
        return jsonify({'message': 'Login failed.'}), 401


# get data for admin based on uploaded date
# check the role of the user
# allow admin, deny the access for all other roles
# fetch data from db based on uploaded data

@app.route("/api/get_data", methods=["POST"])
@jwt_required()
def view_data():
    try:
        current_user = get_jwt_identity()  # Get the identity of the current user
        user_from_db = users_collection.find_one({'username': current_user})
        if user_from_db:
            if user_from_db['role'] == 'Admin' or 'admin':  # validate the role of user
                content = request.json
                # fetch data based on selected date
                data = get_dbdata(content['uploaded_on'])
                logger.info(f"successfully fetched data")
                return jsonify({'message': "successfully fetched data", 'response': json.loads(json_util.dumps(data))}), 200
            else:
                logger.info(f"Access Denied. Login as Admin")
                return jsonify({'message': 'Access denied.Please login as Admin'}), 401
        else:
            logger.info(f"user not found")
            return jsonify({'message': 'User doesnot exist'}), 401
    except Exception as e:
        logger.info(f"failed with exception : {e}")
        return jsonify({'error': str(e)}), 404

# uplaod - accept excel file as input
# read the excel file and insert the data in mongodb


@app.route("/api/upload", methods=["POST"])
@jwt_required()
def upload():
    try:
        current_user = get_jwt_identity()  # Get the identity of the current user
        user_from_db = get_userdetails(current_user)
        if user_from_db:
            if user_from_db['role'] == 'Admin' or 'admin':  # validate user role
                # Fetch excel file from frontend
                flask_file = request.files['file']
                if not flask_file:
                    return jsonify({'message': 'Please upload a file'}), 404
                else:
                    # read excel file and convert to dataframe
                    df = pd.read_excel(flask_file, engine='openpyxl')
                    df["uploaded_on"] = pd.Timestamp(datetime.now())
                    df["uploaded_on"] = df["uploaded_on"].dt.strftime(
                        '%Y-%m-%d')
                    records = df.to_json(orient='records', date_format='iso')
                    insert_data(json.loads(records))
                    logger.info(f"successfully uploaded file data")
                    return jsonify({'message': 'data uploaded successfully'}), 200
            else:
                logger.info(f"Access Denied. Login as Admin")
                return jsonify({'error': 'Access denied.Please login as Admin'}), 404
        else:
            logger.info(f"user not found")
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.info(f"Upload failed with exception : {e}")
        return jsonify({'error': str(e)}), 404


# logout of session
@app.route('/api/logout', methods=["POST"])
def logout():
    if 'username' in session:
        session.pop('username', None)
    return jsonify({'message': 'You successfully logged out'})


# development - debug True.
# prod - debug false
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5020)
