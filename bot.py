import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды:\n"
                                  "/show_city [город] - Показать город на карте\n"
                                  "/remember_city [город] - Запомнить город\n"
                                  "/show_my_cities - Показать все сохраненные города")

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    image_path = manager.get_city_map(city_name)
    
    if image_path and os.path.exists(image_path):  # Проверяем, существует ли файл
        with open(image_path, "rb") as image:
            bot.send_photo(message.chat.id, image, caption=f"Карта города {city_name}")
    else:
        bot.send_message(message.chat.id, "Не удалось найти или создать карту города.")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажите название города после команды.")
        return
    city_name = parts[1]
    user_id = message.chat.id
    if manager.add_city(user_id, city_name):
        bot.send_message(user_id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(user_id, 'Такого города я не знаю. Убедитесь, что он написан правильно!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_my_cities(message):
    cities = manager.select_cities(message.chat.id)
    map_image = manager.get_multiple_cities_map(cities)

    if map_image and os.path.exists(map_image):
        with open(map_image, "rb") as image:
            bot.send_photo(message.chat.id, image, caption="Ваши сохраненные города.")
    else:
        bot.send_message(message.chat.id, "Карта не создана или файл отсутствует.")


manager = DB_Map(DATABASE)
bot.polling()