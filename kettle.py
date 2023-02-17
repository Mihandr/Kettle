import msvcrt
import time
import threading
import configparser
import logging


class TimeoutExpired(Exception):
    """Отдельный класс для обработки исключений истечения времени"""
    pass


class Kettle:
    """
    Класс 'Чайник' эмулирует работу настоящего электрического чайника.
    Имеет слудующие методы:
    - water_level(self) и water_level(self, water): Методы для работы с переменной __water_level
    - button_stop(self): Кнопка выключения чайника
    - button_start(self): Кнопка включения чайника
    - boil(self): Метод выполняющий кипячение
    - top_up(self, new_water): Метод для того чтобы долить воды
    - check_water(self, water): Метод для проверки входящих данных
    - input_with_timeout(self, timeout, timer=time.monotonic): Метод для отслеживания нажатия пользователем клавиши
    - help(self): Информационный метод
    """

    def __init__(self, water=0.0):
        """Инициализация класса. Загрузка переменных из файла конфигурации."""
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")  # Запись логов в файл
        config = configparser.ConfigParser()
        config.read("settings.ini")
        self.__max_water_level = float(config["Kettle"]["water_level"])  # Максимальная вместимость чайника
        self.__time_boil = int(config["Kettle"]["time_boil"])  # Время кипечения
        if self.__time_boil == 0:  # Проверка входных данных
            logging.warning('Невозможно установить время кипячения на 0. Поднято до 1 секунды.')
            print('Невозможно установить время кипячения на 0. Поднято до 1 секунды.')
            self.__time_boil = 1
        if self.__max_water_level == 0:  # Проверка входных данных
            logging.warning('Невозможно установить максимальную вместимость на 0. Поднято до 0.1.')
            print('Невозможно установить максимальную вместимость на 0. Поднято до 0.1.')
            self.__max_water_level = 0.1
        self.__temperature_stop = int(config["Kettle"]["temperature"])  # Уровень температуры для выключения
        water = self.check_water(water)  # Проверка уровня воды и правильности типа входящих данных
        self.__water_level = water  # Ввод пользовательской информации
        self.__button_position = False  # Кнопка Вкл/Выкл

    @property
    def water_level(self):
        """Метод для обращения к переменной извне класса"""
        return self.__water_level

    @water_level.setter
    def water_level(self, water):
        """Метод для изменения пременной извне класса"""
        water = self.check_water(water)
        self.__water_level = water

    def button_stop(self):
        """Метод выключения чайника"""
        self.__button_position = False
        logging.info('Чайник выключен')
        print('Чайник выключен')

    def button_start(self):
        """Метод включения чайника"""
        logging.info('Чайник включен')
        print('Чайник включен')
        self.__button_position = True
        threading.Thread(target=self.boil, daemon=True).start()  # Создание отдельного потока для кипячения
        try:
            self.input_with_timeout(self.__time_boil + 1)  # Функция для отлова пользовательского ввода
        except TimeoutExpired:
            pass

    def boil(self):
        """Метод для реализации кипячения"""
        temperature = 0
        shag_temp = 100 // self.__time_boil
        if self.__water_level == 0:  # Поверка уровня воды
            logging.warning(f'В чайнике нет воды! Уровень: {self.__max_water_level}')
            print(f'В чайнике нет воды! Уровень: {self.__max_water_level}')
        else:
            for second in range(self.__time_boil):  # Каждую секунду выполнять вывод информации
                if (self.__button_position) and (temperature < self.__temperature_stop):
                    # Проверка включен ли чайник и не достигнут ли заданный уровень температуры
                    time.sleep(1)
                    temperature += shag_temp
                    logging.info(f'Температура чайника {temperature}°С')
                    print(f'Температура чайника {temperature}°С')
            if temperature >= self.__temperature_stop:  # Если достигнута нужная температура
                logging.info('Достигнута необходимая температура')
                print('Достигнута необходимая температура')
            logging.info('Чайник закипел')
            print('Чайник закипел')
        self.button_stop()

    def top_up(self, new_water):
        """Метод для реализации добавления воды"""
        new_water = self.check_water(new_water)
        if self.__water_level + new_water > self.__max_water_level:  # Если воды больше максимума, лишнее выльется
            logging.warning(f'Лишняя вода вылилась! Осталось только {self.__max_water_level}')
            print(f'Лишняя вода вылилась! Осталось только {self.__max_water_level}')
            self.__water_level = self.__max_water_level
        else:
            self.__water_level = self.__water_level + new_water

    def check_water(self, water):
        """Метод проверки входдных данных"""
        if isinstance(water, int) or isinstance(water, float):  # Если число, то продолжаем работу
            if water > self.__max_water_level:
                logging.warning(f'Лишняя вода вылилась! Осталось только {self.__max_water_level}')
                print(f'Лишняя вода вылилась! Осталось только {self.__max_water_level}')
                water = self.__max_water_level
        else:  # Если не число, то ничего не лить
            logging.warning('Только вода! Попробуй долить!')
            print('Только вода! Попробуй долить!')
            water = 0.0
        return water

    def input_with_timeout(self, timeout, timer=time.monotonic):
        """Метод для отлова пользовательского ввода. Таймер нужен для отмены ожидания ввода"""
        endtime = timer() + timeout
        while timer() < endtime:
            if not self.__button_position:  # Если чайник выключен, ждать нечего
                break
            if msvcrt.kbhit():  # Если пользователь нажал клавишу, выключить чайник
                logging.info('Чайник остановлен')
                print('Чайник остановлен')
                self.button_stop()
                break
            time.sleep(0.04)
        raise TimeoutExpired

    def help(self):
        """Информационный метод"""
        logging.info('Запрошена информация')
        print('Запрошена информация')
        print(f'Время кипечения: {self.__time_boil}')
        print(f'Максимальная вместимость чайника: {self.__max_water_level }')
        print(f'Уровень температуры для выключения : {self.__temperature_stop}')
        print(f'Уровень воды : {self.__water_level}')


if __name__ == '__main__':
    pass



