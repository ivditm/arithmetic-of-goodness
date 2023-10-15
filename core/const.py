time_column = [
    'Статус контакта за Сентябрь 2022',
    'Статус контакта за Октябрь 2022',
    'Статус контакта за Ноябрь 2022',
    'Статус контакта за Декабрь 2022',
    'Статус контакта за Январь 2023',
    'Статус контакта за Февраль 2023',
    'Статус контакта за Март 2023',
    'Статус контакта за Апрель 2023',
    'Статус контакта за Май 2023',
    'Статус контакта за Июнь 2023',
    'Статус контакта за Июль 2023',
    'Статус контакта за Август 2023'
]
months = {
    'Сентябрь': 9,
    'Октябрь': 10,
    'Ноябрь': 11,
    'Декабрь': 12,
    'Январь': 1,
    'Февраль': 2,
    'Март': 3,
    'Апрель': 4,
    'Май': 5,
    'Июнь': 6,
    'Июль': 7,
    'Август': 8
}
status_types = [
    "Прямой + Через 3-их лиц",
    "Нет статуса",
    "Прямой",
    "Не выходит на контакт",
    "Через 3-х лиц",
    "Не знаю"]
contact_data: dict = {
    "Дата": [],
    "Не знаю": [],
    "Не знаю_всего": [],
    "Прямой + Через 3-их лиц": [],
    "Нет статуса": [],
    "Прямой": [],
    "Не выходит на контакт": [],
    "Через 3-х лиц": [],
    "Прямой + Через 3-их лиц_всего": [],
    "Нет статуса_всего": [],
    "Прямой_всего": [],
    "Не выходит на контакт_всего": [],
    "Через 3-х лиц_всего": []}
columns_contact = [
    "Не знаю",
    "Нет статуса",
    "Не выходит на контакт",
    "Прямой + Через 3-их лиц",
    "Прямой",
    "Через 3-х лиц"
]
columns_contact_total = [
    "Не знаю_всего",
    "Нет статуса_всего",
    "Не выходит на контакт_всего",
    "Прямой + Через 3-их лиц_всего",
    "Прямой_всего",
    "Через 3-х лиц_всего"
]