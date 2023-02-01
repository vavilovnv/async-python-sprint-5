# Проектное задание пятого спринта

Спроектировать и разработать файловое хранилище, которое позволяет хранить различные типы файлов - документы, фотографии, другие данные.

Кроме этого, выберите и реализуйте из списка дополнительные требования. У каждого требования есть определённая сложность, от которой зависит количество баллов. Необходимо выбрать такое количество заданий, чтобы общая сумма баллов больше или равна 2. Выбор заданий никак не ограничен: можно выбрать все простые или одно среднее и два простых, или одно продвинутое, или решить все.


## Установка и запуск

Сервис развернут в Яндекс.Облаке по адресу 51.250.41.39/api/openapi

Для запуска сервиса необходимо:

1. В папке проекта создать и заполнить .env файл по аналогии с .env_example

2. Запустить контейнеры с приложениями:
```
sudo docker-compose up --build -d
```

Будет запущено четыре контейнера:
* postgres-fastapi - контейнер с postgresql
* cache - контейнер с Redis
* file-server - контейнер с бэкендом на fastapi
* nginx - одноименный web-сервер


3. Выполнить миграции
```
sudo docker-compose exec file-server alembic upgrade head
```

Для запуска тестов находясь в папке проекта выполнить следующие команды:
```
# создать виртуальное окружение
python3 -m venv venv

# активировать вируальное окружение
source venv/bin/activate

# установить зависимости
pip install requirements.txt

# запустить тесты
pytest ./src/tests/test_main.py
```


## Описание задания

Реализовать **http-сервис**, который обрабатывает поступающие запросы. Сервер стартует по адресу `http://127.0.0.1:8080`.

<details>
<summary> Список необходимых эндпойнтов </summary>

1. Статус активности связанных сервисов

```
GET /ping
```
Получить информацию о времени доступа ко всем связанным сервисам, например, к БД, кэшам, примонтированным дискам, etc.

**Response**
```json
{
    "db": 1.27,
    "cache": 1.89,
    ...
    "service-N": 0.56
}
```

2. Регистрация пользователя.

```
POST /register
```
Регистрация нового пользователя. Запрос принимает на вход логин и пароль для создания новой учетной записи.


3. Авторизация пользователя.

```
POST /auth
```
Запрос принимает на вход логин и пароль учетной записи и возвращает авторизационный токен. Далее все запросы проверяют наличие токена в заголовках - `Authorization: Bearer <token>`


4. Информация о загруженных файлах

```
GET /files/list
```
Вернуть информацию о ранее загруженных файлах. Доступно только авторизованному пользователю.

**Response**
```json
{
    "account_id": "AH4f99T0taONIb-OurWxbNQ6ywGRopQngc",
    "files": [
          {
            "id": "a19ad56c-d8c6-4376-b9bb-ea82f7f5a853",
            "name": "notes.txt",
            "created_ad": "2020-09-11T17:22:05Z",
            "path": "/homework/test-fodler/notes.txt",
            "size": 8512,
            "is_downloadable": true
          },
        ...
          {
            "id": "113c7ab9-2300-41c7-9519-91ecbc527de1",
            "name": "tree-picture.png",
            "created_ad": "2019-06-19T13:05:21Z",
            "path": "/homework/work-folder/environment/tree-picture.png",
            "size": 1945,
            "is_downloadable": true
          }
    ]
}
```


5. Загрузить файл в хранилище

```
POST /files/upload
```
Метод загрузки файла в хранилище. Доступно только авторизованному пользователю.
Для загрузки заполняется полный путь до файла, в который будет загружен/переписан загружаемый файл. Если нужные директории не существуют, то они будут созданы автоматически.
Так же, есть возможность указать путь до директории. В этом случае имя создаваемого файла будет создано в соответствии с текущим передаваемым именем файла.

**Request parameters**
```
{
    "path": <full-path-to-save-file>||<path-to-folder>,
}
```
**Response**
```json
{
    "id": "a19ad56c-d8c6-4376-b9bb-ea82f7f5a853",
    "name": "notes.txt",
    "created_ad": "2020-09-11T17:22:05Z",
    "path": "/homework/test-fodler/notes.txt",
    "size": 8512,
    "is_downloadable": true
}
```


6. Скачать загруженный файл

```
GET /files/download
```
Скачивание ранее загруженного файла. Доступно только авторизованному пользователю.

