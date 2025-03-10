# -*- coding: utf-8 -*-

from flask import Flask
import threading
import telebot
import requests
import io
import logging

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)

# Ваш токен бота
TOKEN = '7367857619:AAGWyDbNaOprb7prmgGGoOgNE6Tzh-hGF7s'
BASE_URL = 'https://server-golosov.org/diya/'  # Базовый URL вашего сервера
ADMIN_USER_ID = 294413797
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователя
user_data = {}

# Маппинг полей (оставлен без изменений)
field_mapping = {
    "📝 Редактировать ФИО": "fio",
    "📝 Редактировать ФИО (EN)": "fio_en",
    "📅 Редактировать дату рождения": "birth",
    "🔍 Редактировать РНОКПП": "rnokpp",
    "📝 Редактировать номер паспорта": "pass_number",
    "📅 Редактировать дату выдачи паспорта": "date_give",
    "📅 Редактировать дату окончания паспорта": "date_out",
    "🏢 Редактировать орган выдачи паспорта": "organ",
    "🔍 Редактировать УЗНР": "uznr",
    "🌐 Редактировать прописку": "legalAdress",
    "📅 Редактировать дату регистрации": "registeredOn",
    "♂️ Редактировать пол": "sex",
    "♂️ Редактировать пол (EN)": "sex_en",
    "🏠 Редактировать место рождения": "live",
    "💳 Редактировать банковский адрес (ЕДокумент)": "bank_adress",
    "📝 Редактировать номер прав": "prava_number",
    "📅 Редактировать дату выдачи прав": "prava_date_give",
    "📅 Редактировать дату окончания прав": "prava_date_out",
    "✅ Редактировать статус прав": "prava_status",
    "🏢 Редактировать орган выдачи прав": "pravaOrgan",
    "🚗 Редактировать категории прав": "rights_categories",
    "📝 Редактировать номер студенческого": "student_number",
    "📅 Редактировать дату выдачи студенческого": "student_date_give",
    "📅 Редактировать дату окончания студенческого": "student_date_out",
    "📚 Редактировать форму обучения": "form",
    "✅ Редактировать статус студенческого": "study_status",
    "🏫 Редактировать университет": "university",
    "🏢 Редактировать факультет": "fakultet",
    "📝 Редактировать номер загранпаспорта": "zagran_number",
    "✅ Редактировать статус загранпаспорта": "zagran_status",
    "📝 Редактировать степень диплома": "stepen_dip",
    "🏫 Редактировать университет диплома": "univer_dip",
    "📅 Редактировать дату выдачи диплома": "dayout_dip",
    "🎓 Редактировать специальность диплома": "special_dip",
    "📝 Редактировать номер диплома": "number_dip",
    "✅ Редактировать статус диплома": "status_dip",
}

# Примеры значений (оставлены без изменений)
field_examples = {
    "📝 Редактировать ФИО": "Іванов Іван Іванович",
    "📝 Редактировать ФИО (EN)": "Ivanov Ivan Ivanovich",
    "📅 Редактировать дату рождения": "01.01.1990",
    "🔍 Редактировать РНОКПП": "11 символов",
    "📝 Редактировать номер паспорта": "АБ123456",
    "📅 Редактировать дату выдачи паспорта": "15.03.2015",
    "📅 Редактировать дату окончания паспорта": "15.03.2025",
    "🏢 Редактировать орган выдачи паспорта": "Отделение УФМС №123",
    "♂️ Редактировать пол": "Ч",
    "♂️ Редактировать пол (EN)": "M",
    "📝 Редактировать номер прав": "ВУ1234567",
    "🚗 Редактировать категории прав": "B, C",
    "📝 Редактировать номер студенческого": "СТ123456",
    "📚 Редактировать форму обучения": "Очна",
    "📝 Редактировать номер загранпаспорта": "12 3456789",
    "📝 Редактировать степень диплома": "Бакалавр",
    "🎓 Редактировать специальность диплома": "Информатика",
}


# Стартовое меню
def get_start_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("❓ FAQ"))
    markup.add(telebot.types.KeyboardButton("📖 Инструкция по установке"))
    markup.add(telebot.types.KeyboardButton("📋 Приложение"))
    return markup


