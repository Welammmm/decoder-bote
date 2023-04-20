import os
import tempfile
import urllib.request

from PyPDF2 import PdfFileReader
from PIL import Image
from pyzbar.pyzbar import decode
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters
from io import BytesIO

# Обработчик для документов
def handle_document(update: Update, context) -> None:
    document = update.message.document
    file_name = os.path.join(tempfile.gettempdir(), document.file_name)

    # Скачиваем документ
    document.get_file().download(file_name)

    # Читаем PDF-файл
    pdf = PdfFileReader(open(file_name, "rb"))

    qr_codes = []

    # Извлекаем изображения из PDF
    for page_num in range(pdf.numPages):
        page = pdf.getPage(page_num)
        xObject = page['/Resources']['/XObject'].get_object()
        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                data = xObject[obj]
                image = Image.frombytes(
                    data['/ColorSpace'], (data['/Width'], data['/Height']), data._data
                )
                qr_codes.append(image)

    # Декодируем QR-коды и отправляем результат
    for i, qr_code in enumerate(qr_codes):
        decoded = decode(qr_code)
        if decoded:
            update.message.reply_text(f"QR Code {i+1}:\n{decoded[0].data.decode()}")
            image_bytes = BytesIO()
            qr_code.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            update.message.reply_photo(photo=image_bytes)

    # Удаляем временные файлы
    os.remove(file_name)

# Токен вашего бота
TOKEN = "1441387826:AAGGQdWjIXxrDmgci490jx6BEaXxFLEMnts"

# Создаем экземпляр бота
updater = Updater(token=TOKEN, use_context=True)

# Добавляем обработчик документов
updater.dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

# Запускаем бота
updater.start_polling()

# В бесконечном цикле ждем входящих сообщений и обновлений
updater.idle()