## Сроки сдачи домов (консолидация по кварталам)



### JSON для LLM (нормализованная структура)

Ниже приведён LLM-дружественный JSON, агрегированный из `quarters/05-sroki-sdachi-domov.md`. Поля `status_code` принимают значения: `DELIVERED`, `PLANNED`, `DELAYED`, `PARTIAL`, `AVAILABLE_FOR_SALE`, `UNKNOWN`. Текстовые даты сохранены в исходном формате в полях `status_note`/`planned_date_text`.

```json
{
  "metadata": {
    "generated_at": "2025-09-12",
    "source_file": "quarters/05-sroki-sdachi-domov.md",
    "notes": "Dates and notes kept as-is from source; see status_code for normalization"
  },
  "quarters": [
    {
      "id": "02",
      "name": "Эмиратс Люкс",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 12,
      "buildings": [
        {"number": "1.1", "name": "Диадема", "address": "ул. Аэродромная 32", "floors": "19-15", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "02.08.2017"},
        {"number": "2.4", "name": "Марина 1", "address": "ул. Братская 2", "floors": "13", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "28.05.2018"},
        {"number": "2.5", "name": "Марина 2", "address": "ул. Братская 4", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "20.07.2018"},
        {"number": "2.6", "name": "Марина 3", "address": "ул. Братская 6", "floors": "19", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "01.09.2018"},
        {"number": "2.7", "name": "Марина 4", "address": "ул. Братская 8", "floors": "22", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "01.09.2018"},
        {"number": "2.8", "name": "Марина 5", "address": "ул. Братская 10", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "17.10.2018"},
        {"number": "2.1", "name": "Эмиратс Волна", "address": "пр-т Мира 1", "floors": "переменная", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "1-7 секции 20.04.20; 8-10 секции 01.09.20"},
        {"number": "2.9", "name": "Жемчужина(№1)", "address": "ул. Братская, 12", "floors": "22", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.2019"},
        {"number": "2.10", "name": "Жемчужина(№2)", "address": "ул. Братская, 14", "floors": "18", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.01.2020"},
        {"number": "2.11", "name": "Жемчужина(№3)", "address": "ул. Братская, 16", "floors": "14", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "20.09.2019"},
        {"number": "2.2", "name": "Пальма 1", "address": "ул. Аэродромная 28", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "02.08.2019"},
        {"number": "2.3", "name": "Пальма 2", "address": "ул. Аэродромная 30", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "04.06.2019"}
      ]
    },
    {
      "id": "07",
      "name": "Средиземноморский",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 11,
      "buildings": [
        {"number": "7.2", "name": "Санторини", "address": "ул. Игоря Лученка, 25", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "25.08.2023"},
        {"number": "7.3", "name": "Родос", "address": "ул. Игоря Лученка, 23", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "12.05.2023"},
        {"number": "7.4", "name": "Лимасол", "address": "ул. Игоря Лученка, 19", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "12.05.2023"},
        {"number": "7.5", "name": "Миконос", "address": "ул. Братская, 9", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "17.04.2024"},
        {"number": "7.6", "name": "Портофино", "address": "ул. Братская, 7", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.24"},
        {"number": "7.9", "name": "Канны", "address": "ул. Братская, д. 1", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.01.22"},
        {"number": "7.10", "name": "Ницца", "address": "ул. Николы Теслы, 24", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.11.2021"},
        {"number": "7.11", "name": "Монако", "address": "ул. Николы Теслы, 26", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "01.12.2021"},
        {"number": "7.1", "name": "Ибица", "address": null, "floors": "10", "status_code": "DELAYED", "status": "Перенос", "status_note": "с 10.07.2025 до 15.12.2025"},
        {"number": "7.12", "name": "Анталья", "address": null, "floors": "14", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ЯНВАРЬ 2026г."},
        {"number": "7.13", "name": "Валлетта", "address": null, "floors": "10", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ЯНВАРЬ 2026г."}
      ]
    },
    {
      "id": "09",
      "name": "Южная Америка",
      "developer": "ООО \"Гранд Атриум Девелопмент\"",
      "buildings_count": 10,
      "buildings": [
        {"number": "9.1", "name": "Лима", "address": "ул. Алферова, 5", "floors": "21", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.2024"},
        {"number": "9.2", "name": "Сантьяго", "address": "ул. Алферова, 3", "floors": "21", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.2024"},
        {"number": "9.4", "name": "Бразилиа", "address": "ул. Николы Теслы, 28", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.05.2024"},
        {"number": "9.5", "name": "Монтевидео", "address": "ул. Николы Теслы, 30", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "29.03.2024"},
        {"number": "9.6", "name": "Сан-Паулу", "address": "ул. Щемелева, 10", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "29.03.2024"},
        {"number": "9.7", "name": "Мехико-Сити", "address": "ул. Щемелева, 14", "floors": "19", "status_code": "PARTIAL", "status": "Частично", "status_note": "1 секция готова; ожидаем ввода 2 и 3 секции"},
        {"number": "9.8", "name": "Панама-Сити", "address": "ул. Щемелева, 16", "floors": "19", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.2024"},
        {"number": "9.9", "name": "Буэнос-Айрес", "address": "ул. Игоря Лученка, 31", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.10.2023"},
        {"number": "9.10", "name": "Гавана", "address": "ул. Игоря Лученка, 29", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.10.2023"},
        {"number": "9.11", "name": "Каракас", "address": "ул. Игоря Лученка, 27", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.10.2023"}
      ]
    },
    {
      "id": "10",
      "name": "Тропические острова",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 10,
      "buildings": [
        {"number": "10.1", "name": "Гавайи", "address": "ул. Братская, 17", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.06.2023"},
        {"number": "10.2", "name": "Бора-Бора", "address": "ул. Братская, 15", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.06.2023"},
        {"number": "10.3", "name": "Таити", "address": "ул. Братская, 13", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "19.10.2023"},
        {"number": "10.4", "name": "Багамы", "address": "ул. Братская, 11", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.10.2023"},
        {"number": "10.5", "name": "Бали", "address": "ул. Лученка, 24", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.22"},
        {"number": "10.6", "name": "Фиджи", "address": "ул. Алферова, 10", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "29.09.2023"},
        {"number": "10.7", "name": "Барбадос", "address": "ул. Алферова, 12", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.12.2023"},
        {"number": "10.8", "name": "Аруба", "address": "ул. Ж. Алфёрова, 14", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.06.2023"},
        {"number": "10.9", "name": "Мальдивы", "address": "ул. Алферова, 16", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.06.2023"},
        {"number": "10.10", "name": "Мадагаскар", "address": "ул. Лученка, 26", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.22"}
      ]
    },
    {
      "id": "11",
      "name": "Австралия и Океания (бизнес апартаменты)",
      "developer": "ООО \"Дубай Инвестмент\"",
      "buildings_count": 4,
      "buildings": [
        {"number": "11.3", "name": "Атлантик", "address": null, "floors": "15", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ДЕКАБРЬ 2027г."},
        {"number": "11.4", "name": "Пацифик", "address": null, "floors": "15", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ДЕКАБРЬ 2027г."},
        {"number": "11.5", "name": "Адриатик", "address": null, "floors": "15", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "АВГУСТ 2027г."},
        {"number": "11.6", "name": "Карибиан", "address": null, "floors": "15", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "АВГУСТ 2026г."}
      ]
    },
    {
      "id": "12",
      "name": "Западная Европа",
      "developer": "ООО \"Дубай Инвестмент\"",
      "buildings_count": 10,
      "buildings": [
        {"number": "12.4", "name": "Амстердам", "address": "ул. Л.Щемелева, 18", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "18.11.2024"},
        {"number": "12.5", "name": "Берлин", "address": "ул. Лученка, 32", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.12.2023"},
        {"number": "12.6", "name": "Мюнхен", "address": "ул. Лученка, 28", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "04.03.2024"},
        {"number": "12.7", "name": "Венеция", "address": "ул. Лученка, 30", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "23.12.2024"},
        {"number": "12.8", "name": "Париж", "address": "ул. М. Савицкого, 35", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.2024"},
        {"number": "12.9", "name": "Марсель", "address": "ул. М. Савицкого, 37", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "21.02.2025"},
        {"number": "12.11", "name": "Манчестер", "address": "ул. Ж. Алферова, 7", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.12.2023"},
        {"number": "12.12", "name": "Лиссабон", "address": "ул. Ж. Алферова, 9", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.12.2023"},
        {"number": "12.13", "name": "Брюссель", "address": "ул. Ж. Алферова, 11", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "21.08.2023"},
        {"number": "12.14", "name": "Женева", "address": "ул. Ж. Алферова, 13", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.07.2023"}
      ]
    },
    {
      "id": "16",
      "name": "Родная страна",
      "developer": "ООО \"Дубай Инвестмент\"",
      "buildings_count": 2,
      "buildings": [
        {"number": "16.38", "name": "Несвижский замок", "address": null, "floors": "16", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "СЕНТЯБРЬ 2026г."},
        {"number": "16.39", "name": "Мирский замок", "address": null, "floors": "16", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "НОЯБРЬ 2026г."}
      ]
    },
    {
      "id": "18",
      "name": "Квартал Чемпионов",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 8,
      "buildings": [
        {"number": "18.1", "name": "Пекин", "address": "ул. Белградская, 1", "floors": "23-25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "частями 13.10.21 и 12.03.22"},
        {"number": "18.2", "name": "Солт Лейк Сити", "address": "ул. Аэродромная, д.26", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "08.11.2022"},
        {"number": "18.3", "name": "Лиллехаммер", "address": "ул. Аэродромная, д.26А", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "16.09.22"},
        {"number": "18.4", "name": "Сидней люкс", "address": "пр-т Мира д. 2", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "25.09.2020"},
        {"number": "18.5", "name": "Атланта", "address": "пр. Мира, д.4", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "28.02.2023"},
        {"number": "18.6", "name": "Сочи", "address": "пр-т Мира, 6", "floors": "10 и 25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "25.09.2020"},
        {"number": "18.7", "name": "Рио-де-Жанейро", "address": "ул. Белградская, 5", "floors": "23", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "05.03.2020"},
        {"number": "18.8", "name": "Турин", "address": "ул. Николы Теслы, д.29", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "12.08.21"}
      ]
    },
    {
      "id": "19",
      "name": "Южная Европа",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 8,
      "buildings": [
        {"number": "19.1", "name": "Стамбул", "address": "ул. Аэродромная, д. 18", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "10.06.2021"},
        {"number": "19.4", "name": "Флоренция", "address": "ул. Аэродромная, 20", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "06.05.2022"},
        {"number": "19.6", "name": "Котор", "address": "ул. Аэродромная, 22", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "19.12.22"},
        {"number": "19.7", "name": "Дубровник", "address": "ул. Аэродромная, д.24", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.10.2022"},
        {"number": "19.8", "name": "Салоники", "address": "ул. Белградская, д.2", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "25.11.2022"},
        {"number": "19.9", "name": "Барселона", "address": "Теслы, 23", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "26.09.22"},
        {"number": "19.10", "name": "Валенсия", "address": "Белградская, 4", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.22"},
        {"number": "19.11", "name": "Афины", "address": "ул. Н.Теслы, 21", "floors": "6-8", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "19.06.2020"}
      ]
    },
    {
      "id": "20",
      "name": "Мировых танцев",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 11,
      "buildings": [
        {"number": "20.1", "name": "Танго", "address": "ул. Брилевская, д. 31", "floors": "16, 17, 19", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "20.11.2020"},
        {"number": "20.2", "name": "Самба", "address": "ул. Брилевская, 29", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "03.05.2024"},
        {"number": "20.3", "name": "Румба", "address": "ул. Брилевская, 27", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "08.05.2024"},
        {"number": "20.4", "name": "Ча-ча-ча", "address": "ул. Брилевская, 25", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "17.05.2024"},
        {"number": "20.5", "name": "Фламенко", "address": "ул. Аэродромная, 16", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "06.01.2023"},
        {"number": "20.6", "name": "Сальса", "address": "Теслы, 15", "floors": "15", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "26.09.22"},
        {"number": "20.7", "name": "Мазурка", "address": "ул. Николы Теслы, д. 19", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "27.05.2022"},
        {"number": "20.8", "name": "Чарльстон", "address": "ул. Николы Теслы, д.11", "floors": "15", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "11.12.2020"},
        {"number": "20.9", "name": "Полька", "address": "ул. Николы Теслы, д. 17", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "27.05.2022"},
        {"number": "20.10", "name": "Твист", "address": "ул. Николы Теслы, д. 7", "floors": "15", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "12.11.2020"},
        {"number": "20.11", "name": "Вальс", "address": "ул. Н.Теслы, 1", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "28.10.2020"}
      ]
    },
    {
      "id": "21",
      "name": "Западный",
      "developer": "ООО \"Дубай Инвестмент\"",
      "buildings_count": 1,
      "buildings": [
        {"number": "21.1", "name": "Континенталь", "address": null, "floors": "8", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ДЕКАБРЬ 2027г."}
      ]
    },
    {
      "id": "22",
      "name": "Центральная Европа",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 6,
      "buildings": [
        {"number": "22.2", "name": "Варшава", "address": "ул. Игоря Лученка, 13", "floors": "23", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.04.2021"},
        {"number": "22.3", "name": "Прага", "address": "ул. Игоря Лученка, 11", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ"},
        {"number": "22.4", "name": "Белград", "address": "ул. Теслы, 20", "floors": "15", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.12.2023"},
        {"number": "22.5", "name": "Вена", "address": "ул. Теслы, 18", "floors": "19", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "07.12.21"},
        {"number": "22.6", "name": "Будапешт", "address": "Николы Теслы, д. 16", "floors": "22", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "21.07.22"},
        {"number": "22.7", "name": "София", "address": null, "floors": "12", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ЯНВАРЬ 2026г."}
      ]
    },
    {
      "id": "23",
      "name": "Евразия",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 8,
      "buildings": [
        {"number": "23.1", "name": "Санкт-Петербург", "address": "ул. Игоря Лученка, д.1", "floors": "19", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "14.06.2022"},
        {"number": "23.2", "name": "Тбилиси", "address": "ул. Теслы, 10", "floors": "19", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "11.04.2022"},
        {"number": "23.3", "name": "Ереван", "address": "ул. Н.Теслы, 14", "floors": "19", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "29.04.2022"},
        {"number": "23.4", "name": "Баку", "address": "Белградская, 6", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "11.02.22"},
        {"number": "23.5", "name": "Нур-Султан", "address": "Белградская, 8", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "03.06.2022"},
        {"number": "23.6", "name": "Екатеринбург", "address": "ул. Игоря Лученка, 9", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "15.11.21"},
        {"number": "23.7", "name": "Калининград", "address": "ул Игоря Лученка 7", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "08.10.21"},
        {"number": "23.8", "name": "Москва", "address": "ул. Игоря Лученка, 5", "floors": "21", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "29.01.2021"}
      ]
    },
    {
      "id": "25",
      "name": "Азия",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 11,
      "buildings": [
        {"number": "25.1", "name": "Сеул", "address": "ул. М. Савицкого, 2", "floors": "15", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.06.2023(1 п.-3с.), 31.08.23 (2п. и 1п.)"},
        {"number": "25.2", "name": "Токио", "address": "ул. Михаила Савицкого д. 4", "floors": "16,17,18", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "18.06.21"},
        {"number": "25.3", "name": "Манила", "address": "Савицкого, 8", "floors": "15", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "26.09.22"},
        {"number": "25.4", "name": "Гонконг", "address": "ул. Михаила Савицкого, д. 10", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "23.12.2020"},
        {"number": "25.5", "name": "Куала-Лумпур", "address": "ул. М. Савицкого 12", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.06.2023"},
        {"number": "25.6", "name": "Джакарта", "address": "ул. Лейтенанта Кижеватова, 1Б", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ"},
        {"number": "25.7", "name": "Нью-Дели", "address": "ул. Лейтенанта Кижеватова, д. 1А", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "24.11.2020"},
        {"number": "25.8", "name": "Сингапур", "address": "ул. Лейтенанта Кижеватова д.1", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "25.03.2022"},
        {"number": "25.9", "name": "Мумбаи", "address": "ул. Брилевская д.37", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "05.08.21"},
        {"number": "25.10", "name": "Бангкок", "address": "ул. Брилевская д. 35", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "05.08.21"},
        {"number": "25.11", "name": "Киото", "address": "ул. Брилевская, д.33", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "05.08.21"}
      ]
    },
    {
      "id": "26",
      "name": "Африка",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 6,
      "buildings": [
        {"number": "26.1", "name": "Каир", "address": "ул. Михаила Савицкого, д.1", "floors": "16,17", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "22.09.21"},
        {"number": "26.2", "name": "Кейптаун", "address": "ул. Николы Теслы д.6", "floors": "18", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "17.11.2020"},
        {"number": "26.3", "name": "Касабланка", "address": "ул. Николы Теслы, д. 8", "floors": "19", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "22.01.2021"},
        {"number": "26.4", "name": "Марракеш", "address": "ул. Леонида Левина, д. 2", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "28.01.22"},
        {"number": "26.5", "name": "Найроби", "address": "ул. Николы Теслы, 4", "floors": "18", "status_code": "AVAILABLE_FOR_SALE", "status": "Готовый в продаже"},
        {"number": "26.6", "name": "Александрия", "address": "ул. Михаила Савицкого 3", "floors": "24", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.04.2021"}
      ]
    },
    {
      "id": "27",
      "name": "Happy Planet",
      "developer": "ООО \"Луксудо\"",
      "buildings_count": 5,
      "buildings": [
        {"number": "27.1", "name": "Golden Gate Park", "address": "ул. Л.Левина, 7", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "16.11.2023"},
        {"number": "27.2", "name": "Central Park", "address": "ул. Л.Левина, 1", "floors": "21", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "16.11.2023"},
        {"number": "27.3", "name": "Hyde Park", "address": "ул. Лученка, 2", "floors": "21", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "16.11.2023"},
        {"number": "27.4", "name": "Yoyougi Park", "address": "ул. Лученка, 8", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.12.23"},
        {"number": "27.5", "name": "Калемегдан", "address": "ул. Леонида Левина, 3", "floors": "8", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "элитный дом с антресолями"}
      ]
    },
    {
      "id": "28",
      "name": "Happy Planet (дополнительные)",
      "developer": "ООО \"Луксудо\"",
      "buildings_count": 13,
      "buildings": [
        {"number": "28.1", "name": "Парк Гёреме", "address": null, "floors": "13", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ЯНВАРЬ 2026г."},
        {"number": "28.5", "name": "Люксембургский сад", "address": "ул. И. Лученка, д. 16", "floors": "13", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.24"},
        {"number": "28.6", "name": "Парк Гуэль", "address": "ул. И. Лученка, д. 16", "floors": "6", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.12.24"},
        {"number": "28.7", "name": "Риджентс-парк", "address": "ул. И. Лученка, д. 16", "floors": "13", "status_code": "DELAYED", "status": "Перенос", "status_note": "с 31.03.2025 до 15.05.2025"},
        {"number": "29.1", "name": "Копенгаген", "address": "ул. Белградская 11", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "24.12.2021"},
        {"number": "29.2", "name": "Стокгольм", "address": "ул. Белградская, 9", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "29.12.2021"},
        {"number": "29.3", "name": "Хельсинки", "address": "пр-т Мира, д.12", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "02.11.2022"},
        {"number": "29.4", "name": "Глазго", "address": "пр. Мира, 14", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "22.04.22"},
        {"number": "29.5", "name": "Осло", "address": "пр. Мира, 16", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "08.11.21"},
        {"number": "29.6", "name": "Вильнюс", "address": "проспект Мира, д.18", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "02.11.21"},
        {"number": "29.7", "name": "Таллин", "address": "пр. Мира, 20", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "08.11.21"},
        {"number": "28.2", "name": "Беллунские Доломиты", "address": null, "floors": "13", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ЯНВАРЬ 2026г."},
        {"number": "28.3", "name": "Дурмитор", "address": null, "floors": "13", "status_code": "PLANNED", "status": "Строящийся", "planned_date_text": "ЯНВАРЬ 2026г."}
      ]
    },
    {
      "id": "29",
      "name": "Северная Европа",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 7,
      "buildings": [
        {"number": "29.1", "name": "Копенгаген", "address": "ул. Белградская 11", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "24.12.2021"},
        {"number": "29.2", "name": "Стокгольм", "address": "ул. Белградская, 9", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "29.12.2021"},
        {"number": "29.3", "name": "Хельсинки", "address": "пр-т Мира, д.12", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "02.11.2022"},
        {"number": "29.4", "name": "Глазго", "address": "пр. Мира, 14", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "22.04.22"},
        {"number": "29.5", "name": "Осло", "address": "пр. Мира, 16", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "08.11.21"},
        {"number": "29.6", "name": "Вильнюс", "address": "проспект Мира, д.18", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "02.11.21"},
        {"number": "29.7", "name": "Таллин", "address": "пр. Мира, 20", "floors": "10", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "08.11.21"}
      ]
    },
    {
      "id": "30",
      "name": "Северная Америка",
      "developer": "ИООО \"Дана Астра\"",
      "buildings_count": 12,
      "buildings": [
        {"number": "30.1", "name": "Лос-Анжелес", "address": "ул. Л.Левина, д.13", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "31.05.2020"},
        {"number": "30.2", "name": "Сан-Франциско", "address": "ул. Л.Левина, д.11", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "15.04.2021"},
        {"number": "30.3", "name": "Лас-Вегас", "address": "ул. Леонида Левина, д.9", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.09.2021"},
        {"number": "30.4", "name": "Чикаго", "address": "ул. Савицкого, 20", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "18.05.22"},
        {"number": "30.5", "name": "Бостон", "address": "ул. Савицкого, 22", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "14.10.2022"},
        {"number": "30.6", "name": "Торонто", "address": "ул. Белградская, 14", "floors": "16", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "30.11.21"},
        {"number": "30.7", "name": "Нью-Йорк", "address": "ул. Белградская, д.16", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "07.09.21"},
        {"number": "30.8", "name": "Майами", "address": "ул. Кижеватова, 3Д", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "25.02.22"},
        {"number": "30.9", "name": "Нью Орлеан", "address": "ул. Лейтенанта Кижеватова д.3Г", "floors": "25", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "09.03.2021"},
        {"number": "30.10", "name": "Монреаль", "address": "ул. Лейтенанта Кижеватова д. 3В", "floors": "20", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "04.12.2020"},
        {"number": "30.11", "name": "Ванкувер", "address": "ул. Лейтенанта Кижеватова д.3Б", "floors": "20", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "04.12.2020"},
        {"number": "30.12", "name": "Квебек", "address": "ул. Лейтенанта Кижеватова д.3А", "floors": "20", "status_code": "DELIVERED", "status": "СДАН ГОРОДУ", "status_note": "04.12.2020"}
      ]
    }
  ]
}
```