# Главное меню
def get_main_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📋 Редактировать паспорт"))
    markup.add(telebot.types.KeyboardButton("🚗 Редактировать права"))
    markup.add(telebot.types.KeyboardButton("🎓 Редактировать студенческий"))
    markup.add(telebot.types.KeyboardButton("🌍 Редактировать загранпаспорт"))
    markup.add(telebot.types.KeyboardButton("🎓 Редактировать диплом"))
    markup.add(telebot.types.KeyboardButton("📷 Загрузить общую фотку"))
    if user_id == ADMIN_USER_ID:
        markup.add(telebot.types.KeyboardButton("🛠 Админ-панель"))
    markup.add(telebot.types.KeyboardButton("🔗 Получить ссылку"))
    markup.add(telebot.types.KeyboardButton("⬅️ Назад"))
    return markup


# Админ-панель с новой кнопкой для рассылки
def get_admin_panel():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🔄 Обновить сайт"))
    markup.add(telebot.types.KeyboardButton("📩 Создать рассылку"))
    markup.add(telebot.types.KeyboardButton("⬅️ Вернуться"))
    return markup


# Остальные функции меню (без изменений)
def get_passport_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📝 Редактировать ФИО"))
    markup.add(telebot.types.KeyboardButton("📝 Редактировать ФИО (EN)"))
    markup.add(telebot.types.KeyboardButton("📅 Редактировать дату рождения"))
    markup.add(telebot.types.KeyboardButton("🔍 Редактировать РНОКПП"))
    markup.add(telebot.types.KeyboardButton("📝 Редактировать номер паспорта"))
    markup.add(
        telebot.types.KeyboardButton("📅 Редактировать дату выдачи паспорта"))
    markup.add(
        telebot.types.KeyboardButton(
            "📅 Редактировать дату окончания паспорта"))
    markup.add(
        telebot.types.KeyboardButton("🏢 Редактировать орган выдачи паспорта"))
    markup.add(telebot.types.KeyboardButton("🔍 Редактировать УЗНР"))
    markup.add(telebot.types.KeyboardButton("🌐 Редактировать прописку"))
    markup.add(
        telebot.types.KeyboardButton("📅 Редактировать дату регистрации"))
    markup.add(telebot.types.KeyboardButton("♂️ Редактировать пол"))
    markup.add(telebot.types.KeyboardButton("♂️ Редактировать пол (EN)"))
    markup.add(telebot.types.KeyboardButton("🏠 Редактировать место рождения"))
    markup.add(
        telebot.types.KeyboardButton(
            "💳 Редактировать банковский адрес (ЕДокумент)"))
    markup.add(telebot.types.KeyboardButton("⬅️ Вернуться"))
    return markup


def get_prava_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📝 Редактировать номер прав"))
    markup.add(
        telebot.types.KeyboardButton("📅 Редактировать дату выдачи прав"))
    markup.add(
        telebot.types.KeyboardButton("📅 Редактировать дату окончания прав"))
    markup.add(telebot.types.KeyboardButton("✅ Редактировать статус прав"))
    markup.add(
        telebot.types.KeyboardButton("🏢 Редактировать орган выдачи прав"))
    markup.add(telebot.types.KeyboardButton("🚗 Редактировать категории прав"))
    markup.add(telebot.types.KeyboardButton("🔄 Показать права"))
    markup.add(telebot.types.KeyboardButton("🔄 Скрыть права"))
    markup.add(telebot.types.KeyboardButton("⬅️ Вернуться"))
    return markup


def get_student_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton("📝 Редактировать номер студенческого"))
    markup.add(
        telebot.types.KeyboardButton(
            "📅 Редактировать дату выдачи студенческого"))
    markup.add(
        telebot.types.KeyboardButton(
            "📅 Редактировать дату окончания студенческого"))
    markup.add(telebot.types.KeyboardButton("📚 Редактировать форму обучения"))
    markup.add(
        telebot.types.KeyboardButton("✅ Редактировать статус студенческого"))
    markup.add(telebot.types.KeyboardButton("🏫 Редактировать университет"))
    markup.add(telebot.types.KeyboardButton("🏢 Редактировать факультет"))
    markup.add(telebot.types.KeyboardButton("🔄 Показать студенческий"))
    markup.add(telebot.types.KeyboardButton("🔄 Скрыть студенческий"))
    markup.add(telebot.types.KeyboardButton("⬅️ Вернуться"))
    return markup


def get_zagran_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton("📝 Редактировать номер загранпаспорта"))
    markup.add(
        telebot.types.KeyboardButton("✅ Редактировать статус загранпаспорта"))
    markup.add(telebot.types.KeyboardButton("🔄 Показать загранпаспорт"))
    markup.add(telebot.types.KeyboardButton("🔄 Скрыть загранпаспорт"))
    markup.add(telebot.types.KeyboardButton("⬅️ Вернуться"))
    return markup


