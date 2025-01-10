import requests
import logger
import datetime

link = 'http://127.0.0.1:8000/api/'
@staticmethod
def GetAllGroups():
    '''
    Возвращает словарь со списком групп и их id

    Пример:
    [
    "АТ 21-11-1",
    "АТ 21-11-2",
    "АТ 21-11-3",
    ...
    ]
    '''
    response = requests.get(link+'groups', verify=False)
    if response.status_code == 200 and response.json()!=[]:
        # Обработка успешного ответа
        return response.json()
    else:
        logger.Log('Ошибка при выполнении запроса на получение списка групп: ', response.status_code)
        raise FileNotFoundError

@staticmethod
def GetAllTeachers():
    '''
    Возвращает список преподавателей словарем где ключ = id преподователя, для удобства id есть и внутри объекта преподователя
    
    Пример:
    {
    "1": {
        "id": 1,
        "FirstName": "В.",
        "SecondName": "А.",
        "Surname": "Ткачук"
        }
        "2": {
        "id": 2,
        "FirstName": "В.",
        "SecondName": "С.",
        "Surname": "Белан"
        }
        "3": {
        "id": 3,
        "FirstName": "И.",
        "SecondName": "В.",
        "Surname": "Русских"
        }
        }
    '''
    response = requests.get(link+'teachers', verify=False)
    if response.status_code == 200 and response.json()!=[]:
        # Обработка успешного ответа
        return response.json()
    else:
        logger.Log('Ошибка при выполнении запроса на получение списка преподавателей: ', response.status_code)
        raise FileNotFoundError

@staticmethod
def GetSchedule(Date:datetime.datetime,GroupId:str):
    '''
    Принимает:
        Дата:DateTime
        idГруппы:str
    Возвращает расписание, сразу с изменениями
    Пример:
    {
    "5": {
    "Subject": "Иностранный язык",
    "Prepod": "Ткачук В. А.",
    "Group": "ИСиП 21-11-3",
    "Date": "2023-09-18",
    "Number": 5,
    "Classroom": "891",
    "IsChange": false
    },
    "6": {
    "Date": "2023-09-18",
    "Group": "ИСиП 21-11-3",
    "Number": 6,
    "Classroom": "891",
    "Prepod": "Ткачук В. А.",
    "Subject": "Программирование",
    "Comment": "Будет",
    "Delete": null,
    "IsChange": true
    }
    }
    '''
    response = requests.get(link+'class_day?date='+Date.strftime('%Y-%m-%d')+'&group='+str(GroupId), verify=False)
    if response.status_code == 200 and response.json()!=[]:
        # Обработка успешного ответа
        result = response.json()
        return result
    else:
        logger.Log('Ошибка при выполнении запроса на получение расписания для группы: '+str(GroupId)+' на '+Date.strftime('%d.%m.20%y')+': '+ str(response.status_code))
        raise FileNotFoundError


@staticmethod
def GetTeacherSchedule(Date:datetime.datetime,TeacherId:str):
    '''
    Принимает:
        Дата:DateTime
        id Препода:int
    Возвращает расписание преподавателя
    Пример:
    [
    {
        "Группа": "ИБАС  21-11",
        "Подгруппа": "2",
        "Дата": "2023-02-07",
        "День": "2",
        "Урок": "1",
        "Фамилия": "Гуляев",
        "Имя": "Иван",
        "Отчество": "Павлович",
        "Предмет": "Язык программирования JavaScript",
        "Кабинет": "",
        "ИЗМЕНЕНИЕ": "Нет"
    }
    ]
    '''
    response = requests.get(link+'teacher_day?date='+Date.date().strftime('%Y-%m-%d')+'&teacher='+str(TeacherId), verify=False)
    if response.status_code == 200 and response.json()!=[]:
        # Обработка успешного ответа
        result = response.json()
        return result
    else:
        logger.Log('Ошибка при выполнении запроса на получение расписания для преподавателя: '+str(TeacherId)+' на '+str(Date.strftime('%d.%m.20%y'))+': '+ str(response.status_code))
        raise FileNotFoundError
