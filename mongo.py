"""
MongoDB setup - 'mlab.com'.
"""

from pymongo import MongoClient
from datetime import datetime
import os

db_url = 'mongodb://{}:{}@ds111410.mlab.com:11410/iot'.format(
    os.environ.get('MONGO_USERNAME'), os.environ.get('MONGO_PASSWORD'))

# set up connection to MongoDB client
client = MongoClient(db_url)

# In 'iot' db there is a mongo collection called 'user_db'
user_db = client.iot.get_collection('user_db')


def add_user(user):
  count = user_db.count() # get the current count
  if not user_db.find_one({'user_id': user.get('user_id')}):
    # if the 'user' doesn't exist in the collection yet, 
    # then add the user to the collection
    user['id'] = count + 1
    user_db.insert_one(user)


def update_token(id, token):
  return user_db.update_one({'id':id}, {'$set': token})



def get_user_details(id):
  return user_db.find_one({'id': id})
