from PIL import Image, ImageDraw, ImageFont
import textwrap
import datetime


@staticmethod

def GetUrokTime(Date:datetime,UrokNumber:int):
    '''
    Принимает дату и порядковый номер урока (Именно в этом порядке, иначе вернет None)
    Возвращает время урока в формате str("8:15-9:00")
    '''
    NormalList = {1:"8:15-9:00",
                  2:"9:00-9:45",
                  3:"9:55-10:40",
                  4:"10:40-11:25",
                  5:"11:40-12:25",
                  6:"12:25-13:10",
                  7:"13:30-14:15",
                  8:"14:15-15:00",
                  9:"15:15-16:00",
                  10:"16:00-16:45",
                  11:"16:55-17:40",
                  12:"17:40-18:25",
                  13:"18:35-19:10"}
    SubbotaList = {1:"8:15-9:00",
                   2:"9:00-9:45",
                   3:"9:50-10:35",
                   4:"10:35-11:20",
                   5:"11:35-12:20",
                   6:"12:20-13:05",
                   7:"13:20-14:05",
                   8:"14:05-14:50",
                   9:"15:05-15:50",
                   10:"15:50-16:35",
                   11:"16:40-17:25",
                   12:"17:25-18:10",
                   13:"18:15-19:00"
                   }
    if Date.strftime('%A')=='Saturday':
        return SubbotaList[int(UrokNumber)]
    else:
        return NormalList[int(UrokNumber)]

