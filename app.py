# File contains Routing information for the app
# Basically, what methods to be called when a given
# url is visited


# Flask is a web framework for python
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

import requests
import os
import json

from datetime import datetime
from datetime import timedelta

# from 'api.py' file import the following methods
from api import (generate_token, 
          get_profile_info, 
          get_subscription_info,
          create_new_order,
          get_order_info,
          delete_order,
          delete_order_all
          )

# from 'mongo.py' file import the following methods
from mongo import add_user


app = Flask(__name__) # initiate a Flask app. 
CORS(app) # allow cross origin requests 

@app.route('/auth/login')  # When https://*domain*/auth/login is visited run the following method
def register_amazon():
  # login.html contains the registration screen for amazon
  return render_template('login.html')


@app.route('/auth/redirect', methods=['GET']) # When https://*domain*/auth/redirect is visited run the following method
def register_amazon_redirect():
  
  # the redirect url will also contain parameters such as 'code' and 'scope'
  # so save it into a dictionary
  data = {
      'code': request.args.get('code', None),
      'scope': request.args.get('scope', None)
  }
  # get token from the 'code'
  token_data = generate_token(data.get('code'))
  # get profile datra from access_token which is available in token data
  profile =  get_profile_info(token_data.get('access_token'))
  
  # create a new user from all the details available
  user = {
    'access_token' : token_data.get('access_token'),
    'refresh_token' : token_data.get('refresh_token'),
    'token_created_date' : datetime.now(),
    'token_expiry_date' : datetime.now() + timedelta(seconds = token_data['expires_in']),
    'email' : profile.get('email'),
    'name' : profile.get('name'),
    'user_id' : profile.get('user_id')
  }
  
  # add a new user to the mongoDB
  add_user(user)
  
  # finally return a html file
  return render_template('auth_redirect.html')


@app.route('/subscription/<int:id>') # When for example https://*domain*/subscription/123 is visited run the following method
def subscription(id):
  result = get_subscription_info(id)
  # return the subscription info
  return jsonify(result)


@app.route('/replenish/<int:id>/<string:slot_id>') # When for example https://*domain*/replenish/123/2 is visited run the following method
def replenish(id, slot_id):
  result  = create_new_order(id, slot_id) # example: create_new_order(123, 2) : place order for slot 2, for user 123
  return jsonify(result)  


@app.route('/order-status/<int:id>/<string:instance_id>') # get order status for a given user 'id' and 'instance id'
def order_status(id, instance_id):
  result  = get_order_info(id, instance_id)
  return jsonify(result)  


@app.route('/cancel-order/<int:id>/<string:slot_id>') # cancel order method is ran when this url is visited
def cancel_order(id, slot_id):
  result  = delete_order(id, slot_id)
  return jsonify(result)

@app.route('/cancel-order-all/<int:id>') # cancel all orders method is ran when this url is visited
def cancel_order_all(id):
  result  = delete_order_all(id)
  return jsonify(result)  

@app.route('/') # when https://*domain*/ is visited run the 'dashboard' method which returns 'dashboard.html' for user id: 1
def dashboard():
  return render_template('dashboard.html', user_id = 1)


@app.route('/<int:user_id>') # when https://*domain*/76 is visited run the 'dashboard' method which returns 'dashboard.html' for user id: 76
def dashboard_generic(user_id):
  return render_template('dashboard.html', user_id = user_id)


if __name__ == "__main__":
  # set the port for the service: eg: https://*domain*:5000/
  port = os.environ.get('PORT', 5000)
  
  # start the FLASK app. Now you can visit for example https://*domain*:5000/ 
  app.run(host='0.0.0.0', port=port, debug=True)
