import os
from io import BytesIO
import requests
import logging
import qrcode
from telegram.ext import Updater, MessageHandler, Filters
from PyMuPDF import PdfReader

# Устанавливаем уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Обработчик сообщений
def handle_message(update, context):
    # Получаем объект сообщения и его идентификатор
    message = update.message
    chat_id = message.chat_id

    # Проверяем наличие прикрепленных файлов
    if message.document:
        document = message.document
        file_id = document.file_id

        # Скачиваем файл с серверов Telegram
        file = context.bot.get_file(file_id)
        file.download("input.pdf")

        # Извлекаем QR-коды из PDF-файла
        pdf = PdfReader("input.pdf")
        qr_codes = []
        for page in pdf.pages:
            xObject = page['/Resources']['/XObject'].get_object()
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    data = xObject[obj].get_data()
                    img = qrcode.decode(data)
                    qr_codes.append(img)

        # Отправляем QR-коды обратно пользователю
        for qr_code in qr_codes:
            qr_code.save("output.png")
            context.bot.send_photo(chat_id=chat_id, photo=open("output.png", "rb"))
        
        # Удаляем временные файлы
        os.remove("input.pdf")
        os.remove("output.png")
        
        # Отправляем сообщение о завершении
        context.bot.send_message(chat_id=chat_id, text="Извлечение QR-кодов завершено!")
    else:
        # Если нет прикрепленных файлов, отправляем сообщение с просьбой прикрепить PDF-файл
        context.bot.send_message(chat_id=chat_id, text="Пожалуйста, прикрепите PDF-файл с QR-кодами.")

# Инициализация бота и добавление обработчика
def main():
    # Вставьте ваш токен бота
    TOKEN = '1441387826:AAFrkhHe4TQA1zLvI9sGr_lPKn35kacbJ58'
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.document, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()