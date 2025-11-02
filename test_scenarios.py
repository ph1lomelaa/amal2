from PIL import Image, ImageDraw, ImageFont
import os
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import tempfile
# === КОНФИГУРАЦИЯ ===

Image.MAX_IMAGE_PIXELS = None

FORUM_TTF = os.path.expanduser("/Users/muslimakosmagambetova/Library/Fonts/Forum-Regular.ttf")

# === МЕНЕДЖЕРЫ (ключ -> файлы с именем и телефоном) ===
MANAGER_KEY = "khadidzha"   # поменяешь при вызове

MANAGER_ASSETS = {
    "aidana":     {"name": "res/aidana_name.png",     "phone": "phones/aidana_phone-2.png"},
    "elvira":     {"name": "res/elvira_name.png",     "phone": "phones/elvira_phone-2.png"},
    "khadidzha":  {"name": "res/khadidzha_name.png",  "phone": "phones/khadidzha_phone-2.png"},
    "marina":     {"name": "res/marina_name.png",     "phone": "phones/marina_phone-2.png"},
    "minira":     {"name": "res/minira_name.png",     "phone": "phones/minira_phone-2.png"},
    "oxana":      {"name": "res/oxana_name.png",      "phone": "phones/oxana_phone-2.png"},
}

LINKS = {
    "whatsapp": "https://wa.me/77479711111?text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5%2C%20%D1%85%D0%BE%D1%87%D1%83%20%D1%83%D0%B7%D0%BD%D0%B0%D1%82%D1%8C%20%D0%BF%D0%BE%20%D0%B2%D0%B0%D1%83%D1%87%D0%B5%D1%80%D1%83",
    "instagram": "https://instagram.com/amalexperiences"
}

LINK_ZONES = {
    1: {
        "whatsapp":  (1135, 3187, 1208, 3260),  # <-- подставь твои точные
        "instagram": (1255, 3187, 1328, 3260),
    },
    2: {
        "whatsapp":  (1124, 3216, 1197, 3289),
        "instagram": (1244, 3216, 1317, 3289),
    },
    3: {
        "whatsapp":  (1124, 3216, 1197, 3289),
        "instagram": (1244, 3216, 1317, 3289),
    },
    4: {
        "whatsapp":  (1124, 3216, 1197, 3289),
        "instagram": (1244, 3216, 1317, 3289),
    },
    5: {
        "whatsapp":  (1124, 3216, 1197, 3289),
        "instagram": (1244, 3216, 1317, 3289),
    },
    6: {
        "whatsapp":  (1160, 3322, 1233, 3395),
        "instagram": (1281, 3322, 1354, 3395),
    },
    7: {
        "whatsapp":  (1160, 3322, 1233, 3395),
        "instagram": (1281, 3322, 1354, 3395),
    },
    8: {
        "whatsapp":  (1038, 3381, 1110, 3453),
        "instagram": (1145, 3381, 1217, 3453),
    },
    9: {
        "whatsapp":  (1038, 3381, 1110, 3453),
        "instagram": (1145, 3381, 1217, 3453),
    },
    10: {
        "whatsapp":  (1038, 3381, 1110, 3453),
        "instagram": (1145, 3381, 1217, 3453),
    },
    # Можно ещё добавить "default" как запасной вариант
    "default": {
        "whatsapp":  (1830, 3120, 1905, 3195),
        "instagram": (1915, 3120, 1990, 3195),
    }
}


# === СЦЕНАРИИ И ФОНЫ ===
SCENARIOS = {
    1: {
        "name": "1 страна, базовые данные",
        "bg_path": "scen/scen1.png",
        "description": "Только основные данные отеля и клиенты"
    },
    2: {
        "name": "1 страна + гид",
        "bg_path": "scen/scen2.png",
        "description": "Основные данные + информация о гиде"
    },
    3: {
        "name": "1 страна + сервис",
        "bg_path": "scen/scen3.png",
        "description": "Основные данные + дополнительные услуги"
    },
    4: {
        "name": "1 страна + гид + сервис + экскурсии",
        "bg_path": "scen/scen4.png",
        "description": "Полный пакет с гидом, сервисом и экскурсиями"
    },
    5: {
        "name": "1 страна + гид + сервис + трансфер + экскурсии",
        "bg_path": "scen/scen5.png",
        "description": "Расширенный пакет с 4 сервисными строками"
    },
    6: {
        "name": "2 страны, комбинированный тур",
        "bg_path": "scen/scen6.png",
        "description": "Тур по двум странам с разными отелями и датами"
    },
    7: {
        "name": "2 страны + 1 сервисная строка",
        "bg_path": "scen/scen7.png",
        "description": "Комбо-тур (2 страны) + одна сервисная строка"
    },
    8: {
        "name": "2 страны + 2 сервисные строки",
        "bg_path": "scen/scen8.png",
        "description": "Комбо-тур (2 страны) + две сервисные строки"
    },
    9: {
        "name": "2 страны + 3 сервисные строки",
        "bg_path": "scen/scen9.png",
        "description": "Комбо-тур (2 страны) + три сервисные строки"
    },
    10: {
        "name": "2 страны + 4 сервисные строки",
        "bg_path": "scen/scen10.png",
        "description": "Комбо-тур (2 страны) + 4 сервисные строки"
    },
}

