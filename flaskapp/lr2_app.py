import os
import random
import string

from PIL import Image
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_recaptcha import ReCaptcha
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.utils import secure_filename

import color_recogniser

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads/'

app.secret_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(24))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# используем капчу и полученные секретные ключи с сайта Google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdiKukUAAAAAGOH6Wve-LnDOwd5AyoGFSf4mRzm'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdiKukUAAAAAG16BmzRIq51tWhmQKRQ281q9wOt'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'custom'}

recaptcha = ReCaptcha(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class NetForm(FlaskForm):
    recaptcha = RecaptchaField()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    form = NetForm()
    return render_template('index.html', form=form)


@app.route('/', methods=['POST'])
def upload_file():
    form = NetForm()
    if request.method == 'POST':
        # check if the post request has the files part
        if 'files[]' not in request.files:
            flash('Файлы не найдены')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        if len(files) != 2:
            flash('Загрузите 2 изображения')
            return redirect(request.url)
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Файлы успешно загружены')

        final_filename = ''

        if request.form.get('mergetype').__eq__('Вертикальный'):
            final_filename = merge_vertical(files[0].filename, files[1].filename)
        elif request.form.get('mergetype').__eq__('Горизонтальный'):
            final_filename = merge_horizontal(files[0].filename, files[1].filename)

        color_recogniser.analyse_color("./static/uploads/" + final_filename)
        color_recogniser.analyse_color("./static/uploads/" + files[0].filename)
        color_recogniser.analyse_color("./static/uploads/" + files[1].filename)

        return render_template('index.html', filename=final_filename,
                               color_analyse1='analyse_' + files[0].filename,
                               color_analyse2='analyse_' + files[1].filename,
                               color_analyse_res='analyse_' + final_filename,
                               form=form)


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


def merge_vertical(file_name_1, file_name_2):
    file1_path = UPLOAD_FOLDER + file_name_1
    file2_path = UPLOAD_FOLDER + file_name_2
    images = [Image.open(x) for x in [file1_path, file2_path]]
    widths, heights = zip(*(i.size for i in images))

    total_width = max(widths)
    max_height = sum(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    y_offset = 0
    for im in images:
        new_im.paste(im, (0, y_offset))
        y_offset += im.size[1]

    result_filename = UPLOAD_FOLDER + 'vert-' + file_name_1.rpartition('.')[0] + '-' + file_name_2
    new_im.save(result_filename)
    return 'vert-' + file_name_1.rpartition('.')[0] + '-' + file_name_2


def merge_horizontal(file_name_1, file_name_2):
    file1_path = UPLOAD_FOLDER + file_name_1
    file2_path = UPLOAD_FOLDER + file_name_2
    images = [Image.open(x) for x in [file1_path, file2_path]]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    result_filename = UPLOAD_FOLDER + 'horiz-' + file_name_1.rpartition('.')[0] + '-' + file_name_2
    new_im.save(result_filename)
    return 'horiz-' + file_name_1.rpartition('.')[0] + '-' + file_name_2


if __name__ == '__main__':
    app.run()
