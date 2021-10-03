import os
import random
import string

from PIL import Image
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.utils import secure_filename

import color_recogniser

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads/'

# сгенерированное значение секретного ключа в 24 символа
app.secret_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(24))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# используем капчу и полученные секретные ключи с сайта Google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdiKukUAAAAAGOH6Wve-LnDOwd5AyoGFSf4mRzm'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdiKukUAAAAAG16BmzRIq51tWhmQKRQ281q9wOt'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'custom'}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# класс с формой для капчи
class NetForm(FlaskForm):
    recaptcha = RecaptchaField()


# Функция проверки допустимого формата защруженного файла (изображения)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Функция-контроллер на GET метод, возвращающий страницу index.html
@app.route('/')
def upload_form():
    # создание формы с капчей
    form = NetForm()
    return render_template('index.html', form=form)


# Функция-контроллер на POST метод
@app.route('/', methods=['POST'])
def upload_file():
    # создание формы с капчей
    form = NetForm()
    if request.method == 'POST':
        # проверяет содержит запрос файлы или нет
        if 'files[]' not in request.files:
            flash('Файлы не найдены')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        # проверка на количество файлов
        if len(files) != 2:
            flash('Загрузите 2 изображения')
            return redirect(request.url)
        # проверка форматов и сохранение изображений
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Файлы успешно загружены')

        final_filename = ''

        # в зависимости от параметра, переданного пользователем выполняется способ склеивания изображения
        if request.form.get('mergetype').__eq__('Вертикальный'):
            final_filename = merge_vertical(files[0].filename, files[1].filename)
        elif request.form.get('mergetype').__eq__('Горизонтальный'):
            final_filename = merge_horizontal(files[0].filename, files[1].filename)

        # вызов функций цветового анализа для исходных и склееного изображений
        color_recogniser.analyse_color("./static/uploads/" + final_filename)
        color_recogniser.analyse_color("./static/uploads/" + files[0].filename)
        color_recogniser.analyse_color("./static/uploads/" + files[1].filename)

        # возврат страницы index.html с адресами всех изображений
        return render_template('index.html', filename=final_filename,
                               color_analyse1='analyse_' + files[0].filename,
                               color_analyse2='analyse_' + files[1].filename,
                               color_analyse_res='analyse_' + final_filename,
                               form=form)


# Функция отображения изображения
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


# Функция склеивания изображения по вертикали
def merge_vertical(file_name_1, file_name_2):
    file1_path = UPLOAD_FOLDER + file_name_1
    file2_path = UPLOAD_FOLDER + file_name_2
    images = [Image.open(x) for x in [file1_path, file2_path]]
    widths, heights = zip(*(i.size for i in images))

    # Установка высоты и ширины итогового изображения
    total_width = max(widths)
    max_height = sum(heights)

    # формат и размеры нового изображения
    new_im = Image.new('RGB', (total_width, max_height))

    # склеивание изображений по вертикали (y)
    y_offset = 0
    for im in images:
        new_im.paste(im, (0, y_offset))
        y_offset += im.size[1]

    result_filename = UPLOAD_FOLDER + 'vert-' + file_name_1.rpartition('.')[0] + '-' + file_name_2
    # сохранение нового изображений по переданному адресу (названию)
    new_im.save(result_filename)
    # возврат пути до изображения-результата
    return 'vert-' + file_name_1.rpartition('.')[0] + '-' + file_name_2


# Функция склеивания изображения по горизонтали
def merge_horizontal(file_name_1, file_name_2):
    file1_path = UPLOAD_FOLDER + file_name_1
    file2_path = UPLOAD_FOLDER + file_name_2
    images = [Image.open(x) for x in [file1_path, file2_path]]
    widths, heights = zip(*(i.size for i in images))

    # Установка высоты и ширины итогового изображения
    total_width = sum(widths)
    max_height = max(heights)

    # формат и размеры нового изображения
    new_im = Image.new('RGB', (total_width, max_height))

    # склеивание изображений по горизонтали (x)
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    result_filename = UPLOAD_FOLDER + 'horiz-' + file_name_1.rpartition('.')[0] + '-' + file_name_2
    # сохранение нового изображений по переданному адресу (названию)
    new_im.save(result_filename)
    # возврат пути до изображения-результата
    return 'horiz-' + file_name_1.rpartition('.')[0] + '-' + file_name_2


# Запуск приложения
if __name__ == '__main__':
    app.run()