# === КООРДИНАТЫ ===
COORDS_SCENARIO_1 = {
    "clients": (1480, 738, 2303, 995),
    "country": (1027, 1385, 1735, 1484),
    "city": (1027, 1504, 1328, 1603),
    "hotel": (1027, 1622, 1821, 1721),
    "dates": (1027, 1741, 1370, 1840),
    "stay": (1027, 1860, 1424, 1952),
    "roomcat": (1027, 1970, 1542, 2068),
    "meals": (1027, 2088, 1462, 2187),

    "manager_name": (998, 2680, 1913, 2840),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_2 = {
    "clients": (1480, 738, 2303, 995),
    "country": (1013, 1214, 1717, 1313),
    "city": (1013, 1332, 1318, 1431),
    "hotel": (1013, 1449, 1808, 1548),
    "dates": (1013, 1567, 1357, 1666),
    "stay": (1013, 1686, 1410, 1776),
    "roomcat": (1013, 1795, 1529, 1895),
    "meals": (1013, 1914, 1449, 2013),
    "service_label": (222, 2222, 863, 2309),
    "service_value": (985, 2227, 2008, 2314),

    "manager_name": (998, 2680, 1913, 2840),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_3 = {
    "clients": (1480, 738, 2303, 995),
    "country": (1025, 1283, 1733, 1382),
    "city": (1025, 1401, 1326, 1500),
    "hotel": (1025, 1520, 1819, 1619),
    "dates": (1025, 1639, 1368, 1738),
    "stay": (1025, 1758, 1422, 1857),
    "roomcat": (1025, 1867, 1541, 1966),
    "meals": (1025, 1986, 1461, 2085),
    "service_label": (208, 2280, 331, 2367),
    "service_value": (413, 2280, 920, 2367),
    "service_label2": (208, 2396, 838, 2483),
    "service_value2": (929, 2396, 1935, 2483),

    "manager_name": (998, 2710, 1913, 2870),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_4 = {
    # Клиенты (многострочный список имён)
    "clients": (1480, 738, 2303, 995),

    # Таблица слева (значения во второй колонке)
    "country": (1025, 1283, 1733, 1382),
    "city": (1025, 1401, 1326, 1500),
    "hotel": (1025, 1520, 1819, 1619),
    "dates": (1025, 1639, 1368, 1738),
    "stay": (1025, 1758, 1422, 1857),
    "roomcat": (1025, 1867, 1541, 1966),
    "meals": (1025, 1986, 1461, 2085),

    # Три сервисные строки
    "service_label": (212, 2296, 373, 2383),    # Первая строка - label (Гид)
    "service_value": (426, 2296, 1434, 2383),   # Первая строка - value (+7 775 846 73 47)

    "service_label2": (212, 2407, 548, 2494),   # Вторая строка - label (Трансфер)
    "service_value2": (623, 2407, 1156, 2506),  # Вторая строка - value (+7 775 846 73 47)

    "service_label3": (212, 2519, 612, 2607),   # Третья строка - label (Экскурсии)
    "service_value3": (623, 2523, 1141, 2610),

    "manager_name": (998, 2710, 1913, 2870),
    "manager_phone": (1936, 2855, 2283, 2946)# Третья строка - value (+7 775 846 73 47)
}

COORDS_SCENARIO_5 = {
    # Клиенты (многострочный список имён)
    "clients": (1480, 738, 2303, 995),

    # Таблица слева (значения во второй колонке)
    "country": (1025, 1283, 1733, 1382),
    "city": (1025, 1401, 1326, 1500),
    "hotel": (1025, 1520, 1819, 1619),
    "dates": (1025, 1639, 1368, 1738),
    "stay": (1025, 1758, 1422, 1857),
    "roomcat": (1025, 1867, 1541, 1966),
    "meals": (1025, 1986, 1461, 2085),

    # Четыре сервисные строки
    "service_label": (216, 2219, 376, 2306),    # Первая строка - label (Гид)
    "service_value": (406, 2218, 1412, 2306),   # Первая строка - value (+7 775 846 73 47)

    "service_label2": (216, 2324, 464, 2411),   # Вторая строка - label (Трансфер)
    "service_value2": (523, 2328, 1529, 2415),  # Вторая строка - value (+7 775 846 73 47)

    "service_label3": (216, 2423, 541, 2510),   # Третья строка - label (Экскурсии)
    "service_value3": (581, 2437, 1114, 2524),  # Третья строка - value

    "service_label4": (216, 2535, 616, 2622),   # Четвертая строка - label
    "service_value4": (611, 2539, 1129, 2616),

    "manager_name": (998, 2710, 1913, 2870),
    "manager_phone": (1936, 2855, 2283, 2946)# Четвертая строка - value
}

COORDS_SCENARIO_6 = {
    # Клиенты (многострочный список имён)
    "clients": (1501, 558, 2336, 787),

    # ПЕРВАЯ СТРАНА (верхняя таблица)
    "country_1": (959, 1010, 1590, 1095),
    "city_1": (959, 1116, 1227, 1201),
    "hotel_1": (959, 1221, 1667, 1309),
    "dates_1": (959, 1327, 1265, 1415),
    "stay_1": (959, 1433, 1313, 1513),
    "roomcat_1": (959, 1530, 1419, 1615),
    "meals_1": (959, 1636, 1347, 1724),

    # ВТОРАЯ СТРАНА (нижняя таблица)
    "country_2": (959, 1855, 1591, 1943),
    "city_2": (959, 1961, 1227, 2050),
    "hotel_2": (959, 2067, 1667, 2155),
    "dates_2": (959, 2173, 1265, 2261),
    "stay_2": (959, 2279, 1312, 2359),
    "roomcat_2": (959, 2376, 1419, 2464),
    "meals_2": (959, 2482, 1347, 2570),

    "manager_name": (1022, 2812, 1903, 2965),    # имя менеджера
    "manager_phone": (1966, 2988, 2315, 3081),
}

COORDS_SCENARIO_7 = {
    # Клиенты (многострочный список имён)
    "clients": (1501, 470, 2336, 700),

    # ПЕРВАЯ СТРАНА (верхняя таблица)
    "country_1": (959, 861, 1591, 949),
    "city_1": (959, 966, 1228, 1055),
    "hotel_1": (959, 1073, 1668, 1161),
    "dates_1": (959, 1179, 1266, 1276),
    "stay_1": (959, 1284, 1314, 1364),
    "roomcat_1": (959, 1382, 1419, 1470),
    "meals_1": (959, 1488, 1347, 1575),

    # ВТОРАЯ СТРАНА (нижняя таблица)
    "country_2": (959, 1643, 1591, 1731),
    "city_2": (959, 1749, 1227, 1837),
    "hotel_2": (959, 1854, 1668, 1942),
    "dates_2": (959, 1960, 1265, 2048),
    "stay_2": (959, 2066, 1312, 2146),
    "roomcat_2": (959, 2164, 1419, 2252),
    "meals_2": (959, 2270, 1347, 2358),

    "service_label": (271, 2524, 917, 2611),    # Первая строка - label (Гид)
    "service_value": (1153, 2524, 1673, 2611),

    "manager_name": (1022, 2812, 1903, 2965),    # имя менеджера
    "manager_phone": (1966, 2988, 2315, 3081),# Первая строка - value (+7 775 846 73 47)
}

COORDS_SCENARIO_8 = {
    # Клиенты (многострочный список имён)
    "clients": (1481, 421, 2302, 646),

    # ПЕРВАЯ СТРАНА (верхняя таблица)
    "country_1": (959, 794, 1579, 881),
    "city_1": (959, 898, 1223, 985),
    "hotel_1": (959, 1002, 1654, 1089),
    "dates_1": (959, 1106, 1260, 1193),
    "stay_1": (959, 1210, 1306, 1287),
    "roomcat_1": (959, 1305, 1405, 1392),
    "meals_1": (959, 1410, 1335, 1496),

    # ВТОРАЯ СТРАНА (нижняя таблица)
    "country_2": (959, 1601, 1579, 1688),
    "city_2": (959, 1705, 1223, 1792),
    "hotel_2": (959, 1809, 1654, 1896),
    "dates_2": (959, 1912, 1259, 2000),
    "stay_2": (959, 2017, 1307, 2095),
    "roomcat_2": (959, 2112, 1410, 2199),
    "meals_2": (959, 2216, 1340, 2303),

    "service_label": (213, 2467, 557, 2555),    # Первая строка - label (Гид)
    "service_value": (623, 2468, 1127, 2555),   # Первая строка - value (+7 775 846 73 47)

    "service_label2": (213, 2567, 847, 2654),   # Вторая строка - label (Трансфер)
    "service_value2": (954, 2567, 1960, 2654),

    "manager_name": (907, 2860, 1849, 3024),    # имя менеджера
    "manager_phone": (1916, 3048, 2289, 3147),# Вторая строка - value (+7 775 846 73 47)
}

COORDS_SCENARIO_9 = {
    # Клиенты (многострочный список имён)
    "clients": (1481, 421, 2302, 646),

    # ПЕРВАЯ СТРАНА (верхняя таблица)
    "country_1": (959, 794, 1579, 881),
    "city_1": (959, 898, 1223, 985),
    "hotel_1": (959, 1002, 1654, 1089),
    "dates_1": (959, 1106, 1260, 1193),
    "stay_1": (959, 1210, 1306, 1287),
    "roomcat_1": (959, 1305, 1405, 1392),
    "meals_1": (959, 1410, 1335, 1496),

    # ВТОРАЯ СТРАНА (нижняя таблица)
    "country_2": (959, 1601, 1579, 1688),
    "city_2": (959, 1705, 1223, 1792),
    "hotel_2": (959, 1809, 1654, 1896),
    "dates_2": (959, 1912, 1259, 2000),
    "stay_2": (959, 2017, 1307, 2095),
    "roomcat_2": (959, 2112, 1410, 2199),
    "meals_2": (959, 2216, 1340, 2303),

    "service_label": (213, 2429, 373, 2516),    # Первая строка - label (Гид)
    "service_value": (427, 2429, 1433, 2516),   # Первая строка - value (+7 775 846 73 47)

    "service_label2": (213, 2540, 556, 2627),   # Вторая строка - label (Трансфер)
    "service_value2": (624, 2540, 1157, 2627),  # Вторая строка - value

    "service_label3": (213, 2652, 557, 2739),   # Третья строка - label (Экскурсии)
    "service_value3": (624, 2652, 1143, 2739),

    "manager_name": (907, 2860, 1849, 3024),    # имя менеджера
    "manager_phone": (1916, 3048, 2289, 3147),# Третья строка - value
}

COORDS_SCENARIO_10 = {
    # Клиенты (многострочный список имён)
    "clients": (1481, 360, 2301, 594),

    # ПЕРВАЯ СТРАНА (верхняя таблица)
    "country_1": (959, 737, 1579, 824),
    "city_1": (959, 848, 1223, 935),
    "hotel_1": (959, 947, 1654, 1034),
    "dates_1": (959, 1048, 1260, 1135),
    "stay_1": (959, 1151, 1306, 1229),
    "roomcat_1": (959, 1250, 1405, 1337),
    "meals_1": (959, 1356, 1335, 1443),

    # ВТОРАЯ СТРАНА (нижняя таблица)
    "country_2": (959, 1494, 1579, 1581),
    "city_2": (959, 1598, 1223, 1685),
    "hotel_2": (959, 1702, 1654, 1789),
    "dates_2": (959, 1805, 1259, 1892),
    "stay_2": (959, 1909, 1307, 1987),
    "roomcat_2": (959, 2005, 1410, 2092),
    "meals_2": (959, 2109, 1340, 2196),

    "service_label": (265, 2339, 453, 2426),    # Первая строка - label (Гид)
    "service_value": (434, 2339, 733, 2426),   # Первая строка - value

    "service_label2": (265, 2451, 614, 2537),   # Вторая строка - label (Трансфер)
    "service_value2": (670, 2451, 1108, 2538),  # Вторая строка - value

    "service_label3": (265, 2564, 586, 2650),   # Третья строка - label (Экскурсии)
    "service_value3": (633, 2564, 965, 2651),   # Третья строка - value

    "service_label4": (265, 2681, 906, 2768),   # Четвертая строка - label (Менеджер)
    "service_value4": (928, 2681, 1260, 2768),

    "manager_name": (907, 2860, 1849, 3024),    # имя менеджера
    "manager_phone": (1916, 3048, 2289, 3147),# Четвертая строка - value
}

# === ТЕСТОВЫЕ ДАННЫЕ ===
TEST_DATA = {
    "scenario_1": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        "country": "Турция",
        "city": "Анталья",
        "hotel": "Hotel Sultan Beach Resort",
        "dates": "15.11.2024 - 22.11.2024",
        "stay": "DBL (TWIN)",
        "roomcat": "Standard Room",
        "meals": "All Inclusive"
    },
    "scenario_2": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        "country": "Турция",
        "city": "Анталья",
        "hotel": "Hotel Sultan Beach Resort",
        "dates": "15.11.2024 - 22.11.2024",
        "stay": "DBL (TWIN)",
        "roomcat": "Standard Room",
        "meals": "All Inclusive",
        "service_label": "Гид",
        "service_value": "Мехмет Йылмаз - +90 555 123 4567"
    },
    "scenario_3": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        "country": "Турция",
        "city": "Анталья",
        "hotel": "Hotel Sultan Beach Resort",
        "dates": "15.11.2024 - 22.11.2024",
        "stay": "DBL (TWIN)",
        "roomcat": "Standard Room",
        "meals": "All Inclusive",
        "service_label": "Менеджер:",
        "service_value": "Хадижа",
        "service_label2": "Телефон:",
        "service_value2": "+7 705 846 73 47"
    },
    "scenario_4": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        "country": "Турция",
        "city": "Анталья",
        "hotel": "Hotel Sultan Beach Resort",
        "dates": "15.11.2024 - 22.11.2024",
        "stay": "DBL (TWIN)",
        "roomcat": "Standard Room",
        "meals": "All Inclusive",
        "service_label": "Гид",
        "service_value": "+7 (747) 9711111",
        "service_label2": "Трансфер",
        "service_value2": "Cadillac",
        "service_label3": "Экскурсии",
        "service_value3": "Мекка - Медина"
    },
    "scenario_5": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        "country": "Турция",
        "city": "Анталья",
        "hotel": "Hotel Sultan Beach Resort",
        "dates": "15.11.2024 - 22.11.2024",
        "stay": "DBL (TWIN)",
        "roomcat": "Standard Room",
        "meals": "All Inclusive",
        "service_label": "Гид",
        "service_value": "+7 (747) 9711111",
        "service_label2": "Сервис",
        "service_value2": "+7 (747) 9711111",
        "service_label3": "Трансфер",
        "service_value3": "Cadillac",
        "service_label4": "Экскурсии",
        "service_value4": "Мекка - Медина"
    },
    "scenario_6": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        # Первая страна (Саудовская Аравия)
        "country_1": "Саудовская Аравия",
        "city_1": "Джидда",
        "hotel_1": "Rixos Obhur Jeddah 5*",
        "dates_1": "31.10 - 02.11.2024",
        "stay_1": "DBL (KING)",
        "roomcat_1": "Superior Room",
        "meals_1": "All Inclusive",
        # Вторая страна (ОАЭ)
        "country_2": "ОАЭ",
        "city_2": "Дубай",
        "hotel_2": "Atlantis The Palm 5*",
        "dates_2": "03.11 - 07.11.2024",
        "stay_2": "DBL (TWIN)",
        "roomcat_2": "Deluxe Room",
        "meals_2": "Breakfast",
    },
    "scenario_7": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        # Первая страна
        "country_1": "Саудовская Аравия",
        "city_1": "Макка",
        "hotel_1": "Swissotel Al Maqam 5*",
        "dates_1": "10.11 - 12.11.2024",
        "stay_1": "DBL (KING)",
        "roomcat_1": "Superior",
        "meals_1": "Breakfast",
        # Вторая страна
        "country_2": "ОАЭ",
        "city_2": "Дубай",
        "hotel_2": "Rixos Premium JBR 5*",
        "dates_2": "12.11 - 15.11.2024",
        "stay_2": "DBL (TWIN)",
        "roomcat_2": "Deluxe",
        "meals_2": "HB",
        # Одна сервисная строка
        "service_label": "Гид",
        "service_value": "+966 55 123 4567"
    },
    "scenario_8": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        # Первая страна
        "country_1": "Саудовская Аравия",
        "city_1": "Джидда",
        "hotel_1": "Rixos Obhur Jeddah 5*",
        "dates_1": "05.12 - 08.12.2024",
        "stay_1": "DBL (KING)",
        "roomcat_1": "Superior",
        "meals_1": "BB",
        # Вторая страна
        "country_2": "Катар",
        "city_2": "Доха",
        "hotel_2": "Fairmont Doha 5*",
        "dates_2": "08.12 - 11.12.2024",
        "stay_2": "DBL (TWIN)",
        "roomcat_2": "Sea View",
        "meals_2": "HB",
        # Две сервисные строки
        "service_label": "Гид",
        "service_value": "+974 50 765 4321",
        "service_label2": "Трансфер",
        "service_value2": "Cadillac Escalade"
    },
    "scenario_9": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        # Первая страна
        "country_1": "Саудовская Аравия",
        "city_1": "Джидда",
        "hotel_1": "Rixos Obhur Jeddah 5*",
        "dates_1": "05.12 - 08.12.2024",
        "stay_1": "DBL (KING)",
        "roomcat_1": "Superior",
        "meals_1": "BB",
        # Вторая страна
        "country_2": "Катар",
        "city_2": "Доха",
        "hotel_2": "Fairmont Doha 5*",
        "dates_2": "08.12 - 11.12.2024",
        "stay_2": "DBL (TWIN)",
        "roomcat_2": "Sea View",
        "meals_2": "HB",
        # Три сервисные строки
        "service_label": "Гид",
        "service_value": "+974 50 765 4321",
        "service_label2": "Трансфер",
        "service_value2": "Cadillac Escalade",
        "service_label3": "Экскурсии",
        "service_value3": "Al-Ula"
    },
    "scenario_10": {
        "clients": ["ALEXEY MAMYRKANOV", "ASKABYL MAMYRKANOV"],
        # Первая страна
        "country_1": "Саудовская Аравия",
        "city_1": "Джидда",
        "hotel_1": "Rixos Obhur Jeddah 5*",
        "dates_1": "05.12 - 08.12.2024",
        "stay_1": "DBL (KING)",
        "roomcat_1": "Superior",
        "meals_1": "BB",
        # Вторая страна
        "country_2": "Катар",
        "city_2": "Доха",
        "hotel_2": "Fairmont Doha 5*",
        "dates_2": "08.12 - 11.12.2024",
        "stay_2": "DBL (TWIN)",
        "roomcat_2": "Sea View",
        "meals_2": "HB",
        # Четыре сервисные строки
        "service_label": "Гид",
        "service_value": "+974 50 765 4321",
        "service_label2": "Трансфер",
        "service_value2": "Cadillac Escalade",
        "service_label3": "Экскурсии",
        "service_value3": "Al-Ula",
        "service_label4": "Менеджер",
        "service_value4": "Хадиджа +87076754679"
    }
}

