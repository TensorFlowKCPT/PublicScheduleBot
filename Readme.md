# Проект бота для расписания КЦПТ
## Бот использует API Сервер для своей работы, его можно найти здесь
### https://github.com/TensorFlowKCPT/PublicKCPTApi
## Инструкция по запуску бота локально
- Клонируете репозиторий на свой пк
- Переходите в папку с репозиторием и устанавливаете зависимости
```
pip install -r requirements.txt
```
- В telegram находите @BotFather и получаете у него ключ для вашего бота
- в файле TeleBot.py укажите свой ключ в строке 
```
bot = telebot.TeleBot("KEY")
```
- Запускаете сервер KCPTapi, предварительно заставив его спарсить расписание с сайта кцпт
- Запускаете бота используя TeleBot.py
```
python TeleBot.py
```
- Готово, бот готов принимать сообщения используя введенный вами ключ от вашего бота, попробуйте отправить ему /start