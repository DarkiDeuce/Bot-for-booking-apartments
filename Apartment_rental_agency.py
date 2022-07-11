import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot(" ")
dates = []

def Date_display():
    con = sqlite3.connect("Information_Apartaments.db")
    cursor = con.cursor()
    cursor.execute("SELECT Available_dates FROM Information_Apartaments WHERE Addres == (?)", [Apartaments])
    Available_dates_FromDB = cursor.fetchall()
    separation = Available_dates_FromDB[0][0].split(",")
    buttons_in_row = 6
    buttons_added = []

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row_width = 6

    for Button in separation:
        buttons_added.append(types.KeyboardButton(Button))
        if len(buttons_added) == buttons_in_row:
            markup.add(*buttons_added)
            buttons_added = []

    if buttons_added:
        markup.add(*buttons_added)
    markup.add(types.KeyboardButton("Забронировать"), types.KeyboardButton("Вернуться назад."))

    return markup

def rent_or_answer_or_information():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    BookApartaments = types.KeyboardButton("Забронировать квартиру.")
    Information_About_Apartments = types.KeyboardButton("Информация о квартирах.")
    AnswerOnQuestions = types.KeyboardButton("Ответы на часто задаваемые вопросы.")
    markup.add(Information_About_Apartments, BookApartaments, AnswerOnQuestions)

    return markup

def mailing(message):
    con = sqlite3.connect("id_user.db")
    cur = con.cursor()

    cur.execute("SELECT id_user FROM Test")
    all_id = cur.fetchall()
    text_mailing = message.text

    for i in all_id:
        bot.send_message(i[0], text_mailing)

def choice(message):
    con = sqlite3.connect("Information_Apartaments.db")
    cursor = con.cursor()

    if message.text == "Ответы на часто задаваемые вопросы.":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        Appliances = types.KeyboardButton("Есть ли в квартире базовые бытовые предметы(посуда, постельное бельё, полотенца)?")
        Pledge = types.KeyboardButton("Какой залог при снятии квартиры?")
        Smoking = types.KeyboardButton("Можно ли курить и пить спиртное в квартире?")
        Back = types.KeyboardButton("Вернуться назад.")

        markup.add(Appliances, Pledge, Smoking, Back)

        bot.send_message(message.chat.id, "Выберете интересующий вас вопрос:", reply_markup=markup)

        bot.register_next_step_handler(message, question)

    elif message.text == "Забронировать квартиру.":
        cursor.execute("SELECT Addres FROM Information_Apartaments")
        Address_list = cursor.fetchall()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for Address in Address_list:
            markup.add(Address[0])
        #Сюда ещё нужно добавить фотографии и информацию о квартирах. Фотографии загрузить в БД. Отправить фотографии командой: bot.send_message(message.chat.id, 'Имя переменной в которой будут лежать фотографии из БД'
        #Добавление фотографии происходит по стандарту, через выборку  полей из таблицы, в переменную записываются через fetchall. Пример: bot.send_photo(message.chat.id, BiPhoto[0][0], caption="Получилось")
        bot.send_message(message.chat.id, "Выберете адрес интересующей вас квартиры.", reply_markup=markup)

        bot.register_next_step_handler(message, booking)

    elif message.text == "Информация о квартирах.":
        cursor.execute("SELECT Addres FROM Information_Apartaments")
        Address_list = cursor.fetchall()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for Address in Address_list:
            markup.add(Address[0])

        markup.add("Вернуться назад.")

        bot.send_message(message.chat.id, "Выберете интересующую вас квартиру.", reply_markup=markup)

        bot.register_next_step_handler(message, Information)

def Information(message):
    global Apartaments

    con = sqlite3.connect("Information_Apartaments.db")
    cursor = con.cursor()
    Apartaments = message.text

    if Apartaments == "Вернуться назад.":
        markup = rent_or_answer_or_information()

        bot.send_message(message.chat.id,"Есть ещё вопросы или хотите забронировать квартиру?", reply_markup=markup)
        bot.register_next_step_handler(message, choice)

    else:
        bot.register_next_step_handler(message, Information)
        cursor.execute("SELECT Information_Apartaments FROM Information_Apartaments WHERE Addres = (?)", [Apartaments])
        Information_Apartaments = cursor.fetchall()

        cursor.execute("SELECT Photo_Apartaments FROM Information_Apartaments WHERE Addres = (?)", [Apartaments])
        Photo_Apartaments = cursor.fetchall()
        separation = Photo_Apartaments[0][0].split(",")

        bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(Photo, caption=Information_Apartaments[0][0]) for Photo in separation])

