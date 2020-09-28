import vk
from config import *

session = vk.Session(access_token = default_key)
vk_api = vk.API(session)
print(vk_api.users.get(user_id=1, v = '5.103', lang = 'ru'))

