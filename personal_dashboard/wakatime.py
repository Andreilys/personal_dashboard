#!/usr/bin/env python

import hashlib
import os
import sys
from rauth import OAuth2Service
import requests
import base64


service = OAuth2Service(
    client_id='sxKaBRcw1Z89YmAnX3xsEKCk', # your App ID from https://wakatime.com/apps
    client_secret='sec_AiGlAEZTOrvwG0CNeZMbsZ7HRpMcXdbASO45HoF5Vgwrmb2UeUTvIwZrxtgI3c3z9ws1Brl6SciTu8Dn', # your App Secret from https://wakatime.com/apps
    name='wakatime',
    authorize_url='https://wakatime.com/oauth/authorize',
    access_token_url='https://wakatime.com/oauth/token',
    base_url='https://wakatime.com/api/v1/')

redirect_uri = 'https://wakatime.com/oauth/test'
state = hashlib.sha1(os.urandom(40)).hexdigest()
params = {'scope': 'email,read_stats,read_logged_time',
          'response_type': 'code',
          'state': state,
          'redirect_uri': redirect_uri}

url = service.get_authorize_url(**params)
#
# print('**** Visit {url} in your browser. ****'.format(url=url))
# print('**** After clicking Authorize, paste code here and press Enter ****')
# code = input('Enter code from url: ')
#
# # Make sure returned state has not changed for security reasons, and exchange
# # code for an Access Token.
# headers = {'Accept': 'application/x-www-form-urlencoded'}
# session = service.get_auth_session(headers=headers,
#                                    data={'code': code,
#                                          'grant_type': 'authorization_code',
#                                          'redirect_uri': redirect_uri})
# print(dir(session))
# print(session)
# print(session.access_token)
# print(session.access_token_key)
# # print(session.rebuild_auth())
# # print(session.rebuild_method())
# access_token = session.access_token_key
# print("-")
# print(access_token)
# print("-")
#
#
# user = session.get('users/current').json()
# print(user['data']['email'])
# stats = session.get('users/current/stats').json()
# print(stats.get('data', {}).get('human_readable_total', 'Calculating...'))


r = requests.get('https://wakatime.com/api/v1/users/current?api_key=eac4a89e-de12-4bd7-bb90-993364f13626')
print(r.status_code)
print(dir(r))
print(r.reason)
print(r.text)
b = requests.get('https://wakatime.com/api/v1/users/current/summaries?start=2017-10-03&end=2017-10-04?api_key=eac4a89e-de12-4bd7-bb90-993364f13626')
print(b.text)
print(b.reason)