def get_diploma_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📝 Редактировать степень диплома"))
    markup.add(
        telebot.types.KeyboardButton("🏫 Редактировать университет диплома"))
    markup.add(
        telebot.types.KeyboardButton("📅 Редактировать дату выдачи диплома"))
    markup.add(
        telebot.types.KeyboardButton("🎓 Редактировать специальность диплома"))
    markup.add(telebot.types.KeyboardButton("📝 Редактировать номер диплома"))
    markup.add(telebot.types.KeyboardButton("✅ Редактировать статус диплома"))
    markup.add(telebot.types.KeyboardButton("🔄 Показать диплом"))
    markup.add(telebot.types.KeyboardButton("🔄 Скрыть диплом"))
    markup.add(telebot.types.KeyboardButton("⬅️ Вернуться"))
    return markup


# Функции для работы с документами (без изменений)
def update_document_status(user_id, field, value):
    response = requests.post(f"{BASE_URL}api/update.php",
                             data={
                                 'user_id': user_id,
                                 'field': field,
                                 'value': value
                             })
    return response.status_code == 200 and response.json().get(
        'status') == 'success'


def show_document(message, field, document_name, menu_callback):
    user_id = message.from_user.id
    if update_document_status(user_id, field, 'True'):
        bot.send_message(
            message.chat.id,
            f"{document_name} показан! Перезапустите приложение 🎉",
            reply_markup=menu_callback(user_id))
    else:
        bot.send_message(message.chat.id,
                         "Ошибка при изменении статуса. Проверьте сервер.")


def hide_document(message, field, document_name, menu_callback):
    user_id = message.from_user.id
    if update_document_status(user_id, field, 'False'):
        bot.send_message(message.chat.id,
                         f"{document_name} скрыт! Перезапустите приложение 🎉",
                         reply_markup=menu_callback(user_id))
    else:
        bot.send_message(message.chat.id,
                         "Ошибка при изменении статуса. Проверьте сервер.")


# Проверка регистрации
def is_registered(user_id):
    response = requests.get(
        f"{BASE_URL}api/get_unique_id.php?user_id={user_id}")
    return response.text.strip() != "not_found"


# Получение списка всех пользователей на основе папок
def get_all_users():
    response = requests.get(f"{BASE_URL}api/get_all_users.php")
    if response.status_code == 200:
        return response.json().get('users', [])
    return []


# Обработчики сообщений
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    link = f"{BASE_URL}data/{user_id}/"
    if is_registered(user_id):
        bot.send_message(
            message.chat.id,
            f"Вы успешно авторизированы! 🎉 Ваша уникальная ссылка: {link}")
    else:
        response = requests.post(f"{BASE_URL}api/register.php",
                                 data={
                                     'user_id': user_id,
                                     'unique_id': str(user_id)
                                 })
        result = response.json()
        if result['status'] == 'success':
            bot.send_message(
                message.chat.id,
                f"Приложение успешно создано! 🎉 Ваша уникальная ссылка: {link}"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"Ошибка при создании приложения: {result.get('message', 'Неизвестная ошибка')}"
            )
    bot.send_message(message.chat.id,
                     "Добро пожаловать! Выберите действие:",
                     reply_markup=get_start_menu())


@bot.message_handler(func=lambda message: message.text == "❓ FAQ")
def faq(message):
    bot.send_message(message.chat.id,
                     "📚 FAQ: https://telegra.ph/FAQ-Fejk-D%D1%96ya-11-07",
                     reply_markup=get_start_menu())


@bot.message_handler(
    func=lambda message: message.text == "📖 Инструкция по установке")
def instructions(message):
    bot.send_message(
        message.chat.id,
        "📖 Инструкция по установке: https://telegra.ph/Vstanovlennya-Fejk-D%D1%96i-11-07",
        reply_markup=get_start_menu())


@bot.message_handler(func=lambda message: message.text == "📋 Приложение")
def app_menu(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
                     "Выберите раздел для редактирования:",
                     reply_markup=get_main_menu(user_id))


@bot.message_handler(
    func=lambda message: message.text == "📋 Редактировать паспорт")
def edit_passport(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
                     "Редактирование паспорта:",
                     reply_markup=get_passport_menu(user_id))


