import cv2 as cv
import cv2
import numpy as np

def find_rectangle(fn):
    hsv_min = np.array((35, 38, 0), np.uint8)
    hsv_max = np.array((255, 255, 255), np.uint8)
    # 1600x1200
    # 10
    # -2
    # -2
    # 2
    # Negative
    # Home
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
        box = np.int0(box)  # округление координат
        center = (int(rect[0][0]), int(rect[0][1]))
        area = int(rect[1][0] * rect[1][1])  # вычисление площади
        # вычисление координат двух векторов, являющихся сторонам прямоугольника
        edge1 = np.int0((box[1][0] - box[0][0], box[1][1] - box[0][1]))
        edge2 = np.int0((box[2][0] - box[1][0], box[2][1] - box[1][1]))
        # выясняем какой вектор больше
        usedEdge = edge1
        if cv.norm(edge2) > cv.norm(edge1):
            usedEdge = edge2
        reference = (1, 0)  # горизонтальный вектор, задающий горизонт
        # вычисляем угол между самой длинной стороной прямоугольника и горизонтом
        # angle = 180.0 / math.pi * math.acos((reference[0] * usedEdge[0] + reference[1] * usedEdge[1]) / (cv.norm(reference) * cv.norm(usedEdge)))  ###Просчёт угла отключён
        if area > 500:
            cv.drawContours(img, [box], 0, (255, 0, 0), 2)  # рисуем прямоугольник
            cv.circle(img, center, 5, color_yellow, 2)  # рисуем маленький кружок в центре прямоугольника
            # выводим в кадр величину угла наклона
            # cv.putText(img, "%d" % int(angle), (center[0] + 20, center[1] - 20), cv.FONT_HERSHEY_SIMPLEX, 1, color_yellow, 2) ###Вывод угла отключён
    return img, center



if __name__ == '__main__':
    # initialize the camera
    # If you have multiple camera connected with
    # current device, assign a value in cam_port
    # variable according to that
    cam_port = 'http://192.168.1.17:81/stream'

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

        img, angel = find_rectangle(img)

        cv2.imshow("Cat", img)

        # при нажатии клавиши "q", совершаем выход
        if cv2.waitKey(25) == ord('q'):
            break

    # освобождаем память от переменной cap
    cap.release()
    # закрываем все открытые opencv окна
    cv2.destroyAllWindows()
