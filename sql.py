import sqlite3
import random, string
from KCPTapi import GetAllTeachers
class Database:
    @staticmethod
    def generate_password(length,seed:int):
        random.seed(seed)
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    @staticmethod
    def GetPrepodPasswords():
        Database.StartDatabase()
        with sqlite3.connect('ScheduleBot.db') as conn:
            c = conn.cursor()
            c.execute("SELECT FIO, Password FROM PrepodUsers")
            data = c.fetchall()

        formatted_data = ''
        for row in data:
            formatted_data += f"ФИО: {row[0]}, Пароль: /pr {row[1]}\n"

        return formatted_data
        

    @staticmethod
    def RegUser(ChatId, Group: str):
        with sqlite3.connect('ScheduleBot.db') as conn:
            # Добавляем нового пользователя в таблицу Users
            conn.execute('''
    INSERT INTO Users (id, group_id)
    VALUES (?, ?)
    ON CONFLICT (id) DO UPDATE SET group_id = EXCLUDED.group_id;
''', (ChatId, Group))
    @staticmethod
    def RegPrepod(ChatId:int, Password:str):
        check_password = False
        with sqlite3.connect('ScheduleBot.db') as conn:
            cursor = conn.execute("SELECT EXISTS(SELECT 1 FROM PrepodUsers WHERE Password = ?)", (Password,))
            result = cursor.fetchone()
            check_password = bool(result)
        if(not check_password): return False
        with sqlite3.connect('ScheduleBot.db') as conn:
            c = conn.cursor()
            # Добавляем нового пользователя в таблицу Users
            c.execute('''
             UPDATE PrepodUsers
             SET chatid = ?
             WHERE Password = ?
            ''', (ChatId, Password))
            conn.commit()
        return True

    @staticmethod
    def Execute(query: str, params: dict = None):
        with sqlite3.connect('ScheduleBot.db') as conn:
            cursor = conn.execute(query, params) if params else conn.execute(query)
            result = cursor.fetchone()
            if result:
                return cursor.fetchall()
            else:
                return result
    @staticmethod
    def RemovePrepodUser(chatid):
        with sqlite3.connect('ScheduleBot.db') as conn:
            cursor = conn.execute("UPDATE PrepodUsers SET chatid = NULL WHERE chatid = ?", (chatid,))

    @staticmethod
    def GetUsersCount():
        with sqlite3.connect('ScheduleBot.db') as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM Users")
            return c.fetchone()
    @staticmethod
    def GetGroupIdByUserId(ChatId):
        with sqlite3.connect('ScheduleBot.db') as conn:
            cursor = conn.execute("SELECT Users.group_id FROM Users WHERE Users.id=?", (ChatId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    @staticmethod
    def getPrepodFioByChatId(ChatId:str):
        with sqlite3.connect('ScheduleBot.db') as conn:
            cursor = conn.execute("SELECT PrepodUsers.FIO FROM PrepodUsers WHERE chatid = ?", (ChatId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    @staticmethod
    def getPrepodIdByChatId(ChatId:str):
        with sqlite3.connect('ScheduleBot.db') as conn:
            cursor = conn.execute("SELECT PrepodUsers.FIO FROM PrepodUsers WHERE chatid = ?", (ChatId,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    @staticmethod
    def is_user_prepod(user_id):
        with sqlite3.connect('ScheduleBot.db') as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM PrepodUsers WHERE chatid = ?", (user_id,))
            result = cursor.fetchone()
            if(result[0] == 0):
                return False
            else: return True
    @staticmethod
    def is_user_exists(user_id):
        with sqlite3.connect('ScheduleBot.db') as conn:
          c = conn.cursor()
          c.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
          result = c.fetchone()
          return result is not None
    @staticmethod
    def StartDatabase():
        with sqlite3.connect('ScheduleBot.db') as conn:
                conn.execute('''CREATE TABLE IF NOT EXISTS PrepodUsers (
                             Password TEXT NOT NULL,
                             chatid INTEGER,
                             FIO TEXT NOT NULL
                             )''')
                cur = conn.cursor()
                data = []
                teachers = GetAllTeachers()
                for i in teachers:
                    t = (teachers[str(i)]["Surname"]+" "+teachers[str(i)]['FirstName']+" "+teachers[str(i)]['SecondName'], Database.generate_password(8,teachers[str(i)]["Surname"]))
                    data.append(t)
                
                for i in data:
                    if int(conn.execute('SELECT Count(*) FROM PrepodUsers WHERE FIO = ?',(i[0],)).fetchone()[0]) == 0:
                        conn.execute('INSERT INTO PrepodUsers (FIO, Password) Values(?,?)',(i[0],i[1],))

                conn.commit()
            #Создание таблицы с пользователями
                conn.execute('''
                     CREATE TABLE IF NOT EXISTS Users (
                       id INTEGER PRIMARY KEY,
                       group_id Text NOT NULL
                       )
                    ''')
Database.StartDatabase()
#with sqlite3.connect('ScheduleBot.db') as conn:
#            c = conn.cursor()
#            c.execute("SELECT * FROM PrepodUsers")
#            print(c.fetchall())