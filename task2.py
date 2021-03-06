# access_token=2b1d954236b68015ec94a0be8265c67565316b6ec987b78a1d3292e65c02096b549821b5d5cea05b9b744
# https://api.vk.com/method/groups.get?user_id=57263194&access_token=2b1d954236b68015ec94a0be8265c67565316b6ec987b78a1d3292e65c02096b549821b5d5cea05b9b744&v=5.52

import requests
from pprint import pprint
import json
main_link = 'https://api.vk.com/method/groups.get'
params = {'user_id':'57263194',
          'access_token':'2b1d954236b68015ec94a0be8265c67565316b6ec987b78a1d3292e65c02096b549821b5d5cea05b9b744',
          'v':'5.52'}

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36'}
response = requests.get(main_link, params=params, headers=headers)
j_body = response.json()

pprint(j_body)

with open('vk_groups_id.json', 'w') as f:
    json.dump(response.json(), f)