from PIL import ImageChops, ImageOps

from PIL import ImageChops

def _autocrop_alpha(im):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    bbox = im.split()[-1].getbbox()
    return im.crop(bbox) if bbox else im

def _paste_text_like(img_bg, asset, box, pad=(10,10,10,10)):
    """
    Вставка PNG как текста: автотрим, сохранение пропорций,
    выравнивание ПО ЛЕВОМУ КРАЮ, вертикальный центр внутри бокса.
    pad=(L,T,R,B) — такой же отступ, как в draw_in_box(+10,+10).
    """
    x1,y1,x2,y2 = box
    L,T,R,B = pad
    W = max(1, (x2-x1) - L - R)
    H = max(1, (y2-y1) - T - B)

    asset = _autocrop_alpha(asset)
    # вписываем по меньшей стороне с сохранением пропорций
    k = min(W/asset.width, H/asset.height)
    new_size = (max(1,int(asset.width*k)), max(1,int(asset.height*k)))
    asset = asset.resize(new_size, Image.Resampling.LANCZOS)

    ax = x1 + L                      # ЛЕВЫЙ КРАЙ
    ay = y1 + T + (H - asset.height)//2  # по центру по вертикали
    img_bg.paste(asset, (ax, ay), asset)
    return img_bg

    # --- 1) Утилиты для массовой правки боксов ---
