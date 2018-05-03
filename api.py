import requests
import os
import json
from mongo import get_user_details, update_token
from datetime import datetime
from datetime import timedelta

AMAZON_OAUTH2_URI = 'https://api.amazon.com/auth/o2/token'
DRS_BASE_URI = 'https://dash-replenishment-service-na.amazon.com'

def generate_token(code):
  '''
  generates new token from auth code 
  '''
  client_id = os.environ.get('CLIENT_ID')
  client_secret = os.environ.get('CLIENT_SECRET')
  redirect_url = os.environ.get('REDIRECT_URL')

  payload = {
      'grant_type': 'authorization_code',
      'code': code,
      'client_id': client_id,
      'client_secret': client_secret,
      'redirect_url': redirect_url
  }
  
  r = requests.post(AMAZON_OAUTH2_URI, data=payload)
  return json.loads(r.text)


def get_and_update_token(id, refresh_token):
  '''
  renew token 
  '''
  client_id = os.environ.get('CLIENT_ID')
  client_secret = os.environ.get('CLIENT_SECRET')
  redirect_url = os.environ.get('REDIRECT_URL')

  payload = {
      'grant_type': 'refresh_token',
      'refresh_token': refresh_token,
      'client_id': client_id,
      'client_secret': client_secret,
      'redirect_url': redirect_url
  }

  r = requests.post(AMAZON_OAUTH2_URI, data=payload)
  token_data = json.loads(r.text)
  token = {
      'access_token': token_data.get('access_token'),
      'refresh_token': token_data.get('refresh_token'),
      'token_created_date': datetime.now(),
      'token_expiry_date': datetime.now() + timedelta(seconds=token_data['expires_in'])
  }
  update_token(id, token)
  return token_data.get('access_token')


def get_access_token(id):
  '''
  return token or renew and return token 
  '''
  user = get_user_details(id)
  access_token = user.get('access_token')
  refresh_token = user.get('refresh_token')
  token_expiry_date = user.get('token_expiry_date')
  now = datetime.now()

  if now < token_expiry_date:  # return old but valid token
    return access_token
  else:  # update and return new token
    access_token = get_and_update_token(id, refresh_token)
  return access_token


def get_subscription_info(id):
  access_token = get_access_token(id)
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsSubscriptionInfoResult@2.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsSubscriptionInfoInput@1.0'
  }
  r = requests.get(DRS_BASE_URI + '/subscriptionInfo', headers=headers)
  return json.loads(r.text)


def create_new_order(id, slot_id):
  access_token = get_access_token(id)
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsReplenishResult@1.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsReplenishInput@1.0'
  }
  r = requests.post(
      DRS_BASE_URI + '/replenish/{}'.format(slot_id), headers=headers)
  return json.loads(r.text)


def get_order_info(id, instance_id):
  access_token = get_access_token(id)
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsOrderInfoResult@1.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsOrderInfoInput@1.0'
  }
  r = requests.get(
      DRS_BASE_URI + '/getOrderInfo/{}'.format(instance_id), headers=headers)
  return json.loads(r.text)


def delete_order(id, slot_id):
  access_token = get_access_token(id)
  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'x-amzn-accept-type': 'com.amazon.dash.replenishment.DrsCancelTestOrdersResult@1.0',
      'x-amzn-type-version': 'com.amazon.dash.replenishment.DrsCancelTestOrdersInput@1.0'
  }
  r = requests.delete(
      DRS_BASE_URI + '/testOrders/slots/{}'.format(slot_id), headers=headers)
  return json.loads(r.text)


def get_profile_info(access_token=None, id=None):
  if not access_token:
    if id:
      access_token = get_access_token(id)
    else:
      return None
  headers = {
      'x-amz-access-token': access_token
  }

  r = requests.get('https://api.amazon.com/user/profile', headers=headers)
  return json.loads(r.text)
