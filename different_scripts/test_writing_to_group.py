import vk_api
from config import *

session = vk_api.VkApi(token = default_key)
vk = session.get_api()

vk.messages.send(
            message = "test",
            # peer_id = user_id,  # Could be user id, but to be more generic...
            random_id = vk_api.utils.get_random_id(),
            peer_id = 2000000000 + 2
)