def grow_box(box, dleft=0, dtop=0, dright=0, dbottom=0):
    x1,y1,x2,y2 = box
    return (x1 - dleft, y1 - dtop, x2 + dright, y2 + dbottom)

ALL_COORDS = [
    COORDS_SCENARIO_1, COORDS_SCENARIO_2, COORDS_SCENARIO_3, COORDS_SCENARIO_4, COORDS_SCENARIO_5,
    COORDS_SCENARIO_6, COORDS_SCENARIO_7, COORDS_SCENARIO_8, COORDS_SCENARIO_9, COORDS_SCENARIO_10,
]

def bump_all_phone_boxes(dright=20, dbottom=8):
    """Увеличить бокс телефона для всех сценариев (вправо и вниз)."""
    for C in ALL_COORDS:
        if "manager_phone" in C:
            C["manager_phone"] = grow_box(C["manager_phone"], dright=dright, dbottom=dbottom)

# вызов один раз после определения всех COORDS_*:
bump_all_phone_boxes(dright=20, dbottom=8)


PAD_NAME  = (10,10,10,10)   # как было
PAD_PHONE = (6,4,6,4)       # меньше отступ — больше видимый размер

def insert_manager_assets(img, manager_key, name_coords, phone_coords):
    try:
        m = MANAGER_ASSETS.get(manager_key, MANAGER_ASSETS["khadidzha"])

        if os.path.exists(m["name"]):
            name_img = Image.open(m["name"]).convert("RGBA")
            img = _paste_text_like(img, name_img,  name_coords,  pad=PAD_NAME)

        if os.path.exists(m["phone"]):
            phone_img = Image.open(m["phone"]).convert("RGBA")
            img = _paste_text_like(img, phone_img, phone_coords, pad=PAD_PHONE)

        return img
    except Exception as e:
        print("❌ Ошибка при вставке менеджера:", e)
        return img




