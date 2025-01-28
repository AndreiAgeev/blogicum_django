# Проект blogicum_django
## Описание:
Сервис "Блогикум", наспианный с использованием Django в рамках обучения на платформе Yandex.Practicum.
Представляет собой вариацию простейших блогов пользователей - зарегистрированные пользователи могут постить текстовые посты, а также оставлять к ним комментарии. Пользователи могут редактировать и удалять свои посты и комментарии. Посты имеют метки категорий и локаций, по которым их можно сортировать.
## Как запустить парсер на локальной машине:
Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:AndreiAgeev/blogicum_django.git
```

```
cd blogicum_django
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv .venv
```

* Если у вас Linux/macOS

    ```
    source .venv/bin/activate
    ```

* Если у вас Windows

    ```
    source .venv/scripts/activate
    ```

Обновить pip и установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Выполнить миграции и запустить проект:
```
python3 manage.py migrate
```
```
python3 manage.py runserver
```
Проект будет доступен по адресу http://127.0.0.1:8000/.
## Авторы:
**Идея и ТЗ** - Yandex.Practicum<br />
**Реализация** - Andrei Ageev (@AndreiAgeev)
