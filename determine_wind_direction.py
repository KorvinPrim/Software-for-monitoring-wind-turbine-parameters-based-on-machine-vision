import cv2 as cv
import cv2
import numpy as np
import math

def find_rectangle(fn,color_number):
    hsv_min = np.array((114, 90, 194), np.uint8)
    hsv_max = np.array((132, 255, 255), np.uint8)
    if color_number == 0:
        #blue
        hsv_min = np.array((114, 90, 194), np.uint8)
        hsv_max = np.array((132, 255, 255), np.uint8)
    elif color_number == 1:
        #green
        hsv_min = np.array((35, 38, 255), np.uint8)
        hsv_max = np.array((108, 255, 255), np.uint8)
    elif color_number == 2:
        #orange
        hsv_min = np.array((10, 87, 220), np.uint8)
        hsv_max = np.array((26, 255, 255), np.uint8)
    elif color_number == 3:
        #yellow
        hsv_min = np.array((10, 9, 255), np.uint8)
        hsv_max = np.array((50, 245, 255), np.uint8)


    center = (0,0)
    color_blue = (255, 0, 0)
    color_yellow = (0, 255, 255)
    img = fn
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    thresh = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр
    contours0, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # перебираем все найденные контуры в цикле
    for cnt in contours0:
        rect = cv.minAreaRect(cnt)  # пытаемся вписать прямоугольник
    if len(contours0) != 0:
        box = cv.boxPoints(rect)  # поиск четырех вершин прямоугольника

        box = np.intp(box)  # округление координат
        center = (int(rect[0][0]), int(rect[0][1]))
        area = int(rect[1][0] * rect[1][1])  # вычисление площади
        # вычисление координат двух векторов, являющихся сторонам прямоугольника
        edge1 = np.intp((box[1][0] - box[0][0], box[1][1] - box[0][1]))
        edge2 = np.intp((box[2][0] - box[1][0], box[2][1] - box[1][1]))
        # выясняем какой вектор больше
        usedEdge = edge1
        if cv.norm(edge2) > cv.norm(edge1):
            usedEdge = edge2
        reference = (1, 0)  # горизонтальный вектор, задающий горизонт
        # вычисляем угол между самой длинной стороной прямоугольника и горизонтом
        #angle = 180.0 / math.pi * math.acos((reference[0] * usedEdge[0] + reference[1] * usedEdge[1]) / (cv.norm(reference) * cv.norm(usedEdge)))  ###Просчёт угла отключён
        if area > 500:
            cv.drawContours(img, [box], 0, (255, 0, 0), 2)  # рисуем прямоугольник
            cv.circle(img, center, 5, color_yellow, 2)  # рисуем маленький кружок в центре прямоугольника
            # выводим в кадр величину угла наклона
            #cv.putText(img, "%d" % int(angle), (center[0] + 20, center[1] - 20), cv.FONT_HERSHEY_SIMPLEX, 1, color_yellow, 2) ###Вывод угла отключён
    return img, center


def determining_direction(fn,initial_direction):


    b_img, blue_center = find_rectangle(fn,0)

    g_img, green_center = find_rectangle(fn, 1)

    o_img, orange_center = find_rectangle(fn, 2)

    y_img, yellow_center = find_rectangle(fn, 3)

    color_center = None

    if 500<blue_center[0]<700:
        fn = b_img
        color_center = 'blue'
    elif 500<green_center[0]<700:
        fn = g_img
        color_center = 'green'
    elif 500<orange_center[0]<700:
        fn = o_img
        color_center = 'orange'
    elif 500<yellow_center[0]<700:
        fn = y_img
        color_center = 'yellow'



    return fn,color_center

if __name__ == '__main__':
    # initialize the camera
    # If you have multiple camera connected with
    # current device, assign a value in cam_port
    # variable according to that
    #cam_port = 'http://192.168.1.17:81/stream'
    cam_port = 'анимация_пропеллера_с_цветовыми_направлениями.mp4'

    # создадим объект VideoCapture для захвата видео
    cap = cv2.VideoCapture(cam_port)

    # Если не удалось открыть файл, выводим сообщение об ошибке
    if cap.isOpened() == False:
        print('Не возможно открыть файл')

    # Пока файл открыт
    while cap.isOpened():
        # поочередно считываем кадры видео
        fl, img = cap.read()
        # если кадры закончились, совершаем выход
        if img is None:
            break
        # выводим текущий кадр на экран

        img,actual_color = determining_direction(img,1)
        print(actual_color)
        #img,cent = find_rectangle(img,3)

        cv2.imshow("Cat", img)

        # при нажатии клавиши "q", совершаем выход
        if cv2.waitKey(25) == ord('q'):
            break

    # освобождаем память от переменной cap
    cap.release()
    # закрываем все открытые opencv окна
    cv2.destroyAllWindows()
