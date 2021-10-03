from collections import Counter

import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


# Основная функия цветового анализа изображения
# В качестве аргумента принимает путь до изображения
def analyse_color(image_path):
    # считывает изображение
    image = cv2.imread(image_path)
    # конвертирует формат изображения из BGR в RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image)
    modified_image = prep_image(image)
    color_analysis(modified_image, image_path)


# Функция конвертации из RGB формата в HEX цветовой формат,:
# вместо трех различных значений (красный, зеленный, синий) будет возвращено
# одно HEX значение.
def rgb_to_hex(rgb_color):
    hex_color = "#"
    for i in rgb_color:
        i = int(i)
        hex_color += ("{:02x}".format(i))
    return hex_color


# Функция выполняющая преподготовку изображения:
# изменяет размер и форму. Измение размера опционально,
# но измение формы обязательтно для проведения цветового анализа.
# Возвращает измененное изображение.
def prep_image(raw_img):
    modified_img = cv2.resize(raw_img, (900, 600), interpolation=cv2.INTER_AREA)
    modified_img = modified_img.reshape(modified_img.shape[0] * modified_img.shape[1], 3)
    return modified_img


# Функия цветового анализа:
def color_analysis(img, title: str):
    # KMeans() для кластеризации верхних цветов.
    # Внутри функции передаем значение того, на сколько кластеров мы хотим разделить наш анализ
    clf = KMeans(n_clusters=5)
    # После кластеризации прогнозируем, какие цвета будут иметь наибольший "вес",
    # то есть те, что занимают наибольшую площадь изображения.
    color_labels = clf.fit_predict(img)
    center_colors = clf.cluster_centers_

    # Counter создает контейнер для элементов в ключах словаря, а их объем сохраняется в виде значений словаря.
    counts = Counter(color_labels)
    ordered_colors = [center_colors[i] for i in counts.keys()]

    # переводим в HEX значения
    hex_colors = [rgb_to_hex(ordered_colors[i]) for i in counts.keys()]
    # визуализация результата
    plt.figure(figsize=(12, 8))
    plt.pie(counts.values(), labels=hex_colors, colors=hex_colors)
    # сохранение резульата в папку uploads
    plt.savefig('./static/uploads/analyse_' + title.split("/")[3])