# === ФУНКЦИИ РЕНДЕРИНГА ===
def create_clickable_pdf(image_path, scenario_id, output_path=None):
    """Создает PDF с кликабельными ссылками"""
    try:
        if output_path is None:
            output_path = f"voucher_scenario_{scenario_id}_{uuid.uuid4().hex[:8]}.pdf"

        # Создаем PDF
        c = canvas.Canvas(output_path, pagesize=A4)

        # Добавляем изображение ваучера (на всю страницу)
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Масштабируем изображение под размер страницы A4
        page_width, page_height = A4
        scale = min(page_width / img_width, page_height / img_height)
        new_width = img_width * scale
        new_height = img_height * scale

        # Центрируем изображение
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2

        # Добавляем изображение
        c.drawImage(image_path, x, y, new_width, new_height)

        # Добавляем кликабельные зоны для ссылок
        link_zones = LINK_ZONES.get(scenario_id, LINK_ZONES.get("default", {}))

        for link_type, zone_coords in link_zones.items():
            if link_type in LINKS:
                # Масштабируем координаты под новое расположение изображения
                x1, y1, x2, y2 = zone_coords

                # Преобразуем координаты из системы изображения в систему PDF
                pdf_x1 = x + (x1 * scale)
                pdf_y1 = y + (img_height * scale) - (y2 * scale)  # инвертируем Y
                pdf_x2 = x + (x2 * scale)
                pdf_y2 = y + (img_height * scale) - (y1 * scale)  # инвертируем Y

                # Добавляем кликабельную ссылку (невидимый прямоугольник)
                c.linkURL(
                    LINKS[link_type],
                    (pdf_x1, pdf_y1, pdf_x2, pdf_y2),
                    relative=0,
                    thickness=0
                )
                print(f"✅ Добавлена кликабельная ссылка: {link_type} -> {LINKS[link_type]}")

        # Сохраняем PDF
        c.save()
        print(f"✅ PDF с кликабельными ссылками сохранен: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Ошибка при создании PDF: {e}")
        return None

