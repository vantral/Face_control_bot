# -*- coding: utf-8 -*-
import telebot
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import conf  # импортируем наш секретный токен
import flask
import random

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)
telebot.apihelper.proxy = conf.PROXY
bot = telebot.TeleBot(conf.TOKEN)  # создаем экземпляр бота
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

app = flask.Flask(__name__)


def put_text_pil(img, txt):
    font_size = img.shape[0] // 10

    im = Image.fromarray(img)

    font = ImageFont.truetype('3952.ttf', size=font_size)

    draw = ImageDraw.Draw(im)
    wid, hei = draw.textsize(txt, font=font)
    while img.shape[1] - wid <= img.shape[1] / 50:
        font_size -= 10
        font = ImageFont.truetype('3952.ttf', size=font_size)
        draw = ImageDraw.Draw(im)
        wid, hei = draw.textsize(txt, font=font)

    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)

    offset = font_size // 25
    shadowColor = 'black'

    w = int((img.shape[1] - wid) / 2)
    h = img.shape[0] * 0.85

    while img.shape[0] - hei < h:
        h -= img.shape[0] / 100

    for off in range(offset):
        # move right
        d.text((w - off, h), txt, font=font, fill=shadowColor)
        # move left
        d.text((w + off, h), txt, font=font, fill=shadowColor)
        # move up
        d.text((w, h + off), txt, font=font, fill=shadowColor)
        # move down
        d.text((w, h - off), txt, font=font, fill=shadowColor)
        # diagnal left up
        d.text((w - off, h + off), txt, font=font, fill=shadowColor)
        # diagnal right up
        d.text((w + off, h + off), txt, font=font, fill=shadowColor)
        # diagnal left down
        d.text((w - off, h - off), txt, font=font, fill=shadowColor)
        # diagnal right down
        d.text((w + off, h - off), txt, font=font, fill=shadowColor)

    # теперь можно центрировать текст
    d.text((w, h), txt, fill='rgb(255, 255, 255)', font=font)
    img = np.asarray(im)
    return img

def put_text_face(img, txt, sw, fw, h):
    font_size = img.shape[0] // 15

    im = Image.fromarray(img)

    font = ImageFont.truetype('3952.ttf', size=font_size)

    draw = ImageDraw.Draw(im)
    wid, hei = draw.textsize(txt, font=font)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    w = (sw + fw) / 2 - wid / 2
    offset = font_size // 25
    shadowColor = 'black'

    for off in range(offset):
        # move right
        d.text((w-off, h), txt, font=font, fill=shadowColor)
        # move left
        d.text((w+off, h), txt, font=font, fill=shadowColor)
        # move up
        d.text((w, h+off), txt, font=font, fill=shadowColor)
        # move down
        d.text((w, h-off), txt, font=font, fill=shadowColor)
        # diagnal left up
        d.text((w-off, h+off), txt, font=font, fill=shadowColor)
        # diagnal right up
        d.text((w+off, h+off), txt, font=font, fill=shadowColor)
        # diagnal left down
        d.text((w-off, h-off), txt, font=font, fill=shadowColor)
        # diagnal right down
        d.text((w+off, h-off), txt, font=font, fill=shadowColor)

    # теперь можно центрировать текст
    d.text((w, h), txt, fill='rgb(255, 255, 255)', font=font)
    img = np.asarray(im)
    return img

def main_menu(name):
    mark_up = telebot.types.InlineKeyboardMarkup()
    item = telebot.types.InlineKeyboardButton(
        text=u'Хочешь поразвлекаться?', callback_data='1'
    )
    mark_up.add(item)
    return mark_up


@bot.message_handler(commands=['start'])
def start_message(message):
    id = message.chat.id
    name = message.chat.first_name
    r_name = ''
    for letter in name:
        k = chr(ord(letter) + 6)
        r_name += k
    mark_up = main_menu(r_name)
    bot.send_message(id, u'Привет! Я не буллетпруф', reply_markup=mark_up)