def booking(message):
    global Apartaments

    Apartaments = message.text
    Note = 'Последовательно выберете даты на которые вы хотите забронировать квартиру. После выбора нажмите на кнопку "Забронировать".\n\n Свободные даты:'
    markup = Date_display()

    bot.send_message(message.chat.id, text=Note, reply_markup=markup)
    bot.register_next_step_handler(message, db_change)

def db_change(message):
    con = sqlite3.connect("Information_Apartaments.db")
    cursor = con.cursor()

    if message.text == "Вернуться назад.":
        markup = rent_or_answer_or_information()

        bot.send_message(message.chat.id, "Есть ещё вопросы или хотите забронировать квартиру?", reply_markup=markup)
        bot.register_next_step_handler(message, choice)
    elif message.text != "Вернуться назад." and message.text != "Забронировать":
        dates.append(message.text)
        bot.register_next_step_handler(message, db_change)
    elif message.text == "Забронировать":
        cursor.execute("SELECT Available_dates FROM Information_Apartaments WHERE Addres = (?)", [Apartaments])
        Available_dates_FromDB = cursor.fetchall()
        separation = Available_dates_FromDB[0][0].split(",")
        for i in dates:
            for j in separation:
                if i == j:
                    separation.remove(i)
                    Available_dates_FromDB = ",".join(separation)

        cursor.execute("UPDATE Information_Apartaments SET Available_dates = (?) WHERE Addres = (?)",[Available_dates_FromDB, Apartaments])
        con.commit()

        Parting = "Выбранная вами квартира забронирована на указанные даты. \n\nДля подтверждения брони в ближайшее время с вами свяжется администратор агества для подтверждения информации.\n\n \
Пожалуйста, оставьте ваши контактные данные в произвольной форме."

        bot.send_message(message.chat.id, text=Parting)
        bot.register_next_step_handler(message, message_for_admin)

def message_for_admin(message):
    bot.send_message(520794257, f"Квартира {Apartaments} забронированна на {dates}. \n\nКонтактная информация оставленная клиентом:")
    bot.forward_message(520794257, message.chat.id, message.id)
    dates.clear()

    markup = rent_or_answer_or_information()
    bot.send_message(message.chat.id, "Информация переданна администратору.", reply_markup=markup)
    bot.register_next_step_handler(message, choice)

def question(message):
    answer = message.text
    question_answer = {"Есть ли в квартире базовые бытовые предметы(посуда, постельное бельё, полотенца)?": "В каждой квартире имеется:" \
                                                                                                     "\n-Посуда" \
                                                                                                     "\n-Постельное бельё" \
                                                                                                     "\n-Фен и утюг" \
                                                                                                     "\n-Стиральная машина.", \
                "Какой залог при снятии квартиры?":"Залоговая сумма фиксирована и составляет 5000 рублей.",\
                "Можно ли курить и пить спиртное в квартире?":"Употребление алкогольной и табачной продукции в квартирах строго запрещено!",\
                "Вернуться назад.":"Есть ещё вопросы или хотите забронировать квартиру?"}

    if answer == "Вернуться назад.":
        markup = rent_or_answer_or_information()

        bot.send_message(message.chat.id, question_answer.get(answer), reply_markup=markup)
        bot.register_next_step_handler(message, choice)

    elif answer in question_answer:
        bot.send_message(message.chat.id, question_answer.get(answer))
        bot.register_next_step_handler(message, question)
    else:
        bot.register_next_step_handler(message, question)

@bot.message_handler(commands=["start"])
def start(message):
    con = sqlite3.connect("Test.db")
    cur = con.cursor()

    Greetings = 'Вас привествует агенство по аредне недвижимости "Этажи".' \
                '\n\nБронирование квартир производится по средствам данного бота и последующей отправки информации администратору. ' \
                'Стоимость аренды квартир может меняться в зависимости от времени года и даты.' \
                '\n\nГотовы сразу ответить на нексколько интересующих Вас вопросов или предоставить информацию о бронировании квартир.',

    markup = rent_or_answer_or_information()

    bot.send_message(message.chat.id, text=Greetings, reply_markup=markup)

    cur.execute("SELECT id_user FROM Test")
    all_id = cur.fetchall()

    if message.from_user.id in all_id[0]:
        bot.register_next_step_handler(message, choice)
    else:
        cur.execute("INSERT INTO Test(id_user) VALUES (?)", [message.from_user.id])
        bot.register_next_step_handler(message, choice)
        con.commit()

@bot.message_handler(commands=["mailing"])
def Authorization(message):
    if message.from_user.id == 520794257:
        bot.send_message(520794257, "Введите текст рассылки.")
        bot.register_next_step_handler(message, mailing)

bot.polling(non_stop=True)
