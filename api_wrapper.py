import vk_api
from typing import Optional, Union

from config import default_key


def get_name_by_id(target_id : int, api : vk_api.vk_api.VkApiMethod) -> str:
    info = api.users.get(user_ids = target_id, lang="ru")[0]
    return info["first_name"] + " " + info["last_name"]


def get_chat_info(chat_id : int, api : vk_api.vk_api.VkApiMethod):
    data = api.messages.getHistory(user_id = chat_id)
    return data["items"]

def user_is_in_community(api : vk_api.vk_api.VkApiMethod, user_id : int, group_id : Union[int, str] = "math_jokes00") -> bool:  # Group is Mathematical_jokes by default
    return bool(api.groups.isMember(group_id = group_id, user_id = user_id))


if __name__ == '__main__':
    session = vk_api.VkApi(token = default_key)
    vk = session.get_api()

    print(user_is_in_community(vk, 215659697, "math_jokes00"))
    print(user_is_in_community(vk, 155277564, "math_jokes00"))
    print(user_is_in_community(vk, 200792183, "math_jokes00"))