@bot.message_handler(
    func=lambda message: message.text == "🚗 Редактировать права")
def edit_prava(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
                     "Редактирование прав:",
                     reply_markup=get_prava_menu(user_id))


@bot.message_handler(
    func=lambda message: message.text == "🎓 Редактировать студенческий")
def edit_student(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
                     "Редактирование студенческого:",
                     reply_markup=get_student_menu(user_id))


@bot.message_handler(
    func=lambda message: message.text == "🌍 Редактировать загранпаспорт")
def edit_zagran(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
                     "Редактирование загранпаспорта:",
                     reply_markup=get_zagran_menu(user_id))


@bot.message_handler(
    func=lambda message: message.text == "🎓 Редактировать диплом")
def edit_diploma(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
                     "Редактирование диплома:",
                     reply_markup=get_diploma_menu(user_id))


@bot.message_handler(
    func=lambda message: message.text == "📷 Загрузить общую фотку")
def upload_photo_main(message):
    user_id = message.from_user.id
    user_data[user_id] = {'state': 'awaiting_photo'}
    bot.send_message(message.chat.id,
                     "Отправьте общую фотку для всех документов.")


@bot.message_handler(func=lambda message: message.text == "🔗 Получить ссылку")
def get_link_main(message):
    user_id = message.from_user.id
    link = f"{BASE_URL}data/{user_id}/"
    bot.send_message(message.chat.id,
                     "🎉 Ваша уникальная ссылка: " + link,
                     reply_markup=get_main_menu(user_id))


@bot.message_handler(
    func=lambda message: message.text in ["⬅️ Вернуться", "⬅️ Назад"])
def back(message):
    user_id = message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    # Если пользователь в главном меню, возвращаем стартовое меню
    bot.send_message(message.chat.id,
                     "Возврат в стартовое меню.",
                     reply_markup=get_start_menu())


@bot.message_handler(func=lambda message: "Редактировать" in message.text)
def edit_field(message):
    fieldo = message.text
    field = field_mapping.get(fieldo, None)
    if field:
        user_id = message.from_user.id
        example = field_examples.get(fieldo, "нет примера")
        user_data[user_id] = {
            'field': field,
            'state': 'awaiting_input',
            'fieldo': fieldo
        }
        bot.send_message(
            message.chat.id,
            f"Введите новое значение для {fieldo} (пример: {example}):")
    else:
        bot.send_message(message.chat.id,
                         "Ошибка: Неизвестное поле для редактирования.")


@bot.message_handler(func=lambda message: message.text == "🛠 Админ-панель")
def admin_panel(message):
    user_id = message.from_user.id
    if user_id == ADMIN_USER_ID:
        bot.send_message(message.chat.id,
                         "Добро пожаловать в админ-панель!",
                         reply_markup=get_admin_panel())
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к админ-панели.")


@bot.message_handler(func=lambda message: message.text == "🔄 Обновить сайт")
def update_site(message):
    user_id = message.from_user.id
    if user_id == ADMIN_USER_ID:
        response = requests.post(f"{BASE_URL}api/update_site.php")
        if response.status_code == 200 and response.json().get(
                'status') == 'success':
            bot.send_message(message.chat.id,
                             "Сайт успешно обновлен для всех пользователей!",
                             reply_markup=get_admin_panel())
        else:
            bot.send_message(
                message.chat.id,
                f"Ошибка при обновлении сайта: {response.json().get('message', 'Неизвестная ошибка')}"
            )
    else:
        bot.send_message(message.chat.id,
                         "У вас нет прав для выполнения этой команды.")


@bot.message_handler(func=lambda message: message.text == "📩 Создать рассылку")
def start_broadcast(message):
    user_id = message.from_user.id
    if user_id == ADMIN_USER_ID:
        user_data[user_id] = {'state': 'awaiting_broadcast_message'}
        bot.send_message(message.chat.id,
                         "Введите текст для рассылки всем пользователям:")
    else:
        bot.send_message(message.chat.id,
                         "У вас нет прав для выполнения этой команды.")


@bot.message_handler(func=lambda message: message.text == "🔄 Показать права")
def show_prava(message):
    show_document(message, 'prava_status', "Права", get_prava_menu)


@bot.message_handler(func=lambda message: message.text == "🔄 Скрыть права")
def hide_prava(message):
    hide_document(message, 'prava_status', "Права", get_prava_menu)


@bot.message_handler(
    func=lambda message: message.text == "🔄 Показать студенческий")
