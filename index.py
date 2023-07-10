# import module

from PIL import Image
from datetime import datetime
from pathlib import Path

import streamlit as st
import time
import random
import cv2


import rectangle_search
import determine_wind_direction
import Wi_pw

#########################
# Подключение камеры
# cam_port = 'http://192.168.1.17:81/stream'

# Имитация подключения камеры от видео
project_folder = Path('imd_wind/')

cam_port = Path('animation for machine vision.mp4')

cap = cv2.VideoCapture(str(cam_port))
fl, img = cap.read()

video_file = open(str(cam_port), 'rb')
video_bytes = video_file.read()

#########################




# Словарь розы ветров
wind_rose = {1: 'Север', 2: 'Северо-Восток', 3: 'Восток', 4: 'Юго-Восток', 5: 'Юг', 6: 'Юго-Запад', 7: 'Запад',
             8: 'Северо-Запад'}

#Роза ветров
wind_rose_img = {1: Image.open(project_folder / 'N.jpg'),
                 2: Image.open(project_folder / 'NE.jpg'),
                 3: Image.open(project_folder / 'E.jpg'),
                 4: Image.open(project_folder / 'SE.jpg'),
                 5: Image.open(project_folder / 'S.jpg'),
                 6: Image.open(project_folder / 'SW.jpg'),
                 7: Image.open(project_folder / 'W.jpg'),
                 8: Image.open(project_folder / 'NW.jpg')}
direction_now_wind = 1
# Объявляем переменные для 4 точек в которых будет обновление замера скорости вращения пропеллера
min_x = 0
min_x_y = 0

max_x = 2000
max_x_y = 0

min_y = 0
min_y_x = 0

max_y = 2000
max_y_x = 0

# C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_64>python -m streamlit run C:/Users/Korvin/Documents/диплом/index.py
# give a title to our app
initial_time = 0
working_hours = 0
angle = 0
last_angle = 0
rotation_speed = 0

T_wind = 0  # Период оборота винта
x_min_wind = 0  # Минимальная координата х по которой будем определять период

checking_minimum = True

list_T = []
list_obs_s = []
list_wind_speed = [0]
list_wind_direction = [1]

turns_done = 0

passed_semicircle = True  # Проверка на преодоления половины круга после последнего замера, что бы не было повтороного считывания периода

past_color = None  # Цвет прямоугольника по центру

list_center_coordinates_x = []  # множество координат х центра
list_center_coordinates_y = []  # множество координат y центра

time_clock = True
wind_speed_list = list(range(1, 19))


def find_period(min_x, max_x, center):
    global turns_done
    global passed_semicircle
    global timer_T
    global list_T

    if min_x != 0 and min_x - 5 < center[
        0] < min_x + 5 and passed_semicircle:  # Ловим проходы центра по минимуму х что бы записать период обращения
        T_wind = initial_time - timer_T
        passed_semicircle = False
        if turns_done != 0:  # Отсекаем первый некорректный промер
            list_T.append(T_wind)
        timer_T = time.time()
        turns_done += 1

    if max_x != 0 and max_x - 5 < center[0] < max_x + 5:
        passed_semicircle = True

    if list_T:
        obs_s = 1 / list_T[-1] * 60
        list_obs_s.append(obs_s)
        return obs_s
    else:
        obs_s = 0
        return None


####Блок создания HTML страницы####
st.set_page_config(layout="wide")

