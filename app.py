from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from datetime import datetime
from datetime import timedelta
from api import (generate_token, 
          get_profile_info, 
          get_subscription_info,
          create_new_order,
          get_order_info,
          delete_order
          )
from mongo import add_user

app = Flask(__name__)
CORS(app)


@app.route('/auth/login')
def register_amazon():
  return render_template('index.html')


@app.route('/auth/redirect', methods=['GET'])
def register_amazon_redirect():
  data = {
      'code': request.args.get('code', None),
      'scope': request.args.get('scope', None)
  }
  token_data = generate_token(data.get('code'))
  profile =  get_profile_info(token_data.get('access_token'))
  
  user = {
    'access_token' : token_data.get('access_token'),
    'refresh_token' : token_data.get('refresh_token'),
    'token_created_date' : datetime.now(),
    'token_expiry_date' : datetime.now() + timedelta(seconds = token_data['expires_in']),
    'email' : profile.get('email'),
    'name' : profile.get('name'),
    'user_id' : profile.get('user_id')
  }

  add_user(user)

  return render_template('auth_redirect.html')


@app.route('/subscription/<int:id>')
def subscription(id):
  result = get_subscription_info(id)
  return jsonify(result)


@app.route('/replenish/<int:id>/<string:slot_id>')
def replenish(id, slot_id):
  result  = create_new_order(id, slot_id)
  return jsonify(result)  


@app.route('/order-status/<int:id>/<string:instance_id>')
def order_status(id, instance_id):
  result  = get_order_info(id, instance_id)
  return jsonify(result)  


@app.route('/cancel-order/<int:id>/<string:slot_id>')
def cancel_order(id, slot_id):
  result  = delete_order(id, slot_id)
  return jsonify(result)  



if __name__ == "__main__":
  port = os.environ.get('PORT', 5000)
  app.run(host='0.0.0.0', port=port, debug=True)
