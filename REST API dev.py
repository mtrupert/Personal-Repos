#Importing credentials and sql connections
import flask
import hashlib
from flask import jsonify
from flask import request, make_response

from sql import create_connection
from sql import execute_read_query
from sql import execute_query

import creds

#setting up an application name
app = flask.Flask(__name__)
app.config["DEBUG"] = True #allow to show errors in browser

#default url without any routing as GET request
@app.route('/', methods=['GET'])
def home():
    return "<h1> WELCOME to API class</h1>"

masterPassword = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # Hash value of Password 'password' 
masterUsername = 'username'

# 'password' as plaintext should not be used to verify authorization to access. 
# the password should be hashed and the hash should be compared to the stored password hash in the database
@app.route('/authenticatedroute', methods=['GET'])
def auth_test():
    if request.authorization:
        encoded = request.authorization.password.encode() #unicode encoding
        hasedResult = hashlib.sha256(encoded) #hashing
        if request.authorization.username == masterUsername and hasedResult.hexdigest() == masterPassword:
            return '<h1> Authorized user access </h1>'
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

# ///////////// API's for DATABASE access ///////////////
#     
#create a endpoint to get a single user from DB : http://127.0.0.1:5000/api/snowboard
@app.route('/api/snowboard', methods=['GET'])
def api_users_by_id():
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return 'Error: No ID is provided!'
    myCreds = creds.Creds()
    conn = create_connection(myCreds.connectionstring, myCreds.username, myCreds.passwd, myCreds.dataBase)
    sql ="select * from snowboard"
    users = execute_read_query(conn, sql)
    results = []
    for user in users:
        if user['id']== id:
            results.append(user)
    return jsonify(results)

#get all data from the snowboard table
@app.route('/api/snowboard/all', methods=['GET'])
def api_users_all():
    myCreds = creds.Creds()
    conn = create_connection(myCreds.connectionstring, myCreds.username, myCreds.passwd, myCreds.dataBase)
    sql ="select * from snowboard"
    users = execute_read_query(conn, sql)
    return jsonify(users)

#adding a new snowboard for the database with POST method
@app.route('/api/snowboard', methods=['POST'])
def api_add_users():
    request_data = request.get_json()
    NewBoardType = request_data['boardtype']
    NewBrand = request_data['brand']
    NewMSRP = request_data['msrp']
    NewSize = request_data['size']

    myCreds = creds.Creds()
    conn = create_connection(myCreds.connectionstring, myCreds.username, myCreds.passwd, myCreds.dataBase)
    sql = "insert into snowboard(boardtype, brand, msrp, size) values ('%s','%s', %s, %s)" % (NewBoardType, NewBrand, NewMSRP, NewSize)

    execute_query(conn, sql)
    return 'Add user request successful!'

# Delete a snowboard record with delete method
@app.route('/api/snowboard', methods=['DELETE'])
def api_delete_user_byID():
    request_data = request.get_json()
    idtodelete = request_data['id']
    
    myCreds = creds.Creds()
    conn = create_connection(myCreds.connectionstring, myCreds.username, myCreds.passwd, myCreds.dataBase)
    sql = "delete from snowboard where id = %s" % (idtodelete)
    execute_query(conn, sql)
        
    return "Delete request successful!"

#use PUT method for databse
@app.route('/api/snowboard', methods=['PUT'])
def api_update_snowboardDB():
    request_data = request.get_json()
    IDupdate = request_data['id']
    boardtypeUpdate = request_data['boardtype']
    brandUpdate = request_data['brand']
    MSRPupdate = request_data['msrp']
    Sizeupdate = request_data['size']
    myCreds = creds.Creds()
    conn = create_connection(myCreds.connectionstring, myCreds.username, myCreds.passwd, myCreds.dataBase)
    sql = "update snowboard set boardtype = '%s',brand = '%s', msrp = %s, size = %s where id = %s" % (boardtypeUpdate,brandUpdate,MSRPupdate,Sizeupdate,IDupdate)
    execute_query(conn, sql)

    return 'Update request Successful' #  message confirming the update request

app.run()
