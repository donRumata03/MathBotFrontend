import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

key = "b8e34ba2603a410e101f19797d1ef3c412fb8c52a78580c05d7a20ac48e3a8ba1294dcba4ebf2cd9dcf9e"

good_key = "82066d27a1bd4961a16bf1cbf9a2ba48bbb55bd38a5340ce01db2f5e5b11b328b0d8de7c7f584d5e2b04a"

session = vk_api.VkApi(token=key)
vk = session.get_api()


keyboard = VkKeyboard(one_time=True)

keyboard.add_button('Белая кнопка', color = VkKeyboardColor.DEFAULT)
keyboard.add_button('Зелёная кнопка', color = VkKeyboardColor.POSITIVE)


keyboard.add_line()  # Переход на вторую строку
keyboard.add_location_button()


print(vk.messages.getConversations())


vk.messages.send(
    domain = "donrumata03",
    random_id = get_random_id(),
    keyboard = keyboard.get_keyboard(),
    message = 'Пример клавиатуры'
)
