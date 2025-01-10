import telebot
from telebot import types
from sql import Database
import datetime
import locale
from KCPTapi import GetSchedule,GetTeacherSchedule,GetAllGroups
from CreateImg import getGroupScheduleAsImg,getTeacherScheduleAsImg
import logger
import os

# Здесь ключ для бота, который можно получить у @BotFather
bot = telebot.TeleBot("KEY")
bot_id = bot.get_me().id
UsersQueriesCount = 0
TeacherQueriesCount = 0
UserFailsCount = 0
TeacherFailsCount = 0
#region Клавиатуры
def GetPrepodsKeyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    ScheduleButton = types.KeyboardButton(text="Посмотреть мое расписание🗒️")
    BackButton = types.KeyboardButton(text="◀️")
    keyboard.add(ScheduleButton,BackButton)
    ExitButton = types.KeyboardButton(text="Я не преподаватель❌")
    keyboard.add(ExitButton)
    return keyboard
@staticmethod
def GetGroupsKeyboard():
    # Создаем клавиатуру
    keyboard = types.ReplyKeyboardMarkup(row_width=5)
    # Создаем кнопки
    for i in GetAllGroups():
        button = types.KeyboardButton(i)
        keyboard.add(button)
    return keyboard
@staticmethod
def GetSettingsKeyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    ScheduleButton = types.KeyboardButton(text="Изменить группу")
    BackButton = types.KeyboardButton(text="◀️")
    keyboard.add(ScheduleButton,BackButton)
    return keyboard