def test_scenario_with_pdf(scenario_id, coordinates, data_key):
    """Тестирует сценарий и создает PDF с кликабельными ссылками"""
    # Сначала создаем изображение
    image_path = _test_scenario(scenario_id, coordinates, data_key)

    if image_path and os.path.exists(image_path):
        # Затем создаем PDF с кликабельными ссылками
        pdf_path = create_clickable_pdf(image_path, scenario_id)
        return pdf_path
    else:
        print("❌ Не удалось создать изображение для PDF")
        return None

# Обновляем функции тестирования для создания PDF
def test_scenario_1():
    """Тестирование сценария 1 с созданием PDF"""
    print("🧪 Тестируем сценарий 1...")
    return test_scenario_with_pdf(1, COORDS_SCENARIO_1, "scenario_1")

def test_scenario_2():
    """Тестирование сценария 2 с созданием PDF"""
    print("🧪 Тестируем сценарий 2...")
    return test_scenario_with_pdf(2, COORDS_SCENARIO_2, "scenario_2")

def test_scenario_3():
    """Тестирование сценария 3 с созданием PDF"""
    print("🧪 Тестируем сценарий 3...")
    return test_scenario_with_pdf(3, COORDS_SCENARIO_3, "scenario_3")

def test_scenario_4():
    """Тестирование сценария 4 с созданием PDF"""
    print("🧪 Тестируем сценарий 4...")
    return test_scenario_with_pdf(4, COORDS_SCENARIO_4, "scenario_4")

