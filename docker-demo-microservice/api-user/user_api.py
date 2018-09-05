# -*- coding: utf-8 -*-
# since   : 2018-08-22
# author  : ZedOptima

import logging
import socket

from datetime   import datetime

from bson       import ObjectId
from flask      import Flask
from flask      import jsonify
from flask      import request
from redis      import Redis
from redis      import RedisError
from pymongo    import MongoClient

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)
mongo = MongoClient('mongodb://mongodb:27017')
app   = Flask(__name__)


def init():
  # Initialize database for the first time
  database  = mongo.get_database('test')

  # Create the indexes
  database.get_collection('users').drop_indexes()
  database.get_collection('users').create_index([('username', 1)], unique=True)


init()


@app.route("/")
def get_application_properties():
  app_properties = \
    {
      'name'      : 'User API'
      , 'version' : '1.0.0'
    }

  return jsonify(app_properties)


@app.route("/api/summary")
def get_api_calls_summary():
  increment_redis_counter()
  total_calls = get_redis_counter()

  result = \
    {
      'total_calls' : total_calls
    }

  json_response = build_json_response(result=result)

  return json_response


@app.route("/register", methods=['POST'])
def register():
  username    = request.form.get('username')
  password    = request.form.get('password')
  first_name  = request.form.get('first_name' , '')
  last_name   = request.form.get('last_name'  , '')
  created_dt  = datetime.now()
  modified_dt = created_dt

  user = \
    {
      'username'      : username
      , 'password'    : password
      , 'first_name'  : first_name
      , 'last_name'   : last_name
      , 'created_dt'  : created_dt
      , 'modified_dt' : modified_dt
    }

  database      = mongo.get_database('test')
  coll          = database.get_collection('users')
  db_result     = coll.insert_one(user)

  acknowledged  = db_result.acknowledged
  inserted_id   = db_result.inserted_id

  user.pop('_id')
  user.pop('password')
  user['id']    = str(inserted_id)

  json_response = build_json_response(message='User registered successfully.', result=user)

  return json_response


@app.route("/login", methods=['POST'])
def login():
  username  = request.form.get('username')
  password  = request.form.get('password')

  database  = mongo.get_database('test')
  coll      = database.get_collection('users')
  user      = coll.find_one({'username' : username})

  status  = 'failed'
  code    = 400
  count   = 0

  if user is not None:
    user_id         = str(user.get('_id'))
    saved_password  = user.get('password')

    first_name      = user.get('first_name'     , '')
    last_name       = user.get('last_name'      , '')
    created_dt      = str(user.get('created_dt' , ''))
    modified_dt     = str(user.get('modified_dt', ''))

    if password == saved_password:
      status  = 'success'
      code    = 200
      count   = 1
      message = 'Ok'
      result  = \
        {
          'id'            : user_id
          , 'first_name'  : first_name
          , 'last_name'   : last_name
          , 'created_dt'  : created_dt
          , 'modified_dt' : modified_dt
        }
    else:
      code    = 401
      message = 'Invalid user credentials.'
      result  = \
        {
          'metadata'  : get_host_metadata()
        }
  else:
    message = 'User not found.'
    result  = \
      {
        'metadata'  : get_host_metadata()
      }

  json_response = build_json_response(status=status, code=code, message=message, count=count, result=result)

  return json_response


@app.route("/users/<user_id>", methods=['GET'])
def get_user(user_id):
  database  = mongo.get_database('test')
  coll      = database.get_collection('users')
  user      = coll.find_one({'_id' : ObjectId(user_id)})

  status  = 'failed'
  code    = 400
  count   = 0

  if user is not None:
    user_id         = str(user.get('_id'))

    first_name      = user.get('first_name'     , '')
    last_name       = user.get('last_name'      , '')
    created_dt      = str(user.get('created_dt' , ''))
    modified_dt     = str(user.get('modified_dt', ''))

    status  = 'success'
    code    = 200
    count   = 1
    message = 'Ok'
    result  = \
      {
        'id'            : user_id
        , 'first_name'  : first_name
        , 'last_name'   : last_name
        , 'created_dt'  : created_dt
        , 'modified_dt' : modified_dt
      }
  else:
    message = 'User not found.'
    result  = \
      {
        'metadata'  : get_host_metadata()
      }

  json_response = build_json_response(status=status, code=code, message=message, count=count, result=result)

  return json_response


def build_json_response(status    = 'success'
                        , code    = 200
                        , message = 'Ok'
                        , count   = None
                        , result  = None):
  json_result = \
    {
      'status'      : status
      , 'code'      : code
      , 'message'   : message
      , 'metadata'  : get_host_metadata()
    }

  if count is not None:
    json_result['count'] = count
  else:
    pass

  if result is not None:
    json_result['result'] = result
  else:
    pass

  return jsonify(json_result)


def get_host_metadata():
  hostname = socket.gethostname()

  metadata = \
    {
      'hostname' : hostname
    }

  return metadata


def increment_redis_counter():
  try:
    redis.incr('counter')
  except RedisError:
    logging.info('<i>Cannot connect to Redis, counter disabled</i>')


def get_redis_counter():
  try:
    return redis.incr('counter')
  except RedisError:
    logging.info('<i>Cannot connect to Redis, counter disabled</i>')
    return 0


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8001)