@bot.callback_query_handler(func=None)
def gotit(message):
    id = message.from_user.id
    if message.data == '1':
        mark_up = telebot.types.InlineKeyboardMarkup()
        item = telebot.types.InlineKeyboardButton(
            text=u'Закрыть лицо', callback_data='2'
        )
        mark_up.add(item)
        item = telebot.types.InlineKeyboardButton(
            text=u'Написать текст', callback_data='3'
        )
        mark_up.add(item)
        bot.send_message(id, text=u'Выбери режим!', reply_markup=mark_up)
    if message.data == '2':
        SRC = ['']
        FILE_INFO = ['']
        bot.send_message(id, text=u'Отправь мне фото!')

        @bot.message_handler(content_types=['photo'])
        def face_control(message):
            FILE_INFO[0] = bot.get_file(message.photo[-1].file_id)
            SRC[0] = message.chat.id
            if FILE_INFO[0] and SRC[0] == message.chat.id:
                downloaded_file = bot.download_file(FILE_INFO[0].file_path)
                with open(str(SRC[0]), 'wb') as new_file:
                    new_file.write(downloaded_file)
            prototxt_path = os.path.join('model_data/deploy.prototxt')
            caffemodel_path = os.path.join('model_data/weights.caffemodel')
            model = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
            img = cv2.imread(str(SRC[0]))

            (h, w) = img.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

            model.setInput(blob)
            detections = model.forward()
            faces = 0
            for i in (range(0, detections.shape[2])):
                if detections[0, 0, i, 2] > 0.5:
                    faces = 1
                    break
            if faces == 0:
                bot.send_message(message.chat.id, u'Лиц не обнаружено')
            else:
                confidence = 0

                while confidence <= 0.5:
                    i = random.choice(range(0, detections.shape[2]))
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    confidence = detections[0, 0, i, 2]

                cv2.rectangle(img, (startX, startY), (endX, endY), (0, 0, 0), -1)
                img = put_text_face(img, 'чорт', startX, endX, endY)
                cv2.imwrite(str(SRC[0]) + '.png', img)
                photo = open(str(SRC[0]) + '.png', 'rb')
                os.remove(str(SRC[0]))
                os.remove(str(SRC[0]) + '.png')
                SRC[0] = ''
                FILE_INFO[0] = ''
                bot.send_photo(message.chat.id, photo=photo)
    if message.data == '3':
        SRC = ['']
        FILE_INFO = ['']
        bot.send_message(id, text=u'Отправь мне фото!')

        @bot.message_handler(content_types=['photo'])
        def photo(message):
            FILE_INFO[0] = bot.get_file(message.photo[-1].file_id)
            SRC[0] = message.chat.id
            mark_up = telebot.types.ReplyKeyboardMarkup()
            mark_up.row(u'Хочу ввести свой текст')
            mark_up.row(u'Хочу дефолтный текст')
            bot.send_message(message.chat.id, text=u'Какой текст?', reply_markup=mark_up)

            @bot.message_handler(regexp='Хочу ввести свой текст')
            def choice(message):
                bot.send_message(message.chat.id, text=u'Отправь текст, который хочешь написать.',
                                 reply_markup=telebot.types.ReplyKeyboardRemove())

                @bot.message_handler()
                def text(message):
                    if FILE_INFO[0] and SRC[0] == message.chat.id:
                        downloaded_file = bot.download_file(FILE_INFO[0].file_path)
                        with open(str(SRC[0]), 'wb') as new_file:
                            new_file.write(downloaded_file)
                        img = cv2.imread(str(SRC[0]))
                        img = put_text_pil(img, message.text)
                        cv2.imwrite(str(SRC[0]) + '.png', img)
                        photo = open(str(SRC[0]) + '.png', 'rb')
                        os.remove(str(SRC[0]))
                        os.remove(str(SRC[0]) + '.png')
                        SRC[0] = ''
                        FILE_INFO[0] = ''
                        bot.send_photo(message.chat.id, photo=photo)

            @bot.message_handler(regexp='Хочу дефолтный текст')
            def no_choice(message):
                if FILE_INFO[0] and SRC[0] == message.chat.id:
                    downloaded_file = bot.download_file(FILE_INFO[0].file_path)
                    with open(str(SRC[0]), 'wb') as new_file:
                        new_file.write(downloaded_file)
                    img = cv2.imread(str(SRC[0]))
                    img = put_text_pil(img, 'Вот тут дефолт')
                    cv2.imwrite(str(SRC[0]) + '.png', img)
                    photo = open(str(SRC[0]) + '.png', 'rb')
                    os.remove(str(SRC[0]))
                    os.remove(str(SRC[0]) + '.png')
                    SRC[0] = ''
                    FILE_INFO[0] = ''
                    bot.send_photo(message.chat.id, photo=photo, reply_markup=telebot.types.ReplyKeyboardRemove())


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


if __name__ == '__main__':
    import os

    app.debug = False
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
