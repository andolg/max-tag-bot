# Уже всё совсем не так

## Общее описание

Класс `ChatUI` из `bot.ui.base` предоставляет базовый класс для интерфейса. Реализация интерфейса нашего бота находится в `bot.ui.tag_bot.TagBotUI`.
Тип события обрабатывается в `bot.main`, там же вызывается соответствующая функция извлечения маршрута и аргументов, которые передаются в [`ChatUI.respond()`](#respondself-event-updateunion-route_name-str-args-dict---dict).

---

## Поля класса `ChatUI`

| Поле | Тип | Описание |
|------|-----|-----------|
| `route_templates` | `dict[str, dict]` | Словарь шаблонов маршрутов. [Подробнее](#формат-route_templates) |
| `bgrid_h` | `int` | Максимальное количество строк при генерации [сетки кнопок](#build_button_gridself-contents-listtuplestr-str---listlistcallbackbutton). Default: 5 |
| `bgrid_w` | `int` | Количество кнопок в одной строке сетки. Default: 3 |
| `empty_pl` | `str` | Payload для "пустых" кнопок-заполнителей. Default: `'/empty'` |

---

## Методы класса `ChatUI`

### `respond(self, event: UpdateUnion, route_name: str, args: dict) -> dict`
Формирует ответное сообщение в виде словаря для отправки через Max API.

#### Аргументы:
- `event`: объект события (`MessageCreated`, `MessageCallback`, `BotStarted` и т.д.);
- `route_name`: строка с именем маршрута (например, `"/start"` или `"/help"`);
- `args`: словарь аргументов маршрута, полученных из payload или текста команды. Например: `{'arg1': ['val1', 'val2'], 'arg2': ['val1']}` (в значениях массивы строк).

#### Возвращает:
Словарь вида:
```python
{
    "text": str,
    "attachments": [ButtonsPayload, ...]
}
```

#### Логика работы:
1. Проверяет наличие шаблона маршрута в `route_templates`.
2. Если в шаблоне маршрута задан `handler`, вызывает соответствующий метод.
3. Формирует текст:
   - либо из поля `"text"`,
   - либо вызывает функцию, указанную в `"ftext"`.
4. Генерирует вложения (`attachments`). Пока только кнопки.
5. Возвращает готовый словарь для отправки пользователю.

---

### `build_button_grid(self, contents: list[tuple[str, str]]) -> list[list[CallbackButton]]`
Создаёт сетку кнопок.

#### Аргументы:
- `contents`: список кортежей вида `(button_text, payload)`.

#### Возвращает:
Список строк кнопок `list[list[CallbackButton]]`.

#### Поведение:
- Ограничивает общее количество кнопок размерами сетки `bgrid_h * bgrid_w`.
- Если последняя строка не полная — заполняет её кнопками-заглушками (`"..."`).
- Кнопки-заглушки получают `Intent.NEGATIVE`, остальные — `Intent.DEFAULT`.

#### Пример:
```python
ui.build_button_grid([
    ("Первая", "/route1"),
    ("Вторая", "/route2"),
    ("Третья", "/route3")
])
```

---

## Типы методов, используемых в `ChatUI`

`ChatUI` предполагает использование следующих видов методов, которые наследники должны реализовывать:

### 1. **Handler-методы**
Методы для выполнения логики при переходе по маршруту без создания визуальных элементов.

**Сигнатура:**
```python
def some_handler(self, event: UpdateUnion, args: dict) -> None
```

Используется в `route_templates` как:
```python
'handler': 'some_handler'
```

---

### 2. **Методы для форматирования текста (`ftext`)**
Методы, возвращающие динамически сгенерированный текст.

**Сигнатура:**
```python
def some_text_function(self, event: UpdateUnion, args: dict) -> str
```

Используется в `route_templates` как:
```python
'ftext': 'some_text_function'
```

---

### 3. **Методы кнопок**
Методы, возвращающие одну кнопку или двумерный список (сетку) кнопок.

**Сигнатура:**
```python
def button_method(self, event: UpdateUnion, args: dict) -> CallbackButton
```
или
```python
def button_grid_method(self, event: UpdateUnion, args: dict) -> list[list[CallbackButton]]
```

Используется в `route_templates` в секции `"buttons"`.


### 4. **Методы изображений**
TODO

---

## Функции для извлечения payload

### `extract_message_created_payload(event: MessageCreated) -> tuple[str, dict]`

Извлекает маршрут и аргументы из события MessageCreated. Обрабатывает текстовые команды, вводимые пользователем.

#### Поведение:
- Делит текст сообщения по пробелам.
- Первый токен — это `route_name`.
- Остальные токены становятся аргументами с числовыми ключами.

#### Пример:
Событие с текстом:
```
/tags tag1 tag2
```
Вернёт:
```python
("/tags", {0: ["tag1"], 1: ["tag2"]})
```

---

### `extract_message_callback_payload(event: MessageCallback) -> tuple[str, dict]`

Извлекает маршрут и аргументы из события MessageCallback, вызываемого при нажатии кнопок.

#### Поведение:
- Парсит payload как URL.
- Путь (`path`) используется как `route_name`.
- Параметры запроса (`query`) превращаются в словарь аргументов.

#### Пример:
Событие с payload:
```
/tags?chat_id=123&tag=tag1
```
Вернёт:
```python
("/tags", {"chat_id": ["123"], "tag": ["tag1"]})
```

---

## Формат `route_templates`

`route_templates` — это словарь, где каждый ключ — имя маршрута (`str`),  
а значение — словарь с необязательными полями.

### Пример:
```python
route_templates = {
    '/start': {
        'handler': 'start_handler',
        'text': 'Добро пожаловать!',
        'buttons': [
            ['help_button', 'tags_button'],
            ['groups_button']
        ]
    },
    '/tags': {
        'ftext': 'tags_text',
        'buttons': [
            'tag_buttons',       # Сетка кнопок
            ['tags_back_button'] # Обычный ряд кнопок
        ]
    }
}
```

### Ключи шаблона маршрута:

| Ключ | Тип | Описание |
|------|-----|----------|
| `text` | `str` | Статический текст сообщения. |
| `ftext` | `str` | Имя метода, который динамически формирует текст. |
| `handler` | `str` | Имя метода, выполняющего обработку события. |
| `buttons` | `list` | Ссылки на методы, генерирующие кнопки. Метод  |

---

### Пример маршрута:

```python
'/tags': {
    'ftext': 'tags_text',
    'buttons': [
        'tag_buttons',      
        ['tags_back_button']
    ]
}
```

---