def test_scenario_5():
    """Тестирование сценария 5 с созданием PDF"""
    print("🧪 Тестируем сценарий 5...")
    return test_scenario_with_pdf(5, COORDS_SCENARIO_5, "scenario_5")

def test_scenario_6():
    """Тестирование сценария 6 с созданием PDF"""
    print("🧪 Тестируем сценарий 6...")
    return test_scenario_with_pdf(6, COORDS_SCENARIO_6, "scenario_6")

def test_scenario_7():
    """Тестирование сценария 7 с созданием PDF"""
    print("🧪 Тестируем сценарий 7...")
    return test_scenario_with_pdf(7, COORDS_SCENARIO_7, "scenario_7")

def test_scenario_8():
    """Тестирование сценария 8 с созданием PDF"""
    print("🧪 Тестируем сценарий 8...")
    return test_scenario_with_pdf(8, COORDS_SCENARIO_8, "scenario_8")

def test_scenario_9():
    """Тестирование сценария 9 с созданием PDF"""
    print("🧪 Тестируем сценарий 9...")
    return test_scenario_with_pdf(9, COORDS_SCENARIO_9, "scenario_9")

def test_scenario_10():
    """Тестирование сценария 10 с созданием PDF"""
    print("🧪 Тестируем сценарий 10...")
    return test_scenario_with_pdf(10, COORDS_SCENARIO_10, "scenario_10")
def _test_scenario(scenario_id, coordinates, data_key):
    """Универсальная функция для тестирования сценариев"""
    try:
        # Загружаем фон
        bg_path = SCENARIOS[scenario_id]["bg_path"]
        if not os.path.exists(bg_path):
            print(f"❌ Фон не найден: {bg_path}")
            # Пробуем найти любой доступный фон
            for sc_id, config in SCENARIOS.items():
                if os.path.exists(config["bg_path"]):
                    bg_path = config["bg_path"]
                    print(f"🔄 Используем фон сценария {sc_id}: {bg_path}")
                    break

        img = Image.open(bg_path).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Шрифты
        font_large = ImageFont.truetype(FORUM_TTF, 61)   # клиенты (КАПС)
        font_medium = ImageFont.truetype(FORUM_TTF, 68)  # значения в таблицах
        font_small = ImageFont.truetype(FORUM_TTF, 65)   # сервисные строки

        data = TEST_DATA[data_key]
        coords = coordinates

        # Утилита для рисования строки в прямоугольнике (левый верх + отступы)
        def draw_in_box(key_box, text, font):
            x1, y1, _, _ = key_box
            draw.text((x1 + 10, y1 + 10), text, font=font, fill=(0, 0, 0))

        # === 1) Клиенты (правая колонка, выравнивание по правому краю)
        if "clients" in coords and "clients" in data:
            client_box = coords["clients"]
            line_height = 70
            y = client_box[1] + 10
            for client in data["clients"]:
                text_width = draw.textlength(client, font=font_large)
                x = client_box[2] - text_width - 20
                draw.text((x, y), client, font=font_large, fill=(0, 0, 0))
                y += line_height

        # === 2) Определяем, однотабличный режим или мульти-страны (_1/_2)
        has_multi = any(k.endswith("_1") for k in coords.keys())

        if not has_multi:
            # старое поведение: одна таблица слева
            for key in ["country", "city", "hotel", "dates", "stay", "roomcat", "meals"]:
                if key in coords and key in data:
                    draw_in_box(coords[key], data[key], font_medium)
        else:
            # новое поведение: рисуем блоки с суффиксами _1 и _2
            def draw_country_block(suffix: str):
                mapping = {
                    "country": f"country_{suffix}",
                    "city":    f"city_{suffix}",
                    "hotel":   f"hotel_{suffix}",
                    "dates":   f"dates_{suffix}",
                    "stay":    f"stay_{suffix}",
                    "roomcat": f"roomcat_{suffix}",
                    "meals":   f"meals_{suffix}",
                }
                for base, with_suf in mapping.items():
                    if with_suf in coords and with_suf in data:
                        draw_in_box(coords[with_suf], data[with_suf], font_medium)

            # верхний блок (_1) и нижний блок (_2), если есть данные
            draw_country_block("1")
            draw_country_block("2")

        # === 3) Сервисные строки с ВЫРАВНИВАНИЕМ ПО ПРАВОМУ КРАЮ ===
        def draw_service_line_aligned(label_coords, value_coords, label_text, value_text, font):
            # Лейбл пишем как обычно (левая часть)
            label_x = label_coords[0] + 10
            label_y = label_coords[1] + 10
            draw.text((label_x, label_y), label_text, font=font, fill=(0, 0, 0))

            # Вычисляем ширину лейбла
            label_width = draw.textlength(label_text, font=font)

            # Вычисляем стартовую позицию для значения (лейбл + отступ 30px)
            value_start_x = label_x + label_width + 40

            # Пишем значение
            draw.text((value_start_x, label_y), value_text, font=font, fill=(0, 0, 0))

        # Используем новую функцию для всех сервисных строк
        if "service_label" in coords and "service_value" in coords and \
                "service_label" in data and "service_value" in data:
            draw_service_line_aligned(coords["service_label"], coords["service_value"],
                                      data["service_label"], data["service_value"], font_small)

        if "service_label2" in coords and "service_value2" in coords and \
                "service_label2" in data and "service_value2" in data:
            draw_service_line_aligned(coords["service_label2"], coords["service_value2"],
                                      data["service_label2"], data["service_value2"], font_small)

        if "service_label3" in coords and "service_value3" in coords and \
                "service_label3" in data and "service_value3" in data:
            draw_service_line_aligned(coords["service_label3"], coords["service_value3"],
                                      data["service_label3"], data["service_value3"], font_small)

        if "service_label4" in coords and "service_value4" in coords and \
                "service_label4" in data and "service_value4" in data:
            draw_service_line_aligned(coords["service_label4"], coords["service_value4"],
                                      data["service_label4"], data["service_value4"], font_small)

        # === 4) ВСТАВКА МЕНЕДЖЕРА ===
        if "manager_name" in coords and "manager_phone" in coords:
            img = insert_manager_assets(img, MANAGER_KEY,
                                        coords["manager_name"],
                                        coords["manager_phone"])

        # Сохранение
        filename = f"test_scenario_{scenario_id}_{uuid.uuid4().hex[:8]}.png"
        img.save(filename)
        print(f"✅ Тестовый ваучер сохранен: {filename}")
        return filename

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

