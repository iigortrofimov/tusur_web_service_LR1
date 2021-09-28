import os
import random
import string

from flask import Flask
from flask import render_template
# обязательно добавить для работы со стандартными шаблонами
from flask_bootstrap import Bootstrap
# модули работы с формами и полями в формах
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField
# модули валидации полей формы
from wtforms.validators import DataRequired

# подключаем наш модуль и переименовываем
# для исключения конфликта имен
import net as neuronet


class NetForm(FlaskForm):
    # поле для введения строки, валидируется наличием данных
    # валидатор проверяет введение данных после нажатия кнопки submit
    # и указывает пользователю ввести данные, если они не введены
    # или неверны
    openid = StringField('openid', validators=[DataRequired()])
    # поле загрузки файла
    # здесь валидатор укажет ввести правильные файлы
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    # поле формы с capture
    recaptcha = RecaptchaField()
    # кнопка submit, для пользователя отображена как send
    submit = SubmitField('send')


app = Flask(__name__)
# используем csrf токен, можете генерировать его сами
SECRET_KEY = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(24))
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY
# используем капчу и полученные секретные ключи с сайта Google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdiKukUAAAAAGOH6Wve-LnDOwd5AyoGFSf4mRzm'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdiKukUAAAAAG16BmzRIq51tWhmQKRQ281q9wOt'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

bootstrap = Bootstrap(app)


# функция обработки запросов на адрес 127.0.0.1:5000/net
# модуль проверки и преобразование имени файла
# для устранения в имени символов типа / и т.д.
# метод обработки запроса GET и POST от клиента
@app.route("/net", methods=['GET', 'POST'])
def net():
    # создаем объект формы
    form = NetForm()
    # обнуляем переменные, передаваемые в форму
    filename = None
    neurodic = {}
    # проверяем нажатие сабмит и валидацию введенных данных
    if form.validate_on_submit():
        # файлы с изображениями читаются из каталога static
        filename = os.path.join('./static', secure_filename(form.upload.data.filename))
        fcount, fimage = neuronet.read_image_files(10, './static')
        # передаем все изображения в каталоге на классификацию
        # можете изменить немного код и передать только загруженный файл
        decode = neuronet.getresult(fimage)
        # записываем в словарь данные классификации
        for elem in decode:
            neurodic[elem[0][1]] = elem[0][2]
        # сохраняем загруженный файл
        form.upload.data.save(filename)
        # передаем форму в шаблон, так же передаем имя файла и результат работы нейронной
        # сети, если был нажат сабмит, либо передадим falsy значения
    return render_template('net.html', form=form, image_name=filename, neurodic=neurodic)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