def getGroupScheduleAsImg(Schedule):
    if len(Schedule) == 0:
        return False

    header = ["Урок", "Предмет", "Каб.", "Преподаватель", "Время"]
    table_data = []
    max_width = 55
    max_width_kab = 6
    prev_urok_number = 0  # Переменная для отслеживания номера предыдущего урока

    # Создание таблицы данных
    for number in Schedule:
        current_urok_number = Schedule[number][0]["Number"]
        if current_urok_number - prev_urok_number > 1:
            for i in range(prev_urok_number + 1, current_urok_number):
                empty_row = [
                    i,
                    "",
                    "",
                    "",
                    GetUrokTime(datetime.datetime.strptime(Schedule[number][0]["Date"], "%Y-%m-%d"), i)
                ]
                table_data.append(empty_row)

        for urok in Schedule[number]:
            subject_lines = textwrap.wrap(urok["Subject"], max_width)
            classroom_lines = textwrap.wrap(urok["Classroom"], max_width_kab)
            prepod_lines = textwrap.wrap(urok['Prepod'], max_width)

            row = [
                urok["Number"],
                subject_lines,
                classroom_lines,
                prepod_lines,
                GetUrokTime(datetime.datetime.strptime(urok["Date"], "%Y-%m-%d"), urok["Number"])
            ]
            table_data.append(row)

        prev_urok_number = current_urok_number

    # Расчет размера изображения
    total_height = 50 * sum([max([len(row[i]) for i in range(1, 4)]) for row in table_data]) + len(table_data) + 1
    image = Image.new('RGB', (1110, total_height + 350), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('arial.ttf', size=18)

    # Инициализация координат и размеров ячеек
    x, y = 10, 10
    cell_width = [60, 570, 80, 250, 130]  # Ширина ячеек для каждого столбца
    cell_height = 30

    # Вставка логотипа
    logo_image = Image.open("Logo.png")
    logo_width, logo_height = logo_image.size
    new_logo_width = int(logo_width * 0.9)
    new_logo_height = int(logo_height * 0.9)
    logo_image = logo_image.resize((new_logo_width, new_logo_height))
    x_logo = (image.width - new_logo_width) // 2
    y_logo = (image.height - new_logo_height) // 2
    image.paste(logo_image, (x_logo, y_logo))

    # Отрисовка заголовка таблицы
    for i, header_text in enumerate(header):
        bbox = draw.textbbox((x, y), header_text, font=font)
        header_width = bbox[2] - bbox[0]
        header_height = bbox[3] - bbox[1]
        
        text_x = x + (cell_width[i] - header_width) // 2
        text_y = y + (cell_height - header_height) // 2
        draw.rectangle((x, y, x + cell_width[i], y + cell_height), outline=(0, 0, 0))
        draw.text((text_x, text_y), header_text, font=font, fill=(0, 0, 0))
        x += cell_width[i]
    
    x = 10
    y += cell_height

    # Отрисовка данных таблицы
    for row in table_data:
        max_lines = max([len(row[i]) for i in range(1, 4)])
        for i, cell_text in enumerate(row):
            cell_height_adjusted = cell_height * (max_lines + 1)
            draw.rectangle((x, y, x + cell_width[i], y + cell_height_adjusted), outline=(0, 0, 0))

            # Отрисовка текста в ячейках
            if isinstance(cell_text, list):
                for j, line in enumerate(cell_text):
                    draw.text((x + 5, y + 5 + j * cell_height), line, font=font, fill=(0, 0, 0))
            else:
                draw.text((x + 5, y + 5), str(cell_text), font=font, fill=(0, 0, 0))

            x += cell_width[i]

        x = 10
        y += cell_height * (max_lines + 1)

    # Сохранение изображения
    image.save("TableGroup.png")
    return image

def getTeacherScheduleAsImg(Schedule):
    if len(Schedule) == 0:
        return False

    header = ["Урок", "Группа", "Предмет", "Кабинет", "Время"]
    table_data = []
    prev_urok_number = 0

    for urok in Schedule:
        urok_data = Schedule[str(urok)]
        subject_lines = textwrap.wrap(urok_data["Subject"], 50)
        classroom_lines = textwrap.wrap(urok_data["Classroom"], 5)
        current_urok_number = int(urok_data["Number"])

        # Добавляем пустые строки между уроками, если есть пропуск
        if current_urok_number - prev_urok_number > 1:
            for i in range(prev_urok_number + 1, current_urok_number):
                empty_row = [
                    i,
                    [],
                    [],
                    [],
                    GetUrokTime(datetime.datetime.strptime(urok_data["Date"], "%Y-%m-%d"), i)
                ]
                table_data.append(empty_row)

        row = [
            current_urok_number,
            textwrap.wrap(urok_data["Group"], 15),
            subject_lines if isinstance(subject_lines, list) else [subject_lines],
            classroom_lines if isinstance(classroom_lines, list) else [classroom_lines],
            GetUrokTime(datetime.datetime.strptime(urok_data["Date"], "%Y-%m-%d"), current_urok_number)
        ]
        table_data.append(row)

        prev_urok_number = current_urok_number

    # Расчет размера изображения
    row_heights = [120 * max([len(row[i]) for i in range(2, 4)]) for row in table_data]

    # Общее количество строк в таблице
    total_rows = len(table_data)

    # Расчет высоты изображения
    y = sum(row_heights) + total_rows + 250
    image = Image.new('RGB', (1170, y), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('arial.ttf', size=18)

    x, y = 10, 10
    cell_width = [60, 300, 550, 120, 120]  # Ширина ячеек для каждого столбца
    cell_height = 40

    # Вставка логотипа
    logo_image = Image.open("Logo.png")
    logo_width, logo_height = logo_image.size
    new_logo_width = int(logo_width * 0.9)
    new_logo_height = int(logo_height * 0.9)
    logo_image = logo_image.resize((new_logo_width, new_logo_height))
    x_logo = (image.width - new_logo_width) // 2
    y_logo = (image.height - new_logo_height) // 2
    image.paste(logo_image, (x_logo, y_logo))

    # Отрисовка заголовка таблицы
    for i, header_text in enumerate(header):
        bbox = draw.textbbox((x, y), header_text, font=font)
        header_width = bbox[2] - bbox[0]
        header_height = bbox[3] - bbox[1]
        
        text_x = x + (cell_width[i] - header_width) // 2
        text_y = y + (cell_height - header_height) // 2
        draw.rectangle((x, y, x + cell_width[i], y + cell_height), outline=(0, 0, 0))
        draw.text((text_x, text_y), header_text, font=font, fill=(0, 0, 0))
        x += cell_width[i]
    
    x = 10
    y += cell_height

    # Отрисовка данных таблицы
    for row in table_data:
        max_lines = max([len(row[i]) for i in range(2, 4)])
        for i in range(len(row)):
            cell_height_adjusted = cell_height * (max_lines + 1)
            draw.rectangle((x, y, x + cell_width[i], y + cell_height_adjusted), outline=(0, 0, 0))

            # Отрисовка текста в ячейках
            if isinstance(row[i], list):
                for j, line in enumerate(row[i]):
                    draw.text((x + 5, y + 5 + j * cell_height), line, font=font, fill=(0, 0, 0))
            else:
                draw.text((x + 5, y + 5), str(row[i]), font=font, fill=(0, 0, 0))

            x += cell_width[i]

        x = 10
        y += cell_height * (max_lines + 1)

    # Сохранение изображения
    image.save("TableTeacher.png")
    return image