# === ИНТЕРАКТИВНОЕ ТЕСТИРОВАНИЕ ===
def select_manager():
    """Выбор менеджера"""
    print("\n👨‍💼 ВЫБЕРИТЕ МЕНЕДЖЕРА:")
    managers = list(MANAGER_ASSETS.keys())
    for i, manager in enumerate(managers, 1):
        print(f"{i}. {manager}")

    choice = input(f"Ваш выбор (1-{len(managers)}): ").strip()
    try:
        selected_index = int(choice) - 1
        if 0 <= selected_index < len(managers):
            return managers[selected_index]
        else:
            print("❌ Неверный выбор, используем khadidzha")
            return "khadidzha"
    except ValueError:
        print("❌ Неверный ввод, используем khadidzha")
        return "khadidzha"

def interactive_coordinate_test():
    """Интерактивный тест координат"""
    print("\n🎯 ИНТЕРАКТИВНЫЙ ТЕСТ КООРДИНАТ")
    print("=" * 50)

    # Выбираем менеджера один раз в начале
    global MANAGER_KEY
    MANAGER_KEY = select_manager()
    print(f"🎯 Выбран менеджер: {MANAGER_KEY}")

    while True:
        print("\nВыберите действие:")
        print("1. Тест сценария 1 (базовый)")
        print("2. Тест сценария 2 (с гидом)")
        print("3. Тест сценария 3 (с сервисом)")
        print("4. Тест сценария 4 (3 сервисные строки)")
        print("5. Тест сценария 5 (4 сервисные строки)")
        print("6. Тест сценария 6 (2 страны)")
        print("7. Тест сценария 7 (2 страны + 1 сервисная)")
        print("8. Тест сценария 8 (2 страны + 2 сервисные)")
        print("9. Тест сценария 9 (2 страны + 3 сервисные)")
        print("10. Тест сценария 10 (2 страны + 4 сервисные)")
        print("11. Сменить менеджера")
        print("12. Показать текущие координаты")
        print("0. Выход")

        choice = input("Ваш выбор (0-12): ").strip()

        if choice == "1":
            test_scenario_1()
        elif choice == "2":
            test_scenario_2()
        elif choice == "3":
            test_scenario_3()
        elif choice == "4":
            test_scenario_4()
        elif choice == "5":
            test_scenario_5()
        elif choice == "6":
            test_scenario_6()
        elif choice == "7":
            test_scenario_7()
        elif choice == "8":
            test_scenario_8()
        elif choice == "9":
            test_scenario_9()
        elif choice == "10":
            test_scenario_10()
        elif choice == "11":
            MANAGER_KEY = select_manager()
        elif choice == "12":
            break
        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    print("🧪 ТЕСТИРОВАНИЕ СЦЕНАРИЕВ AMAL VOUCHER")
    print("=" * 50)

    # Показываем доступные сценарии
    print("📁 Доступные сценарии:")
    for scenario_id, config in SCENARIOS.items():
        print(f"  {scenario_id}. {config['name']} - {config['description']}")

    # Запускаем интерактивное тестирование
    interactive_coordinate_test()