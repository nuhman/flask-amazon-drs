from pymongo import MongoClient
from datetime import datetime
import os

db_url = 'mongodb://{}:{}@ds111410.mlab.com:11410/iot'.format(
    os.environ.get('MONGO_USERNAME'), os.environ.get('MONGO_PASSWORD'))

client = MongoClient(db_url)

user_db = client.iot.get_collection('user_db')


def add_user(user):
  count = user_db.count()
  if not user_db.find_one({'user_id': user.get('user_id')}):
    user['id'] = count + 1
    user_db.insert_one(user)


def update_token(id, token):
  return user_db.update_one({'id':id}, {'$set': token})



def get_user_details(id):
  return user_db.find_one({'id': id})
