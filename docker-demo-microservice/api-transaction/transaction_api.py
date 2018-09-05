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


@app.route("/")
def get_application_properties():
  app_properties = \
    {
      'name'      : 'Transaction API'
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


@app.route("/posts", methods=['POST'])
def create_post():
  user_id     = request.form.get('user_id')
  title       = request.form.get('title')
  content     = request.form.get('content')
  created_dt  = datetime.now()
  modified_dt = created_dt

  post = \
    {
      'user_id'       : ObjectId(user_id)
      , 'title'       : title
      , 'content'     : content
      , 'created_dt'  : created_dt
      , 'modified_dt' : modified_dt
    }

  database      = mongo.get_database('test')
  coll          = database.get_collection('posts')
  db_result     = coll.insert_one(post)

  acknowledged  = db_result.acknowledged
  inserted_id   = db_result.inserted_id

  user          = get_user(ObjectId(user_id))

  post.pop('_id')
  post.pop('user_id')
  post['id']          = str(inserted_id)
  post['created_by']  = user

  json_response = build_json_response(message='Post has been created', result=post)

  return json_response


@app.route("/posts/<post_id>", methods=['DELETE'])
def delete_post(post_id):
  database  = mongo.get_database('test')
  coll      = database.get_collection('posts')
  db_result = coll.delete_one({'_id' : ObjectId(post_id)})

  count     = db_result.deleted_count

  json_response = build_json_response(message='Post has been deleted', count=count)

  return json_response


@app.route("/posts/<post_id>", methods=['GET'])
def read_post(post_id):
  database  = mongo.get_database('test')
  coll      = database.get_collection('posts')
  post      = coll.find_one({'_id' : ObjectId(post_id)})

  status  = 'failed'
  code    = 404
  count   = 0

  if post is not None:
    post_id     = str(post.get('_id'))
    title       = post.get('title'          , '')
    content     = post.get('content'        , '')
    created_dt  = str(post.get('created_dt' , ''))
    modified_dt = str(post.get('modified_dt', ''))

    user_id     = post.get('user_id'        , None)
    user        = get_user(user_id)

    status  = 'success'
    code    = 200
    count   = 1
    message = 'Ok'
    result  = \
      {
        'id'            : post_id
        , 'title'       : title
        , 'content'     : content
        , 'created_dt'  : created_dt
        , 'modified_dt' : modified_dt
        , 'created_by'  : user
      }
  else:
    message = 'Post not found.'
    result  = \
      {
        'metadata'  : get_host_metadata()
      }

  json_response = build_json_response(status=status, code=code, message=message, count=count, result=result)

  return json_response


@app.route("/posts", methods=['GET'])
def list_posts():
  database  = mongo.get_database('test')
  coll      = database.get_collection('posts')
  db_cursor = coll.find()

  posts = []

  for post in db_cursor:
    post_id     = str(post.get('_id'))
    title       = post.get('title'          , '')
    content     = post.get('content'        , '')
    created_dt  = str(post.get('created_dt' , ''))
    modified_dt = str(post.get('modified_dt', ''))

    user_id     = post.get('user_id'        , None)
    user        = get_user(user_id)

    post = \
      {
        'id'            : post_id
        , 'title'       : title
        , 'content'     : content
        , 'created_dt'  : created_dt
        , 'modified_dt' : modified_dt
        , 'created_by'  : user
      }

    posts.append(post)

  count         = len(posts)
  json_response = build_json_response(count=count, result=posts)

  return json_response


def get_user(user_id):
  if user_id is None:
    return None

  database  = mongo.get_database('test')
  coll      = database.get_collection('users')
  user      = coll.find_one({'_id' : user_id})

  if user is not None:
    user_id         = str(user.get('_id'))

    first_name      = user.get('first_name'     , '')
    last_name       = user.get('last_name'      , '')
    created_dt      = str(user.get('created_dt' , ''))
    modified_dt     = str(user.get('modified_dt', ''))

    user = \
      {
        'id'            : user_id
        , 'first_name'  : first_name
        , 'last_name'   : last_name
      }

    return user
  else:
    return None


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
  app.run(host='0.0.0.0', port=8002)

