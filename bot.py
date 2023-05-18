import urllib.request
import json
import random
import openai
import telebot
TOKEN = "YOUR_TG_TOKEN"
bot = telebot.TeleBot(token=TOKEN)
nameVPK = None
describeVPK = None
screenshoturlVPK = None
flag = False


def getInfo():
    global nameVPK
    global describeVPK
    global screenshoturlVPK
    openai.api_key = "YOUR_OPENAI_TOKEN"
    app = random.randint(1, 687)
    url = "https://rinnegatamante.it/vitadb/list_hbs_json.php"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    screenshots = data[app]['screenshots']
    print(data[app])
    screenshots = screenshots.split(";")
    screenshotsurl = []
    for i in screenshots:
        urlscreenshot = "https://rinnegatamante.it/vitadb/" + i
        screenshotsurl.append(urlscreenshot)

    prompt = f"Переведи этот текст на русский с английского, сохранив имена нарицательные.  {data[app]['long_description']}"
    completion = openai.Completion.create(engine="text-davinci-003",
                                          prompt=prompt,
                                          temperature=0.5,
                                          max_tokens=1000)
    print(data[app])

    name = data[app]["name"]
    nameVPK = name
    describeVPK = completion.choices[0]['text']
    screenshoturlVPK = screenshotsurl


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id, 'Привет! Напиши /vitarandom, если хочешь получить случайную игру, и /vitagame, если хочешь реализовать поиск по имени.')


@bot.message_handler(commands=['vitarandom'])
def start_message(message):
    bot.reply_to(
        message, "Ждите... Процесс занимает около 20 секунд")
    getInfo()
    for i in screenshoturlVPK:
        try:
            bot.send_photo(message.chat.id, photo=i)
        except:
            bot.send_message(
                message.chat.id, "Упс! Какая-то неполадка с скриншотами!")
    bot.send_message(
        message.chat.id, f'Название: {nameVPK} \nОписание: {describeVPK}')


@bot.message_handler(commands=['vitagame'])
def start_handler(message):
    msg = bot.send_message(
        message.chat.id, "Введите слово для поиска приложений:")
    bot.register_next_step_handler(msg, getInfo1)


def getInfo1(message):
    flag = False
    global nameVPK
    openai.api_key = "YOUR_OPENAI_TOKEN"
    global describeVPK
    global screenshoturlVPK
    url = "https://rinnegatamante.it/vitadb/list_hbs_json.php"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    bot.send_message(
        message.chat.id, "Поиск начат")
    for app in data:
        currentname = app["name"]
        currentname = currentname.lower()
        if message.text.lower() in currentname:
            flag = True
            screenshots = app['screenshots']
            screenshots = screenshots.split(";")
            screenshotsurl = []
            for i in screenshots:
                urlscreenshot = "https://rinnegatamante.it/vitadb/" + i
                screenshotsurl.append(urlscreenshot)
            prompt = f"Переведи этот текст на русский с английского, сохранив имена нарицательные.  {app['long_description']}"
            completion = openai.Completion.create(engine="text-davinci-003",
                                                  prompt=prompt,
                                                  temperature=0.5,
                                                  max_tokens=1000)
            nameVPK = app["name"]
            describeVPK = completion.choices[0]['text']
            screenshoturlVPK = screenshotsurl
            bot.send_message(
                message.chat.id, f"Найдена игра: {app['name']}")
            for i in screenshoturlVPK:
                try:
                    bot.send_photo(message.chat.id, photo=i)
                except:
                    bot.send_message(
                        message.chat.id, "Скриншоты отсутствуют!")
            bot.send_message(
                message.chat.id, f"Описание: {describeVPK}")
    if flag == False:
        bot.send_message(
            message.chat.id, "К сожалению, ничего не было найдено.")
    else:
        bot.send_message(
            message.chat.id, "Поиск окончен.")


bot.polling()