@staticmethod
def GetAdminKeyboard(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    LogsButton = types.KeyboardButton(text="Получить логи📝")
    UsersCountButton = types.KeyboardButton(text="Получить количество пользователей👤")
    CountQueriesButton = types.KeyboardButton(text="Получить количество запросов📅")
    PasswordsButton = types.KeyboardButton(text="Получить пароли преподавателей🔒")
    BackButton = types.KeyboardButton(text="◀️")
    keyboard.add(LogsButton,UsersCountButton)
    keyboard.add(CountQueriesButton)
    keyboard.add(PasswordsButton)
    keyboard.add(BackButton)
    return keyboard
@staticmethod
def GetMenuKeyboard(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    ScheduleButton = types.KeyboardButton(text="Расписание 📝")
    SettingsButton = types.KeyboardButton(text="⚙️")
    keyboard.add(ScheduleButton,SettingsButton)
    if Database.is_user_prepod(message.chat.id):
        PrepodPanelButton = types.KeyboardButton(text="Панель преподавателя 🎓")
        keyboard.add(PrepodPanelButton)
    return keyboard
@staticmethod
def GetDatesKeyboard(IsTeacher:bool):
    # Создаем клавиатуру
    
    keyboard = types.InlineKeyboardMarkup()

    # Дни недели для соответствующих дат
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    for i in range(-1, 8):  # Добавляем 8 дней, чтобы пропустить воскресенье и добавить один день в конец
        # Получаем дату для текущего дня и день недели
        current_date = datetime.datetime.now() + datetime.timedelta(days=i)
        formatted_date = current_date.strftime('%d.%m')  # Форматируем дату как "день месяца Месяц"
        
        # Если текущий день - воскресенье, пропустить его и добавить один день
        if current_date.weekday() == 6:
            continue

        day_of_week = days_of_week[current_date.weekday()]  # Получаем день недели

        # Создаем текст для кнопки
        button_text = f"{formatted_date} ({day_of_week})"
        if i == 0:
            button_text += " (Сегодня)"
        elif i == 1:
            button_text += " (Завтра)"
        elif i == -1:
            button_text += " (Вчера)"

        # Создаем кнопку с callback_data
        if IsTeacher:
            button_day = types.InlineKeyboardButton(text=button_text, callback_data=f"{current_date.strftime('%d.%m.%Y')}*")
        else:
            button_day = types.InlineKeyboardButton(text=button_text, callback_data=current_date.strftime('%d.%m.%Y'))

        keyboard.add(button_day)

    return keyboard
#endregion
#region Админ-панель
@bot.message_handler(regexp='Получить пароли преподавателей🔒')
def GetPrepodPasswords(message):
    bot.send_message(message.chat.id, text=Database.GetPrepodPasswords())

@bot.message_handler(regexp='Получить логи📝')
def GetLogsHandler(message):
    with open("app.log", 'rb') as log_file:
        bot.send_document(message.chat.id, log_file)
@bot.message_handler(regexp='Получить количество пользователей👤')
def GetUsersCountHandler(message):
    bot.send_message(message.chat.id,text="Количество пользователей бота: "+str(Database.GetUsersCount()[0]))
@bot.message_handler(regexp='Получить количество запросов📅')
def GetQueriesCountHandler(message):
    global TeacherQueriesCount
    global UsersQueriesCount
    global UserFailsCount
    global TeacherFailsCount
    formatted_text = f"""{datetime.datetime.strftime(datetime.datetime.now(),"%d.%m.%Y, %H:%M")}
Запросы с последнего перезапуска:
Всего запросов: {TeacherQueriesCount + UsersQueriesCount}
Запросов от студентов: {UsersQueriesCount}
Из них неудачных: {UserFailsCount}
Запросов от преподавателей: {TeacherQueriesCount}
Из них неудачных: {TeacherFailsCount}"""
    bot.send_message(message.chat.id,formatted_text)
#endregion
#region Панель преподавателей
@bot.message_handler(regexp='Панель преподавателя 🎓')
def PrepodPanelButton_Handler(message):
    PrepodPanel(message)
@bot.message_handler(regexp='Я не преподаватель❌')
def DeletePrepod(message):
    Database.RemovePrepodUser(message.chat.id)
    MainMenu(message)
@staticmethod
def PrepodPanel(message):
        bot.send_message(message.chat.id,text='Здравствуйте, ' + Database.getPrepodFioByChatId(message.chat.id),reply_markup=GetPrepodsKeyboard())
@bot.message_handler(regexp='Посмотреть мое расписание🗒️')
def GetPrepodsSchedule(message):
    bot.send_message(message.chat.id,text='Выберите дату на которое вам нужно получить расписание',reply_markup=GetDatesKeyboard(True))


@bot.message_handler(commands=['pr'])
def PrepodPassword(message):
    if Database.is_user_prepod(message.chat.id):
        bot.send_message(message.chat.id, text='Вы уже преподаватель!') 
        return
    if(len(message.text)>4 and ' ' in message.text):
        if(Database.RegPrepod(message.chat.id, message.text.split(' ')[1])):
            PrepodPanel(message)
        else: bot.send_message(message.chat.id, text='Неверный пароль')
    else:
        bot.send_message(message.chat.id, text='Используйте /pr [Пароль]') 
#endregion
#region Навигация пользователя по менюшкам

@bot.message_handler(regexp='◀️')
def BackToMenuBtn_Handler(message):
    MainMenu(message)

@bot.message_handler(regexp='⚙️')
def SettingsBtn_Handler(message):
    SettingsMenu(message)

@bot.message_handler(regexp='Изменить группу')
def ChangeGroupBtn_Handler(message):
    bot.send_message(message.chat.id,text='Выберите свою новую группу',reply_markup=GetGroupsKeyboard())
#endregion
#region Менюшки
@staticmethod 
def MainMenu(message):
    if not Database.is_user_exists(message.chat.id):
        bot.send_message(message.chat.id,text='Вы не зарегестрированы, выберите свою группу',reply_markup=GetGroupsKeyboard())
        return
    bot.send_message(message.chat.id,text='Меню\nПо ошибкам писать\n@PikaChu72\n@Lardane\n@bymaginn',reply_markup=GetMenuKeyboard(message))
def SettingsMenu(message):
    bot.send_message(message.chat.id,text='Настройки',reply_markup=GetSettingsKeyboard())
#endregion
#region Старт и регистрация
@bot.message_handler(commands=['admin'])
def PrepodPassword(message):
    if(len(message.text)>6 and ' ' in message.text):
        if(message.text.split(' ')[1]=="QWERTYQWERTY"):
            bot.send_message(message.chat.id,text='Админ панель',reply_markup=GetAdminKeyboard(message))
        else: bot.send_message(message.chat.id, text='Неверный пароль')
    else:
        bot.send_message(message.chat.id, text='Используйте /admin [Пароль]') 
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,text="Здравствуйте, я - бот для расписания TensorFlowKCPTScheduleBot")
    if not Database.is_user_exists(message.chat.id):
        bot.send_message(message.chat.id,text='Вы не зарегестрированы, выберите свою группу',reply_markup=GetGroupsKeyboard())
        return
    MainMenu(message)
@bot.message_handler(regexp='^.*\s([0-9]+(-[0-9]+)+)$')
def on_group_change(message):
    Database.RegUser(message.chat.id,message.text)
    MainMenu(message)
#endregion
#region Функционал расписаний
@bot.message_handler(regexp='Расписание 📝')
def ScheduleButton_handler(message):
    bot.send_message(message.chat.id,text='Выберите дату на которое вам нужно получить расписание',reply_markup=GetDatesKeyboard(False))

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if '*' in call.data:
        global TeacherQueriesCount
        TeacherQueriesCount += 1
        prepod = Database.getPrepodIdByChatId(call.message.chat.id)
        image = getTeacherScheduleAsImg(GetTeacherSchedule(datetime.datetime.strptime(call.data[0:len(call.data)-1],"%d.%m.%Y"),prepod))
        if image != False:
            imgname = str(call.message.chat.id)+".png"
            image.save(imgname)
            with open(imgname, 'rb') as f:
                bot.send_message(call.message.chat.id, text="Расписание для "+ prepod+ ' на ' + call.data[0:len(call.data)-1])
                bot.send_photo(call.message.chat.id,photo=f)
            os.remove(imgname)
            logger.Log(str(call.message.chat.id)+" "+str(datetime.datetime.now()) + ' teacher success!' )

        else:
            global TeacherFailsCount
            TeacherFailsCount += 1
            bot.send_message(call.message.chat.id,text='Расписание на '+call.data[0:len(call.data)-1]+' не найдено')
            return
    else:
        global UsersQueriesCount
        UsersQueriesCount += 1
        group = Database.GetGroupIdByUserId(call.message.chat.id)
        image = getGroupScheduleAsImg(GetSchedule(datetime.datetime.strptime(call.data,"%d.%m.%Y"), group))
        if image != False:
            imgname = str(call.message.chat.id)+".png"
            image.save(imgname)
            with open(imgname, 'rb') as f:
                bot.send_message(call.message.chat.id, text="Расписание для "+ group+ ' на ' + call.data)
                bot.send_photo(call.message.chat.id,photo=f)
            os.remove(imgname)
            logger.Log(str(call.message.chat.id)+" "+str(datetime.datetime.now()) + ' success!' )
        else:
            global UserFailsCount
            UserFailsCount += 1
            logger.Log(str(call.message.chat.id)+" Сейчас: "+str(datetime.datetime.now())+" Запрошенная дата: "+call.data+ " Запрошенная группа: "+Database.GetGroupIdByUserId(call.message.chat.id)+ ' error!' )
            bot.send_message(call.message.chat.id,text='Расписание на ' +call.data+' не найдено')
            return
#endregion
#region Старт бота
Database.StartDatabase()
while 1:
    try:
        logger.Log("Bot Started!")
        bot.polling(non_stop=True, skip_pending=True)
    except Exception as e:
        logger.Log("Bot died!")
        logger.Log(e)
#endregion