**Path parameters**
```
/?path=<path-to-file>||<file-meta-id>
```
Возможность скачивания есть как по переданному пути до файла, так и по идентификатору.


</details>


## Дополнительные требования (отметьте выбранные пункты):

- [x] (2 балла) Добавление возможности скачивания в архиве

<details>
<summary> Описание изменений </summary>

```
GET /files/download
```
Path-параметр расширяется дополнительным параметром - `compression_type`. Доступно только авторизованному пользователю.

Дополнительно в `path` можно указать как путь до директории, так и его **UUID**. При скачивании директории будут скачиваться все файлы, находящиеся в нем.

**Path parameters**
```
/?path=[<path-to-file>||<file-meta-id>||<path-to-folder>||<folder-meta-id>] & compression_type"=[zip||tar||7z]
```
</details>

- [ ] (2 балла) Добавление информация об использовании пользователем дискового пространства.

<details>
<summary> Описание изменений </summary>

```
GET /user/status
```
Вернуть информацию о статусе использования дискового пространства и ранее загруженных файлах. Доступно только авторизованному пользователю.

**Response**
```json
{
    "account_id": "taONIb-OurWxbNQ6ywGRopQngc",
    "info": {
        "root_folder_id": "19f25-3235641",
        "home_folder_id": "19f25-3235641"
    },
    "folders": [
        "root": {
            "allocated": "1000000",
            "used": "395870",
            "files": 89
        },
        "home": {
            "allocated": "1590",
            "used": "539",
            "files": 19
        },
        ...,
        "folder-188734": {
            "allocated": "300",
            "used": "79",
            "files": 2
      }
    ]
}
```
</details>


- [x] (3 балла) Добавление возможности поиска файлов по заданным параметрам

<details>
<summary> Описание изменений </summary>

```
POST /files/search
```
Вернуть информацию о загруженных файла в по заданным параметрам. Доступно только авторизованному пользователю.

**Request**
```json
{
    "options": {
        "path": <folder-id-to-search>,
        "extension": <file-extension>,
        "order_by": <field-to-order-search-result>,
        "limit": <max-number-of-results>
    },
    "query": "<any-text||regex>"
}
```

**Response**
```json
{
    "mathes": [
          {
            "id": "113c7ab9-2300-41c7-9519-91ecbc527de1",
            "name": "tree-picture.png",
            "created_ad": "2019-06-19T13:05:21Z",
            "path": "/homework/work-folder/environment/tree-picture.png",
            "size": 1945,
            "is_downloadable": true
          },
        ...
    ]
}
```
</details>

- [ ] (4 балла) Поддержка версионирования изменений файлов

<details>
<summary> Описание изменений </summary>

```
POST /files/revisions
```
Вернуть информацию о изменениях файла по заданным параметрам. Доступно только авторизованному пользователю.

**Request**
```json
{
    "path": <path-to-file>||<file-meta-id>,
    "limit": <max-number-of-results>
}
```

**Response**
```json
{
    "revisions": [
          {
            "id": "b1863132-5db6-44fe-9d34-b944ab06ad81",
            "name": "presentation.pptx",
            "created_ad": "2020-09-11T17:22:05Z",
            "path": "/homework/learning/presentation.pptx",
            "size": 3496,
            "is_downloadable": true,
            "rev_id": "676ffc2a-a9a5-47f6-905e-99e024ca8ac8",
            "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "modified_at": "2020-09-21T05:13:49Z"
          },
        ...
    ]
}
```
</details>

## Требования к решению

1. В качестве СУБД используйте PostgreSQL не ниже 10 версии.
2. Опишите [docker-compose](docker-compose.yml) для разработки и локального тестирования сервисов.
3. Используйте концепции ООП.
4. Предусмотрите обработку исключительных ситуаций.
5. Приведите стиль кода в соответствие pep8, flake8, mypy.
6. Логируйте результаты действий.
7. Покройте написанный код тестами.


## Рекомендации к решению

1. За основу можно взять реализацию проекта 4 спринта.
2. Разрешено использовать готовые библиотеки и пакеты, например, для авторизации. Для поиска можно использовать [сервис openbase](https://openbase.com/categories/python), [PyPi](https://pypi.org/) или на [GitHub](https://github.com/search?).
3. Используйте **in-memory-db** для кэширования данных.
4. Для скачивания файлов можно использовать возможности сервера отдачи статики, для хранения - облачное объектное хранилище (s3).
