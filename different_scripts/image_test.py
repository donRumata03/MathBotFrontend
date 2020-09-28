from config import *

import vk_api

from mylang import print_as_json

session = vk_api.VkApi(token = default_key)

vk = session.get_api()

upload = vk_api.VkUpload(session)
attachments = []


photo_container = upload.photo_messages(photos=r"D:\Projects\Math_bot\results\_examples\plotting_example.png", peer_id = 215659697)[0]

print_as_json(photo_container)

attachments.append(f"photo{photo_container['owner_id']}_{photo_container['id']}")

vk.messages.send(
    user_id = 215659697,
    attachment = ",".join(attachments),
    random_id = vk_api.utils.get_random_id()
)

