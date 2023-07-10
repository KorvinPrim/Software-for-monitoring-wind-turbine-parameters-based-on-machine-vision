def find__wind_classification(speed_wind):
        if -1 <= speed_wind <= 0.2 :
            return 'Штиль'

        if 0.3 <= speed_wind <= 1.5 :
            return 'Тихий'

        if 1.6 <= speed_wind <= 3.3 :
            return 'Лёгкий'

        if 3.4 <= speed_wind <= 5.4 :
            return 'Слабый'

        if 5.5 <= speed_wind <= 7.9 :
            return 'Умеренный'

        if 8.0 <= speed_wind <= 10.7 :
            return 'Свежий'

        if 10.8 <= speed_wind <= 13.8 :
            return 'Сильный'

        if 13.9 <= speed_wind <= 17.1 :
            return 'Крепкий'

        if 17.2 <= speed_wind <= 20.7 :
            return 'Очень крепкий'

        if 20.8 <= speed_wind <= 24.4 :
            return 'Шторм'

        if 24.5 <= speed_wind <= 28.4 :
            return 'Сильный шторм'

        if 28.5 <= speed_wind <= 32.6 :
            return 'Жестокий шторм'

        if 32.7 <= speed_wind :
            return 'Ураган'

