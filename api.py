# Import all the required libraries
import requests
import os 
import json
from mongo import get_user_details, update_token
from datetime import datetime
from datetime import timedelta

# URI to authenticate yourself into amazon API services
AMAZON_OAUTH2_URI = 'https://api.amazon.com/auth/o2/token'
# URI for DR services
DRS_BASE_URI = 'https://dash-replenishment-service-na.amazon.com'

# method used to generate token
def generate_token(code):
  '''
  takes a auth code as parameter
  and returns new token
  '''  
  client_id = os.environ.get('CLIENT_ID') # get client id
  client_secret = os.environ.get('CLIENT_SECRET') # get client secret
  redirect_url = os.environ.get('REDIRECT_URL') # get the redirect url for the app
  
  # we need to send the following payload to the 
  # API during the POST request
  payload = {
      'grant_type': 'authorization_code',
      'code': code,
      'client_id': client_id,
      'client_secret': client_secret,
      'redirect_url': redirect_url
  }
  
  # make the post request
  r = requests.post(AMAZON_OAUTH2_URI, data=payload)
  
  # post request is succesfully made,
  # 'r.text' is the string response
  # so convert into object by using 'json.loads' function
  return json.loads(r.text)



# periodically update access token to let the
# connection to the API stay active
def get_and_update_token(id, refresh_token):
  '''
  create, update and return access_token
  '''
  
  client_id = os.environ.get('CLIENT_ID')
  client_secret = os.environ.get('CLIENT_SECRET')
  redirect_url = os.environ.get('REDIRECT_URL')

  # we need to send the following payload to the 
  # API during the POST request
  payload = {
      'grant_type': 'refresh_token',
      'refresh_token': refresh_token,
      'client_id': client_id,
      'client_secret': client_secret,
      'redirect_url': redirect_url
  }
  
  # make the post request
  r = requests.post(AMAZON_OAUTH2_URI, data=payload)
  
  # post request is succesfully made,
  # 'r.text' is the string response
  # so convert into object by using 'json.loads' function
  token_data = json.loads(r.text)
  
  # create a new token using data from 'token_data'
  token = {
      'access_token': token_data.get('access_token'),
      'refresh_token': token_data.get('refresh_token'),
      'token_created_date': datetime.now(), # method used to get current timestamp
      'token_expiry_date': datetime.now() + timedelta(seconds=token_data['expires_in']) # caluclate expiry date (usually 1 hour)
  }
  
  # now new token is generated,
  # use it to update the previous token
  update_token(id, token)
  
  # finally return the new token created
  return token_data.get('access_token')


# use the 'get_and_update_token' to generate and
# return new access token if previous token
# is expired
def get_access_token(id):
  '''
  return token or renew and return token 
  '''
  
  user = get_user_details(id) # from the id get user details
  access_token = user.get('access_token')
  refresh_token = user.get('refresh_token')
  token_expiry_date = user.get('token_expiry_date')
  now = datetime.now() # get current timestamp

  if now < token_expiry_date:  
    # token's not expired yet,
    # so return old but valid token
    return access_token
  else:  
    # toekn's expired,
    # so update and return new token
    access_token = get_and_update_token(id, refresh_token)
    
  return access_token


def get_subscription_info(id):
  """
    returns the subscription info for 
    a given 'id'
  """  
  access_token = get_access_token(id) # get access token
  
  # create 'headers' needed to send to 
  # the API during the 'GET' request
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsSubscriptionInfoResult@2.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsSubscriptionInfoInput@1.0'
  }
  
  # make the GET request
  r = requests.get(DRS_BASE_URI + '/subscriptionInfo', headers=headers)
  
  return json.loads(r.text)


def create_new_order(id, slot_id):
  """
    create a new order for the given 'slot_id'
  """
  
  access_token = get_access_token(id) # get access token for the given 'id'
  
  # create 'headers' needed to send to 
  # the API during the 'POST' request
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsReplenishResult@1.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsReplenishInput@1.0'
  }
  
  # maket the POST request to DRS Replenish
  r = requests.post(
      DRS_BASE_URI + '/replenish/{}'.format(slot_id), headers=headers)
  
  # return the results
  return json.loads(r.text)


def get_order_info(id, instance_id):
  """
    return order info for a given 'instance_id'
  """
  
  access_token = get_access_token(id)
  
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsOrderInfoResult@1.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsOrderInfoInput@1.0'
  }
  # make GET request to DRS orderInfo
  r = requests.get(
      DRS_BASE_URI + '/getOrderInfo/{}'.format(instance_id), headers=headers)
  return json.loads(r.text)


def delete_order(id, slot_id):
  """
    deletes an active order for the given 'slot_id'
  """
  
  access_token = get_access_token(id)
  
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsCancelTestOrdersResult@1.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsCancelTestOrdersInput@1.0'
  }
  
  # make a DELETE request to DRS
  r = requests.delete(
      DRS_BASE_URI + '/testOrders/slots/{}'.format(slot_id), headers=headers)
  
  return json.loads(r.text)

def delete_order_all(id):
  """
    delete all orders placed by user with id: 'id'
  """
  
  access_token = get_access_token(id)
  
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsCancelTestOrdersResult@1.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsCancelTestOrdersInput@1.0'
  }
  
  r = requests.delete(
      DRS_BASE_URI + '/testOrders', headers=headers)
  
  return json.loads(r.text)


def get_profile_info(access_token=None, id=None):
  """
    returns the profile info for a 
    given 'access_token' or 'id'
  """
  if not access_token:
    if id:
      # fetch access_token
      access_token = get_access_token(id)
    else:
      # if no access_token and no id, then
      return None
      
  headers = {
      'x-amz-access-token': access_token
  }
  
  r = requests.get('https://api.amazon.com/user/profile', headers=headers)
  
  # return profile results
  return json.loads(r.text)
