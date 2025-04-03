# Поддержка Лидеров в Москве
## Платформы
    Windows, Linux
## Язык программирования
    Python
## Установка
### Linux
#### 1. Скопируйте файлы из репозитория в отдельную папку:
    git clone https://github.com/Tribor0/Moscow_support.git
#### 2. Создайте виртуальное окружение и активируйте его:
    python3 -m venv venv && source venv/bin/activate
#### 3. Установите зависимости:
    pip3 install -r requirements.txt
#### 4. Установите PostgreSQL и импортироуйте database.sql
#### 5. Установите свои значения в файле .env:
#### 6. Запустите проект
    python3 main.py
### Windows 
#### 1. Скопируйте файлы из репозитория в отдельную папку:
    git clone https://github.com/Tribor0/Moscow_support.git
#### 2. Создайте виртуальное окружение и активируйте его:
    python.exe -m venv venv && source venv/bin/activate
#### 3. Установите зависимости:
    pip install -r requirements.txt
#### 4. Установите PostgreSQL и импортироуйте database.sql
#### 5. Установите свои значения в файле .env:
#### 6. Запустите проект
    python.exe main.py
## Зависимости
### Python
### Библиотеки Python
    psycopg2~=2.9.10
    python-telegram-bot~=22.0
    pydantic-settings~=2.8.1
    SQLAlchemy~=2.0.40
## Авторы
    Кравцов Артём Витальевич
    Гурьев Константин Михайлович