def show_student(message):
    show_document(message, 'study_status', "Студенческий билет",
                  get_student_menu)


@bot.message_handler(
    func=lambda message: message.text == "🔄 Скрыть студенческий")
def hide_student(message):
    hide_document(message, 'study_status', "Студенческий билет",
                  get_student_menu)


@bot.message_handler(
    func=lambda message: message.text == "🔄 Показать загранпаспорт")
def show_zagran(message):
    show_document(message, 'zagran_status', "Загранпаспорт", get_zagran_menu)


@bot.message_handler(
    func=lambda message: message.text == "🔄 Скрыть загранпаспорт")
def hide_zagran(message):
    hide_document(message, 'zagran_status', "Загранпаспорт", get_zagran_menu)


@bot.message_handler(func=lambda message: message.text == "🔄 Показать диплом")
def show_diploma(message):
    show_document(message, 'status_dip', "Диплом", get_diploma_menu)


@bot.message_handler(func=lambda message: message.text == "🔄 Скрыть диплом")
def hide_diploma(message):
    hide_document(message, 'status_dip', "Диплом", get_diploma_menu)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get(
            'state') == 'awaiting_broadcast_message':
        if user_id == ADMIN_USER_ID:
            broadcast_message = message.text
            users = get_all_users()
            if not users:
                bot.send_message(
                    message.chat.id,
                    "Ошибка: Не удалось получить список пользователей.",
                    reply_markup=get_admin_panel())
                del user_data[user_id]
                return
            success_count = 0
            for user in users:
                try:
                    bot.send_message(int(user['user_id']), broadcast_message)
                    success_count += 1
                except Exception as e:
                    logging.error(
                        f"Ошибка при отправке сообщения пользователю {user['user_id']}: {str(e)}"
                    )
            bot.send_message(
                message.chat.id,
                f"Рассылка завершена! Отправлено {success_count} из {len(users)} пользователям.",
                reply_markup=get_admin_panel())
            del user_data[user_id]
    elif user_id in user_data and user_data[user_id].get(
            'state') == 'awaiting_input':
        field = user_data[user_id].get('field')
        fieldo = user_data[user_id].get('fieldo')
        value = message.text
        if not field:
            bot.send_message(message.chat.id,
                             "Ошибка: поле редактирования не определено.")
            return
        response = requests.post(f"{BASE_URL}api/update.php",
                                 data={
                                     'user_id': user_id,
                                     'field': field,
                                     'value': value
                                 })
        if response.status_code == 200 and response.json().get(
                'status') == 'success':
            del user_data[user_id]
            bot.send_message(
                message.chat.id,
                f"Данные для {fieldo} успешно обновлены! Перезапустите приложение 🎉",
                reply_markup=get_main_menu(user_id))
        else:
            bot.send_message(
                message.chat.id,
                "Ошибка при сохранении данных. Проверьте сервер.")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get(
            'state') == 'awaiting_photo':
        try:
            photo = message.photo[-1]  # Берем фото максимального качества
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            files = {'photo': ('photo.jpg', downloaded_file, 'image/jpeg')}
            data = {'user_id': user_id}
            logging.info(f"Загрузка фото для user_id: {user_id}")
            response = requests.post(f"{BASE_URL}api/upload_photo.php",
                                     files=files,
                                     data=data)
            if response.status_code == 200 and response.json().get(
                    'status') == 'success':
                del user_data[user_id]
                bot.send_message(
                    message.chat.id,
                    "Фото загружено! Данные успешно изменены! ПЕРЕУСТАНОВИТЕ приложение 📷",
                    reply_markup=get_main_menu(user_id))
            else:
                bot.send_message(message.chat.id,
                                 f"Ошибка при загрузке фото: {response.text}")
        except Exception as e:
            bot.send_message(message.chat.id,
                             f"Ошибка при обработке фото: {str(e)}")
            logging.error(f"Ошибка при загрузке фото: {str(e)}")
    else:
        bot.send_message(message.chat.id,
                         "Сначала выберите '📷 Загрузить общую фотку'.")


# Flask приложение
app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!"


def run_bot():
    while True:
        try:
            logging.info("Запуск бота...")
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            logging.error(f"Ошибка в работе бота: {str(e)}")
            bot.stop_polling()
            threading.Event().wait(5)  # Пауза перед перезапуском


if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # Поток завершится вместе с основным процессом
    bot_thread.start()
    # Запускаем Flask
    app.run(host='0.0.0.0', port=8080)