title = st.title('Панель мониторинга и управления ВГУ')
title.markdown("<h1 style='text-align: center; color: red;'>Панель мониторинга и управления ВГУ</h1>",
               unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

with col1:
    st.write("Текущее время:")
    st.text("Скорость ветра, м/с:")
    st.write("Скорость вращения лопастей, обр/мин:")
    st.write("Класс ветра в данный момент:")
    st.write("Класс ветра за последние 3 часа:")
    st.write("Коэффициент порывистости:")


with col2:
    t = st.success(working_hours)
    wind_speed = st.success(random.randint(0, len(wind_speed_list) - 1))
    label_rotation_speed = st.success(rotation_speed)
    wind_class = st.success(Wi_pw.find__wind_classification(0))
    wind_class_time = st.success(Wi_pw.find__wind_classification(0))
    wind_gustiness = st.success(0)

with col3:
    label_wind_direction = st.text('Направление ветра: {}'.format(wind_rose[direction_now_wind]))
    wind_direction_image = st.image(wind_rose_img[1])

with col4:
    st.text("График скорости ветра, м/с")
    wind_speed_graph = st.line_chart(list_wind_speed)

col1, col2 = st.columns(2)

# Добавим видео(обновляемую картинку) на страницу HTML
with col1:
    # st.video(video_bytes)
    picture_windmill_video = st.image(img)
with col2:
    st.text("График направления ветра")
    wind_direction_chart = st.line_chart(
        list_wind_direction)  ###28 03 2023 доделать график для направлений!"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

####Конец блока создания HTML страницы####

if cap.isOpened() == False:
    print('Не возможно открыть файл')

timer_start = time.time()
schedule_timer = time.time()
drawing_update_timer = time.time()
wind_direction_measurement_timer = time.time()
timer_measuring_rotation_period = time.time()
obs_s = 0
####Цикл обновления данных на странице
while cap.isOpened():
    initial_time = time.time()

    # поочередно считываем кадры видео
    fl, img = cap.read()
    # если кадры закончились, совершаем выход
    if img is None:
        break

    ########################################
    # Определяем прямоугольник какого цвета по центру кадра, что бы определить направление ветра
    if initial_time - wind_direction_measurement_timer > 0.5:
        img, color_rectangle = determine_wind_direction.determining_direction(img, 1)
        # Определяем изменился ли цвет прямоугольника по центру
        if color_rectangle and color_rectangle != past_color:
            if past_color == 'blue' and color_rectangle == 'yellow':
                direction_now_wind += 1
            elif past_color == 'blue' and color_rectangle == 'orange':
                direction_now_wind -= 1
            ###
            elif past_color == 'green' and color_rectangle == 'orange':
                direction_now_wind += 1
            elif past_color == 'green' and color_rectangle == 'yellow':
                direction_now_wind -= 1
            ###
            elif past_color == 'orange' and color_rectangle == 'blue':
                direction_now_wind += 1
            elif past_color == 'orange' and color_rectangle == 'green':
                direction_now_wind -= 1
            ###
            elif past_color == 'yellow' and color_rectangle == 'green':
                direction_now_wind += 1
            elif past_color == 'yellow' and color_rectangle == 'blue':
                direction_now_wind -= 1
            ###
            if direction_now_wind > 8:
                direction_now_wind = 1
            elif direction_now_wind < 1:
                direction_now_wind = 8

            list_wind_direction.append(direction_now_wind)

            past_color = color_rectangle

            wind_direction_measurement_timer = time.time()

    ########################################
    # выводим текущий кадр на экран
    img, center = rectangle_search.find_rectangle(img)

    ####Начало блока подсчёта скорости вращения лопастей####
    # Отсчёт для определения минимальной/максимальной х/у центра, что бы завязать на неё период, в сумме 4 точки
    if initial_time - timer_start > 3 and checking_minimum:
        for i in range(len(list_center_coordinates_x)):

            if list_center_coordinates_x[i] > min_x:
                min_x = list_center_coordinates_x[i]
                min_x_y = list_center_coordinates_y[i]
            if list_center_coordinates_x[i] < max_x:
                max_x = list_center_coordinates_x[i]
                max_x_y = list_center_coordinates_y[i]

        for i in range(len(list_center_coordinates_y)):
            if list_center_coordinates_y[i] > min_y:
                min_y = list_center_coordinates_y[i]
                min_y_x = list_center_coordinates_x[i]
            if list_center_coordinates_y[i] < max_y:
                max_y = list_center_coordinates_y[i]
                max_y_x = list_center_coordinates_x[i]

        checking_minimum = False
        timer_T = time.time()
    elif checking_minimum:
        # Записываем координаты прохода центра пропеллера что бы определить окружность
        list_center_coordinates_x.append(center[0])
        list_center_coordinates_y.append(center[1])

    # Создаём две точки промера периода
    obs_s_1 = find_period(min_x, max_x, center)
    obs_s_2 = find_period(min_y, max_y, center)
    if obs_s_1:
        obs_s = float('%.2f' % obs_s_1)
    if obs_s_2:
        obs_s = float('%.2f' % obs_s_2)
    if obs_s == 0 or type(obs_s) == str:
        obs_s = 'Устанавливается, осталось: {} с'.format(str(10 - (initial_time - timer_start))[:3])

    ####Конец блока подсчёта скорости вращения лопастей и направления ветра####

    # Отображение изображения в отдельном окне
    # cv2.imshow("Cat", img)
    # при нажатии клавиши "q", совершаем выход

    ##### Блок обновления данных на странице####
    if cv2.waitKey(25) == ord('q'):
        break

    t.markdown(str(datetime.now())[:-10])

    # Выводим скорость ветра, если обороты определены как число, если нет пропускаем строку таймера
    if type(obs_s) == float:
        w_speed = float('%.2f' % (
            ((2*(((obs_s**3)/60)*(4**5)*0.5)
        /(4*3.14))**0.5
        )))

        if initial_time - schedule_timer > 1:
            list_wind_speed.append(w_speed)
            schedule_timer = time.time()

        wind_speed.markdown(w_speed)
        wind_class.markdown(Wi_pw.find__wind_classification(w_speed))
        wind_class_time.markdown(Wi_pw.find__wind_classification(sum(list_wind_speed) / len(list_wind_speed)))
        wind_gustiness.markdown(round(max(list_wind_speed[1:])/min(list_wind_speed[1:])),1)




    else:
        wind_speed.markdown(obs_s)
        wind_class.markdown(obs_s)
        wind_class_time.markdown(obs_s)
        wind_gustiness.markdown(obs_s)

    # wind_direction.markdown(wind_rose[direction_now_wind])

    label_wind_direction.text('Направление ветра: {}'.format(wind_rose[direction_now_wind]))
    label_rotation_speed.markdown(obs_s)

    if time.time()-drawing_update_timer > 1:
        wind_direction_image.image(wind_rose_img[direction_now_wind])
        wind_speed_graph.line_chart(list_wind_speed)
        wind_direction_chart.line_chart(list_wind_direction)
        drawing_update_timer = time.time()


    picture_windmill_video.image(img)

    #####Конец блока обновления данных на странице####

# освобождаем память от переменной cap
cap.release()
# закрываем все открытые opencv окна
cv2.destroyAllWindows()

# C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_64>python -m streamlit run C:/Users/Korvin/Documents/диплом/index.py
