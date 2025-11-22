import os
import re
import uuid
import asyncio
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, BufferedInputFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

import os
from dotenv import load_dotenv
load_dotenv()

# === КОНФИГУРАЦИЯ ===
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("API_TOKEN") or ""
if not BOT_TOKEN or ":" not in BOT_TOKEN:
    raise RuntimeError(
        "Отсутствует BOT_TOKEN (или он некорректен). "
        "Добавь его в переменные окружения или в .env"
    )

# Папки для разных языков
LANGUAGE_FOLDERS = {
    "ru": "scen/ru",  # Русские шаблоны
    "en": "scen/en"   # Английские шаблоны
}

# Проверяем существование папок
for lang, folder in LANGUAGE_FOLDERS.items():
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        print(f"⚠️ Создана папка: {folder}")

from aiogram import Bot
bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

Image.MAX_IMAGE_PIXELS = None
FORUM_TTF = os.path.expanduser("Forum-Regular.ttf")

# === ТЕКСТЫ ДЛЯ РАЗНЫХ ЯЗЫКОВ ===
TEXTS = {
    "ru": {
        "start": "🕌 Ассаляму алейкум ва рахматуЛлахи ва баракятуху!\n\n"
                 "Добро пожаловать в конструктор ваучеров AMAL!",

        "choose_manager": "👨‍💼 Кто будет делать ваучер? Выберите менеджера:",
        "choose_language": "🌐 На каком языке составить ваучер?",
        "choose_countries": "🌍 На сколько стран делаем ваучер?",
        "choose_clients_count": "👥 На сколько клиентов делаем ваучер?",

        "enter_clients": "👥 Введите ФИО {count} клиента(ов) ЧЕРЕЗ ЗАПЯТУЮ.\n\n"
                         "📝 Пример: {example}",

        "clients_example_1": "Имя Фамилия",
        "clients_example_2": "Имя Фамилия 1, Имя Фамилия 2",
        "clients_example_3": "Имя Фамилия 1, Имя Фамилия 2, Имя Фамилия 3",

        "clients_saved": "✅ Список клиентов сохранён!\n\n"
                         "👥 Проверьте: {clients_text}\n\n"
                         "Всё верно?",

        "enter_country": "🌍 Введите название страны:",
        "enter_city": "🏙️ Введите город:",
        "enter_hotel": "🏨 Введите название отеля:",
        "enter_dates": "📅 Введите даты пребывания:",
        "enter_stay": "🛏️ Введите тип размещения:",
        "enter_roomcat": "⭐ Введите категорию номера:",
        "enter_meals": "🍽️ Введите тип питания:",
        "enter_booking": "📋 Введите номер бронирования:",

        "choose_services": "🔧 Выберите дополнительные сервисы:",

        "enter_guide": "🧑‍💼 Введите информацию о гиде:",
        "enter_transfer": "🚗 Введите информацию о трансфере:",
        "enter_excursions": "🏛️ Введите информацию об экскурсиях:",
        "enter_extra": "📞 Введите дополнительный контакт менеджера:",

        "country_example": "Например: ОАЭ",
        "city_example": "Например: Дубай",
        "hotel_example": "Например: Burj Al Arab",
        "dates_example": "Например: 15.12.2024 - 22.12.2024",
        "stay_example": "Например: Standard Room",
        "roomcat_example": "Например: 5*",
        "meals_example": "Например: Завтрак",
        "booking_example": "Например: AML-123456789",
        "guide_example": "Например: Русскоязычный гид, 5 часов в день",
        "transfer_example": "Например: Встреча в аэропорту, машина бизнес-класса",
        "excursions_example": "Например: Обзорная экскурсия по городу, посещение музеев",
        "extra_example": "Например: +7 777 123 45 67 (WhatsApp)",

        "data_saved": "✅ Все данные сохранены!",
        "generating": "🔄 Генерирую ваучер...",
        "voucher_ready": "✅ Ваш ваучер готов!\n\nХотите создать ещё один ваучер?",
    },

    "en": {
        "start": "🕌 Ассаляму алейкум ва рахматуЛлахи ва баракятуху!\n"
                 "Добро пожаловать в конструктор ваучеров AMAL!\n\n"
                 "🕌 Assalamu alaikum wa rahmatullahi wa barakatuh!\n"
                 "Welcome to AMAL voucher constructor!",

        "choose_manager": "👨‍💼 Кто будет делать ваучер? Выберите менеджера:\n"
                          "Who will make the voucher? Choose manager:",

        "choose_language": "🌐 На каком языке составить ваучер?\n"
                           "In which language to create the voucher?",

        "choose_countries": "🌍 На сколько стран делаем ваучер?\n"
                            "For how many countries are we making the voucher?",

        "choose_clients_count": "👥 На сколько клиентов делаем ваучер?\n"
                                "For how many clients are we making the voucher?",

        "enter_clients": "👥 Введите ФИО {count} клиента(ов) ЧЕРЕЗ ЗАПЯТУЮ.\n"
                         "👥 Enter full name of {count} client(s) separated by comma.\n\n"
                         "📝 Пример: {example}\n"
                         "Example: {example}",

        "clients_example_1": "Имя Фамилия / John Smith",
        "clients_example_2": "Имя Фамилия 1, Имя Фамилия 2 / John Smith, Jane Doe",
        "clients_example_3": "Имя Фамилия 1, Имя Фамилия 2, Имя Фамилия 3 / John Smith, Jane Doe, Michael Brown",

        "clients_saved": "👥 Проверьте: {clients_text}\n"
                         "Всё верно?\n\n",

        "enter_country": "🌍 Введите название страны:\nEnter country name:",
        "enter_city": "🏙️ Введите город:\nEnter city:",
        "enter_hotel": "🏨 Введите название отеля:\nEnter hotel name:",
        "enter_dates": "📅 Введите даты пребывания:\nEnter stay dates:",
        "enter_stay": "🛏️ Введите тип размещения:\nEnter accommodation type:",
        "enter_roomcat": "⭐ Введите категорию номера:\nEnter room category:",
        "enter_meals": "🍽️ Введите тип питания:\nEnter meal type:",
        "enter_booking": "📋 Введите номер бронирования:\nEnter booking number:",

        "choose_services": "🔧 Выберите дополнительные сервисы:\nChoose additional services:",

        "enter_guide": "🧑‍💼 Введите информацию о гиде:\nEnter guide information:",
        "enter_transfer": "🚗 Введите информацию о трансфере:\nEnter transfer information:",
        "enter_excursions": "🏛️ Введите информацию об экскурсиях:\nEnter excursions information:",
        "enter_extra": "📞 Введите дополнительный контакт менеджера:\nEnter additional manager contact:",

        # ⬇⬇⬇ ДОБАВЛЕННЫЕ ПРИМЕРЫ ДЛЯ АНГЛИЙСКОГО ЯЗЫКА
        "country_example": "For example: UAE",
        "city_example": "For example: Dubai",
        "hotel_example": "For example: Burj Al Arab",
        "dates_example": "For example: 15.12.2024 - 22.12.2024",
        "stay_example": "For example: Standard Room",
        "roomcat_example": "For example: 5*",
        "meals_example": "For example: Breakfast",
        "booking_example": "For example: AML-123456789",

        "guide_example": "For example: English-speaking guide, 5 hours per day",
        "transfer_example": "For example: Airport meet & greet, business class car",
        "excursions_example": "For example: City sightseeing tour, museum visit",
        "extra_example": "For example: +7 777 123 45 67 (WhatsApp)",

        # Сообщение-напоминание, которое ты вызываешь как TEXTS["en"]["fill_in_english"]
        "fill_in_english": "❗ Please fill in all voucher data in English only.",

        "data_saved": "❗Пожалуйста, заполняйте все данные на английском языке\n\n"
                      "All data saved!",

        "generating": "🔄 Генерирую ваучер...\nGenerating voucher...",
        "voucher_ready": "Ваш ваучер готов!\nYour voucher is ready!\n\n"
                         "Создать ещё один?\nCreate another?"
    }

}


# === МЕНЕДЖЕРЫ ===
MANAGER_ASSETS = {
    "Aidana Alimbekova": {"name": "res/aidana_name.png", "phone": "phones/aidana_phone-2.png"},
    "Sarkitbayeva Elvira": {"name": "res/elvira_name.png", "phone": "phones/elvira_phone-2.png"},
    "Khadidzha Gavarukha": {"name": "res/khadidzha_name.png", "phone": "phones/khadidzha_phone-2.png"},
    "Ponomareva Mariya": {"name": "res/marina_name.png", "phone": "phones/marina_phone-2.png"},
    "Minira Yerkibayeva": {"name": "res/minira_name.png", "phone": "phones/minira_phone-2.png"},
    "Oxana Kazakova": {"name": "res/oxana_name.png", "phone": "phones/oxana_phone-2.png"},
}

# === ССЫЛКИ ===
LINKS = {
    "whatsapp": "https://wa.me/77479711111?text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5%2C%20%D1%85%D0%BE%D1%87%D1%83%20%D1%83%D0%B7%D0%BD%D0%B0%D1%82%D1%8C%20%D0%BF%D0%BE%20%D0%B2%D0%B0%D1%83%D1%87%D0%B5%D1%80%D1%83",
    "instagram": "https://instagram.com/amalexperiences"
}

LINK_ZONES = {
    1: {"whatsapp": (1135, 3187, 1208, 3260), "instagram": (1255, 3187, 1328, 3260)},
    2: {"whatsapp": (1124, 3216, 1197, 3289), "instagram": (1244, 3216, 1317, 3289)},
    3: {"whatsapp": (1124, 3216, 1197, 3289), "instagram": (1244, 3216, 1317, 3289)},
    4: {"whatsapp": (1124, 3216, 1197, 3289), "instagram": (1244, 3216, 1317, 3289)},
    5: {"whatsapp": (1124, 3216, 1197, 3289), "instagram": (1244, 3216, 1317, 3289)},
    6: {"whatsapp": (1160, 3322, 1233, 3395), "instagram": (1281, 3322, 1354, 3395)},
    7: {"whatsapp": (1160, 3322, 1233, 3395), "instagram": (1281, 3322, 1354, 3395)},
    8: {"whatsapp": (1038, 3381, 1110, 3453), "instagram": (1145, 3381, 1217, 3453)},
    9: {"whatsapp": (1038, 3381, 1110, 3453), "instagram": (1145, 3381, 1217, 3453)},
    10: {"whatsapp": (1038, 3381, 1110, 3453), "instagram": (1145, 3381, 1217, 3453)},
    "default": {"whatsapp": (1830, 3120, 1905, 3195), "instagram": (1915, 3120, 1990, 3195)}
}

# === СЦЕНАРИИ И ФОНЫ ===
def get_scenario_path(language: str, scenario_id: int) -> str:
    """Получает путь к фону сценария для выбранного языка"""
    base_folder = LANGUAGE_FOLDERS.get(language, "scen/ru")  # По умолчанию русский
    return f"{base_folder}/scen{scenario_id}.png"

SCENARIOS = {
    1: {"name": "Превью вашего ваучера"},
    2: {"name": "Превью вашего ваучера"},
    3: {"name": "Превью вашего ваучера"},
    4: {"name": "Превью вашего ваучера"},
    5: {"name": "Превью вашего ваучера"},
    6: {"name": "Превью вашего ваучера"},
    7: {"name": "Превью вашего ваучера"},
    8: {"name": "Превью вашего ваучера"},
    9: {"name": "Превью вашего ваучера"},
    10: {"name": "Превью вашего ваучера"},
}

# === КООРДИНАТЫ ===
COORDS_SCENARIO_1 = {
    "clients": (1480, 738, 2303, 995),
    "country": (1027, 1385, 1821, 1484),
    "city": (1027, 1504, 1821, 1603),
    "hotel": (1027, 1622, 1821, 1721),
    "dates": (1027, 1741, 1821, 1840),
    "stay": (1027, 1845, 1821, 1937),
    "roomcat": (1027, 1959, 1821, 2058),
    "meals": (1027, 2088, 1821, 2173),
    "booking": (1027, 2198, 1821, 2297),
    "manager_name": (998, 2680, 1913, 2840),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_2 = {
    "clients": (1480, 738, 2303, 995),
    "country": (1027, 1223, 1821, 1323),
    "city": (1027, 1338, 1821, 1437),
    "hotel": (1027, 1452, 1821, 1551),
    "dates": (1027, 1567, 1821, 1666),
    "stay": (1027, 1682, 1821, 1772),
    "roomcat": (1027, 1795, 1821, 1895),
    "meals": (1027, 1911, 1821, 2010),
    "booking": (1027, 2025, 1821, 2125),
    "service_label": (222, 2388, 346, 2475),
    "manager_name": (985, 2707, 1898, 2866),
    "manager_phone": (1926, 2884, 2273, 2976)
}

COORDS_SCENARIO_3 = {
    "clients": (1480, 738, 2303, 995),
    "country": (1027, 1214, 1821, 1313),
    "city": (1027, 1329, 1821, 1429),
    "hotel": (1027, 1444, 1821, 15444),
    "dates": (1027, 1559, 1821, 1658),
    "stay": (1027, 1673, 1821, 1773),
    "roomcat": (1027, 1788, 1821, 1888),
    "meals": (1027, 1902, 1821, 2002),
    "booking": (1027, 2017, 1821, 2117),
    "service_label": (208, 2280, 331, 2367),
    "service_value": (413, 2280, 920, 2367),
    "service_label2": (208, 2396, 838, 2483),
    "service_value2": (929, 2396, 1935, 2483),
    "manager_name": (998, 2710, 1913, 2870),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_4 = {
    "clients": (1480, 738, 2303, 995),
    "country": (1027, 1229, 1821, 1329),
    "city": (1027, 1343, 1821, 1443),
    "hotel": (1027, 1458, 1821, 1558),
    "dates": (1027, 1573, 1821, 1673),
    "stay": (1027, 1687, 1821, 1787),
    "roomcat": (1027, 1802, 1821, 1902),
    "meals": (1027, 1916, 1821, 2016),
    "booking": (1027, 2031, 1821, 2131),
    "service_label": (212, 2253, 335, 2340),
    "service_value": (426, 2296, 1434, 2383),
    "service_label2": (212, 2369, 842, 2456),
    "service_value2": (623, 2407, 1156, 2506),
    "service_label3": (212, 2486, 837, 2573),
    "service_value3": (623, 2523, 1141, 2610),
    "manager_name": (998, 2710, 1913, 2870),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_5 = {
    "clients": (1034, 651, 2314, 909),
    "country": (1027, 1108, 1821, 1207),
    "city": (1027, 1222, 1821, 1322),
    "hotel": (1027, 1337, 1821, 1437),
    "dates": (1027, 1451, 1821, 1551),
    "stay": (1027, 1566, 1821, 1666),
    "roomcat": (1027, 1680, 1821, 1780),
    "meals": (1027, 1795, 1821, 1895),
    "booking": (1027, 1910, 1821, 2110),
    "service_label": (216, 2174, 692, 2261),
    "service_value": (406, 2218, 1412, 2306),
    "service_label2": (216, 2286, 692, 2373),
    "service_value2": (523, 2328, 1529, 2415),
    "service_label3": (216, 2397, 692, 2484),
    "service_value3": (581, 2437, 1114, 2524),
    "service_label4": (216, 2508, 692, 2595),
    "service_value4": (611, 2539, 1129, 2616),
    "manager_name": (998, 2710, 1913, 2870),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_6 = {
    "clients": (1085, 550, 2365, 815),
    "country_1": (959, 1010, 1754, 1095),
    "city_1": (959, 1116, 1754, 1201),
    "hotel_1": (959, 1221, 1754, 1309),
    "dates_1": (959, 1316, 1754, 1405),
    "stay_1": (959, 1411, 1754, 1491),
    "roomcat_1": (959, 1515, 1754, 1600),
    "meals_1": (959, 1618, 1754, 1706),
    "booking_1": (959, 1722, 1754, 1822),
    "country_2": (959, 1920, 1754, 2020),
    "city_2": (959, 2025, 1754, 2125),
    "hotel_2": (959, 2129, 1754, 2239),
    "dates_2": (959, 2222, 1754, 2322),
    "stay_2": (959, 2325, 1754, 2425),
    "roomcat_2": (959, 2429, 1754, 2529),
    "meals_2": (959, 2532, 1754, 2632),
    "booking_2": (959, 2636, 1754, 2736),
    "manager_name": (1022, 2812, 1903, 2965),
    "manager_phone": (1966, 2988, 2315, 3081),
}

COORDS_SCENARIO_7 = {
    "clients": (1047, 395, 2327, 652),
    "country_1": (930, 776, 1724, 876),
    "city_1": (930, 882, 1724, 982),
    "hotel_1": (930, 989, 1724, 999),
    "dates_1": (930, 1088, 1724, 1188),
    "stay_1": (930, 1188, 1724, 1288),
    "roomcat_1": (930, 1295, 1724, 1395),
    "meals_1": (930, 1389, 1724, 1489),
    "booking_1": (930, 1493, 1724, 1593),
    "country_2": (930, 1682, 1724, 1782),
    "city_2": (930, 1788, 1724, 1888),
    "hotel_2": (930, 1895, 1724, 1995),
    "dates_2": (930, 1986, 1724, 2086),
    "stay_2": (930, 2094, 1724, 2194),
    "roomcat_2": (930, 2201, 1724, 2300),
    "meals_2": (930, 2295, 1724, 2395),
    "booking_2": (930, 2399, 1724, 2500),
    "service_label": (271, 2619, 917, 2719),
    "service_value": (1153, 2524, 1673, 2611),
    "manager_name": (1022, 2812, 1903, 2965),
    "manager_phone": (1966, 2988, 2315, 3081),
}

COORDS_SCENARIO_8 = {
    "clients": (1058, 301, 2340, 558),
    "country_1": (930, 663, 1724, 763),
    "city_1": (930, 769, 1724, 869),
    "hotel_1": (930, 877, 1724, 977),
    "dates_1": (930, 975, 1724, 1075),
    "stay_1": (930, 1075, 1724, 1175),
    "roomcat_1": (930, 1182, 1724, 1282),
    "meals_1": (930, 1276, 1724, 1376),
    "booking_1": (930, 1380, 1724, 1480),
    "country_2": (930, 1578, 1724, 1678),
    "city_2": (930, 1684, 1724, 1784),
    "hotel_2": (930, 1792, 1724, 1892),
    "dates_2": (930, 1890, 1724, 1990),
    "stay_2": (930, 1990, 1724, 2090),
    "roomcat_2": (930, 2097, 1724, 2197),
    "meals_2": (930, 2191, 1724, 2291),
    "booking_2": (930, 2295, 1724, 2395),
    "service_label": (216, 2520, 560, 2620),
    "service_value": (623, 2468, 1127, 2555),
    "service_label2": (216, 2620, 847, 2720),
    "service_value2": (954, 2567, 1960, 2654),
    "manager_name": (907, 2860, 1849, 3024),
    "manager_phone": (1916, 3048, 2289, 3147),
}

COORDS_SCENARIO_9 = {
    "clients": (1073, 290, 2353, 547),
    "country_1": (930, 664, 1724, 764),
    "city_1": (930, 770, 1724, 870),
    "hotel_1": (930, 877, 1724, 977),
    "dates_1": (930, 976, 1724, 1076),
    "stay_1": (930, 1076, 1724, 1176),
    "roomcat_1": (930, 1183, 1724, 1283),
    "meals_1": (930, 1277, 1724, 1377),
    "booking_1": (930, 1381, 1724, 1481),
    "country_2": (930, 1578, 1724, 1678),
    "city_2": (930, 1684, 1724, 1784),
    "hotel_2": (930, 1791, 1724, 1891),
    "dates_2": (930, 1890, 1724, 1990),
    "stay_2": (930, 1990, 1724, 2090),
    "roomcat_2": (930, 2097, 1724, 2197),
    "meals_2": (959309, 2191, 1724, 2291),
    "booking_2": (930, 2295, 1724, 2395),
    "service_label": (216, 2499, 559, 2586),
    "service_value": (427, 2429, 1433, 2516),
    "service_label2": (216, 2610, 559, 2697),
    "service_value2": (624, 2540, 1157, 2627),
    "service_label3": (216, 2721, 559, 2810),
    "service_value3": (624, 2652, 1143, 2739),
    "manager_name": (907, 2860, 1849, 3024),
    "manager_phone": (1916, 3048, 2289, 3147),
}

# === СОСТОЯНИЯ ===
class VoucherStates(StatesGroup):
    waiting_for_manager = State()
    waiting_for_language = State()
    waiting_for_countries_count = State()
    waiting_for_clients_count = State()
    waiting_for_clients = State()
    waiting_for_clients_confirmation = State()
    waiting_for_country_1 = State()
    waiting_for_city_1 = State()
    waiting_for_hotel_1 = State()
    waiting_for_dates_1 = State()
    waiting_for_stay_1 = State()
    waiting_for_roomcat_1 = State()
    waiting_for_meals_1 = State()
    waiting_for_booking_1 = State()
    waiting_for_country_2 = State()
    waiting_for_city_2 = State()
    waiting_for_hotel_2 = State()
    waiting_for_dates_2 = State()
    waiting_for_stay_2 = State()
    waiting_for_roomcat_2 = State()
    waiting_for_meals_2 = State()
    waiting_for_booking_2 = State()
    waiting_for_services_selection = State()
    waiting_for_guide_info = State()
    waiting_for_transfer_info = State()
    waiting_for_excursions_info = State()
    waiting_for_extra_info = State()

class EditVoucherStates(StatesGroup):
    editing_clients = State()
    editing_hotel_choose_block = State()
    editing_hotel_country = State()
    editing_hotel_city = State()
    editing_hotel_name = State()
    editing_hotel_dates = State()
    editing_hotel_stay = State()
    editing_hotel_roomcat = State()
    editing_hotel_meals = State()
    editing_hotel_booking = State()
    editing_services_bulk = State()
    editing_manager = State()

# === ХРАНЕНИЕ ДАННЫХ ===
VOUCHER_CACHE = {}
user_services = {}

# === КЛАВИАТУРЫ ===
def get_main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Создать ваучер", callback_data="create_voucher")]
    ])

def get_managers_kb():
    buttons = []
    managers = list(MANAGER_ASSETS.keys())
    for manager in managers:
        buttons.append([InlineKeyboardButton(
            text=f"👨‍💼 {manager}",
            callback_data=f"manager:{manager}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_language_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_managers")]
    ])

def get_countries_count_kb(language="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" 1 страна", callback_data="countries:1")],
        [InlineKeyboardButton(text=" 2 страны", callback_data="countries:2")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_language")]
    ])

def get_clients_count_kb(language="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 1 клиент", callback_data="clients:1")],
        [InlineKeyboardButton(text="👥 2 клиента", callback_data="clients:2")],
        [InlineKeyboardButton(text="👥 3 клиента", callback_data="clients:3")],
        [InlineKeyboardButton(text="👥 4 клиента", callback_data="clients:4")],
        [InlineKeyboardButton(text="👥 5+ клиентов", callback_data="clients:custom")],
        [InlineKeyboardButton(text="⬅️ Назад к странам", callback_data="back_to_countries")]
    ])

def get_clients_confirmation_kb(language="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, всё верно", callback_data="clients_correct")],
        [InlineKeyboardButton(text="✏️ Нет, изменить имена", callback_data="clients_edit")],
        [InlineKeyboardButton(text="🔢 Изменить количество", callback_data="back_to_clients_count")]
    ])

def get_services_kb(user_id: int, language="ru"):
    selected = user_services.get(user_id, set())
    buttons = []

    guide_text = "✅ Гид" if "guide" in selected else "☑️ Гид"
    transfer_text = "✅ Трансфер" if "transfer" in selected else "☑️ Трансфер"
    excursions_text = "✅ Экскурсии" if "excursions" in selected else "☑️ Экскурсии"
    extra_text = "✅ Доп. контакт" if "extra" in selected else "☑️ Доп. контакт"

    buttons.append([InlineKeyboardButton(text=guide_text, callback_data="service_toggle:guide")])
    buttons.append([InlineKeyboardButton(text=transfer_text, callback_data="service_toggle:transfer")])
    buttons.append([InlineKeyboardButton(text=excursions_text, callback_data="service_toggle:excursions")])
    buttons.append([InlineKeyboardButton(text=extra_text, callback_data="service_toggle:extra")])

    if selected:
        continue_text = "🚀 Продолжить с выбранными сервисами" if language == "ru" else "🚀 Continue with selected services"
        buttons.append([InlineKeyboardButton(text=continue_text, callback_data="services_confirm")])

    none_text = "⏭️ Без сервисов" if language == "ru" else "⏭️ Without services"
    back_text = "⬅️ Назад" if language == "ru" else "⬅️ Back"

    buttons.append([InlineKeyboardButton(text=none_text, callback_data="services_none")])
    buttons.append([InlineKeyboardButton(text=back_text, callback_data="back_to_meals")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_edit_kb(cache_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Изменить клиентов", callback_data=f"edit_clients:{cache_id}")],
        [InlineKeyboardButton(text="📋 Изменить основную часть", callback_data=f"edit_main:{cache_id}")],
        [InlineKeyboardButton(text="🔧 Изменить сервисы", callback_data=f"edit_services:{cache_id}")],
        [InlineKeyboardButton(text="👨‍💼 Изменить менеджера", callback_data=f"edit_manager:{cache_id}")],
        [InlineKeyboardButton(text="✅ Сгенерировать ваучер", callback_data=f"generate:{cache_id}")]
    ])

def get_new_voucher_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Создать новый ваучер", callback_data="create_voucher")]
    ])

# === ОСНОВНЫЕ ОБРАБОТЧИКИ ===
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        TEXTS["ru"]["start"],
        reply_markup=get_main_menu_kb()
    )

@dp.callback_query(F.data == "create_voucher")
async def start_voucher_creation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    if user_id in user_services:
        del user_services[user_id]

    await callback.message.answer(
        TEXTS["ru"]["choose_manager"],
        reply_markup=get_managers_kb()
    )
    await state.set_state(VoucherStates.waiting_for_manager)
    await callback.answer("🚀 Начинаем создание нового ваучера!")

@dp.callback_query(F.data.startswith("manager:"))
async def process_manager_selection(callback: CallbackQuery, state: FSMContext):
    manager_key = callback.data.split(":")[1]
    await state.update_data(manager_key=manager_key)

    await callback.message.answer(
        TEXTS["ru"]["choose_language"],
        reply_markup=get_language_kb()
    )
    await state.set_state(VoucherStates.waiting_for_language)
    await callback.answer()

@dp.callback_query(F.data.startswith("lang:"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await state.update_data(language=lang)

    # Если выбран английский, показываем сообщение о заполнении на английском ТОЛЬКО ЗДЕСЬ
    if lang == "en":
        await callback.message.answer(TEXTS["en"]["fill_in_english"])

    # Проверяем существование файлов для выбранного языка
    base_folder = LANGUAGE_FOLDERS.get(lang, "scen/ru")
    missing_files = []

    for scenario_id in range(1, 11):
        expected_file = f"{base_folder}/scen{scenario_id}.png"
        if not os.path.exists(expected_file):
            missing_files.append(f"scen{scenario_id}.png")

    if missing_files:
        warning_msg = (
                f"⚠️ Внимание! Для языка {lang} отсутствуют файлы:\n" +
                "\n".join(missing_files[:5]) +  # Показываем только первые 5
                f"\n\nПожалуйста, добавьте файлы в папку {base_folder}/"
        )
        await callback.message.answer(warning_msg)

    await callback.message.answer(
        TEXTS[lang]["choose_countries"],
        reply_markup=get_countries_count_kb(lang)
    )
    await state.set_state(VoucherStates.waiting_for_countries_count)
    await callback.answer()

@dp.callback_query(F.data.startswith("countries:"))
async def process_countries_count(callback: CallbackQuery, state: FSMContext):
    countries_count = int(callback.data.split(":")[1])
    await state.update_data(countries_count=countries_count)

    data = await state.get_data()
    language = data.get('language', 'ru')

    await callback.message.answer(
        TEXTS[language]["choose_clients_count"],
        reply_markup=get_clients_count_kb(language)
    )
    await state.set_state(VoucherStates.waiting_for_clients_count)
    await callback.answer()

@dp.callback_query(F.data.startswith("clients:"))
async def process_clients_count(callback: CallbackQuery, state: FSMContext):
    clients_count = callback.data.split(":")[1]

    data = await state.get_data()
    language = data.get('language', 'ru')

    if clients_count == "custom":
        custom_text = "👥 Введите число клиентов (например: 6)" if language == "ru" else "👥 Enter number of clients (example: 6)"
        await callback.message.answer(custom_text)
        await state.set_state(VoucherStates.waiting_for_clients_count)
    else:
        count = int(clients_count)

        # Выбираем пример в зависимости от языка
        if language == "ru":
            if count == 1:
                example = TEXTS["ru"]["clients_example_1"]
            elif count == 2:
                example = TEXTS["ru"]["clients_example_2"]
            else:
                example = TEXTS["ru"]["clients_example_3"]
        else:
            if count == 1:
                example = TEXTS["en"]["clients_example_1"]
            elif count == 2:
                example = TEXTS["en"]["clients_example_2"]
            else:
                example = TEXTS["en"]["clients_example_3"]

        await callback.message.answer(
            TEXTS[language]["enter_clients"].format(count=count, example=example)
        )
        await state.update_data(clients_count=count)
        await state.set_state(VoucherStates.waiting_for_clients)
    await callback.answer()

@dp.message(VoucherStates.waiting_for_clients_count)
async def process_custom_clients_count(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        if count <= 0:
            await message.answer("❌ Число должно быть больше 0. Введите снова:")
            return

        data = await state.get_data()
        language = data.get('language', 'ru')

        if language == "ru":
            example = "Имя Фамилия 1, Имя Фамилия 2"
        else:
            example = "John Smith, Jane Doe"

        await message.answer(
            TEXTS[language]["enter_clients"].format(count=count, example=example)
        )
        await state.update_data(clients_count=count)
        await state.set_state(VoucherStates.waiting_for_clients)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число:")

@dp.message(VoucherStates.waiting_for_clients)
async def handle_clients(message: Message, state: FSMContext):
    clients = [c.strip() for c in re.split(r'[,;\n]+', message.text) if c.strip()]

    if not clients:
        await message.answer("❌ Вы не ввели ни одного имени. Введите ФИО через запятую:")
        return

    data = await state.get_data()
    expected_count = data.get('clients_count')
    language = data.get('language', 'ru')

    if expected_count and len(clients) != expected_count:
        await message.answer(
            f"❌ Количество не совпадает!\n"
            f"Вы выбрали: {expected_count}\n"
            f"Вы ввели: {len(clients)}\n\n"
            f"Пожалуйста, введите ровно {expected_count} ФИО ЧЕРЕЗ ЗАПЯТУЮ:"
        )
        return

    await state.update_data(clients=clients)

    clients_text = ", ".join(clients)
    await message.answer(
        TEXTS[language]["clients_saved"].format(clients_text=clients_text),
        reply_markup=get_clients_confirmation_kb(language)
    )
    await state.set_state(VoucherStates.waiting_for_clients_confirmation)

@dp.callback_query(F.data == "clients_correct")
async def confirm_clients(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')

    # Добавляем напоминание для английского языка

    await callback.message.answer(TEXTS[language]["enter_country"])
    await state.set_state(VoucherStates.waiting_for_country_1)
    await callback.answer()

@dp.callback_query(F.data == "clients_edit")
async def edit_clients(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')

    clients_text = "👥 Введите имена клиентов через запятую:" if language == "ru" else "👥 Enter client names separated by comma:"
    await callback.message.answer(clients_text)
    await state.set_state(VoucherStates.waiting_for_clients)
    await callback.answer()

# === ОБРАБОТЧИКИ ДЛЯ ДАННЫХ СТРАНЫ 1 ===
@dp.message(VoucherStates.waiting_for_country_1)
async def process_country_1(message: Message, state: FSMContext):
    await state.update_data(country_1=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')

    # Добавляем пример для английского языка
    if language == "en":
        await message.answer(f"{TEXTS[language]['enter_city']}\n")
    else:
        await message.answer(TEXTS[language]["enter_city"])
    await state.set_state(VoucherStates.waiting_for_city_1)

@dp.message(VoucherStates.waiting_for_city_1)
async def process_city_1(message: Message, state: FSMContext):
    await state.update_data(city_1=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')

    if language == "en":
        await message.answer(f"{TEXTS[language]['enter_hotel']}\n ")
    else:
        await message.answer(TEXTS[language]["enter_hotel"])
    await state.set_state(VoucherStates.waiting_for_hotel_1)

@dp.message(VoucherStates.waiting_for_hotel_1)
async def process_hotel_1(message: Message, state: FSMContext):
    await state.update_data(hotel_1=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')

    if language == "en":
        await message.answer(f"{TEXTS[language]['enter_dates']}\n")
    else:
        await message.answer(TEXTS[language]["enter_dates"])
    await state.set_state(VoucherStates.waiting_for_dates_1)

@dp.message(VoucherStates.waiting_for_dates_1)
async def process_dates_1(message: Message, state: FSMContext):
    await state.update_data(dates_1=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')

    if language == "en":
        await message.answer(f"{TEXTS[language]['enter_stay']}\n")
    else:
        await message.answer(TEXTS[language]["enter_stay"])
    await state.set_state(VoucherStates.waiting_for_stay_1)

@dp.message(VoucherStates.waiting_for_stay_1)
async def process_stay_1(message: Message, state: FSMContext):
    await state.update_data(stay_1=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')

    if language == "en":
        await message.answer(f"{TEXTS[language]['enter_roomcat']}\n")
    else:
        await message.answer(TEXTS[language]["enter_roomcat"])
    await state.set_state(VoucherStates.waiting_for_roomcat_1)

@dp.message(VoucherStates.waiting_for_roomcat_1)
async def process_roomcat_1(message: Message, state: FSMContext):
    await state.update_data(roomcat_1=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')

    if language == "en":
        await message.answer(f"{TEXTS[language]['enter_meals']}\n")
    else:
        await message.answer(TEXTS[language]["enter_meals"])
    await state.set_state(VoucherStates.waiting_for_meals_1)

@dp.message(VoucherStates.waiting_for_meals_1)
async def process_meals_1(message: Message, state: FSMContext):
    await state.update_data(meals_1=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')

    # ДОБАВЛЕНО: Запрос номера бронирования
    if language == "en":
        await message.answer(f"{TEXTS[language]['enter_booking']}\n")
    else:
        await message.answer(TEXTS[language]["enter_booking"])
    await state.set_state(VoucherStates.waiting_for_booking_1)

@dp.message(VoucherStates.waiting_for_booking_1)
async def process_booking_1(message: Message, state: FSMContext):
    await state.update_data(booking_1=message.text.strip())

    data = await state.get_data()
    countries_count = data.get('countries_count', 1)
    language = data.get('language', 'ru')

    if countries_count == 2:
        # Добавляем напоминание для английского языка
        await message.answer(TEXTS[language]["enter_country"])
        await state.set_state(VoucherStates.waiting_for_country_2)
    else:
        user_services[message.from_user.id] = set()
        await message.answer(
            TEXTS[language]["choose_services"],
            reply_markup=get_services_kb(message.from_user.id, language)
        )
        await state.set_state(VoucherStates.waiting_for_services_selection)

# === ОБРАБОТЧИКИ ДЛЯ ДАННЫХ СТРАНЫ 2 ===
@dp.message(VoucherStates.waiting_for_country_2)
async def process_country_2(message: Message, state: FSMContext):
    country2 = message.text.strip()
    await state.update_data(country_2=country2)

    data = await state.get_data()
    language = data.get('language', 'ru')

    if language == "en":
        await message.answer(
            f"🔹 Country 2: {country2}\n"
            f"{TEXTS[language]['enter_city']}"
        )
    else:
        await message.answer(
            f"🔹 Страна 2: {country2}\n"
            f"{TEXTS[language]['enter_city']}"
        )
    await state.set_state(VoucherStates.waiting_for_city_2)


@dp.message(VoucherStates.waiting_for_city_2)
async def process_city_2(message: Message, state: FSMContext):
    await state.update_data(city_2=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')
    country2 = data.get('country_2', '')

    if language == "en":
        await message.answer(
            f"🔹 Country 2: {country2}\n"
            f"{TEXTS[language]['enter_hotel']}"
        )
    else:
        await message.answer(
            f"🔹 Страна 2: {country2}\n"
            f"{TEXTS[language]['enter_hotel']}"
        )
    await state.set_state(VoucherStates.waiting_for_hotel_2)


@dp.message(VoucherStates.waiting_for_hotel_2)
async def process_hotel_2(message: Message, state: FSMContext):
    await state.update_data(hotel_2=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')
    country2 = data.get('country_2', '')

    if language == "en":
        await message.answer(
            f"🔹 Country 2: {country2}\n"
            f"{TEXTS[language]['enter_dates']}"
        )
    else:
        await message.answer(
            f"🔹 Страна 2: {country2}\n"
            f"{TEXTS[language]['enter_dates']}"
        )
    await state.set_state(VoucherStates.waiting_for_dates_2)


@dp.message(VoucherStates.waiting_for_dates_2)
async def process_dates_2(message: Message, state: FSMContext):
    await state.update_data(dates_2=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')
    country2 = data.get('country_2', '')

    if language == "en":
        await message.answer(
            f"🔹 Country 2: {country2}\n"
            f"{TEXTS[language]['enter_stay']}"
        )
    else:
        await message.answer(
            f"🔹 Страна 2: {country2}\n"
            f"{TEXTS[language]['enter_stay']}"
        )
    await state.set_state(VoucherStates.waiting_for_stay_2)


@dp.message(VoucherStates.waiting_for_stay_2)
async def process_stay_2(message: Message, state: FSMContext):
    await state.update_data(stay_2=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')
    country2 = data.get('country_2', '')

    if language == "en":
        await message.answer(
            f"🔹 Country 2: {country2}\n"
            f"{TEXTS[language]['enter_roomcat']}"
        )
    else:
        await message.answer(
            f"🔹 Страна 2: {country2}\n"
            f"{TEXTS[language]['enter_roomcat']}"
        )
    await state.set_state(VoucherStates.waiting_for_roomcat_2)


@dp.message(VoucherStates.waiting_for_roomcat_2)
async def process_roomcat_2(message: Message, state: FSMContext):
    await state.update_data(roomcat_2=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')
    country2 = data.get('country_2', '')

    if language == "en":
        await message.answer(
            f"🔹 Country 2: {country2}\n"
            f"{TEXTS[language]['enter_meals']}"
        )
    else:
        await message.answer(
            f"🔹 Страна 2: {country2}\n"
            f"{TEXTS[language]['enter_meals']}"
        )
    await state.set_state(VoucherStates.waiting_for_meals_2)


@dp.message(VoucherStates.waiting_for_meals_2)
async def process_meals_2(message: Message, state: FSMContext):
    await state.update_data(meals_2=message.text.strip())

    data = await state.get_data()
    language = data.get('language', 'ru')
    country2 = data.get('country_2', '')

    # Запрос номера бронирования для страны 2
    if language == "en":
        await message.answer(
            f"🔹 Country 2: {country2}\n"
            f"{TEXTS[language]['enter_booking']}"
        )
    else:
        await message.answer(
            f"🔹 Страна 2: {country2}\n"
            f"{TEXTS[language]['enter_booking']}"
        )
    await state.set_state(VoucherStates.waiting_for_booking_2)


@dp.message(VoucherStates.waiting_for_booking_2)
async def process_booking_2(message: Message, state: FSMContext):
    await state.update_data(booking_2=message.text.strip())

    user_services[message.from_user.id] = set()
    data = await state.get_data()
    language = data.get('language', 'ru')

    await message.answer(
        TEXTS[language]["choose_services"],
        reply_markup=get_services_kb(message.from_user.id, language)
    )
    await state.set_state(VoucherStates.waiting_for_services_selection)

# === ОБРАБОТЧИКИ СЕРВИСОВ (остаются без изменений, но с поддержкой языка) ===
@dp.callback_query(F.data.startswith("service_toggle:"))
async def toggle_service(callback: CallbackQuery, state: FSMContext):
    service_type = callback.data.split(":")[1]
    user_id = callback.from_user.id

    if user_id not in user_services:
        user_services[user_id] = set()

    if service_type in user_services[user_id]:
        user_services[user_id].remove(service_type)
    else:
        user_services[user_id].add(service_type)

    data = await state.get_data()
    language = data.get('language', 'ru')

    await callback.message.edit_reply_markup(reply_markup=get_services_kb(user_id, language))
    await callback.answer()

@dp.callback_query(F.data == "services_confirm")
async def confirm_services(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected_services = user_services.get(user_id, set())

    if not selected_services:
        await callback.answer("❌ Выберите хотя бы один сервис!")
        return

    await state.update_data(selected_services=list(selected_services))
    await process_next_service(callback, state)
    await callback.answer()

@dp.callback_query(F.data == "services_none")
async def skip_services(callback: CallbackQuery, state: FSMContext):
    await state.update_data(selected_services=[])
    await save_and_preview_data(callback.message, state)
    await callback.answer()

async def process_next_service(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_services = data.get('selected_services', [])
    language = data.get('language', 'ru')

    service_order = ['guide', 'transfer', 'excursions', 'extra']

    for service in service_order:
        if service in selected_services and f'service_{service}' not in data:
            await ask_service_info(callback.message, state, service, language)
            return

    await save_and_preview_data(callback.message, state)

async def ask_service_info(message: Message, state: FSMContext, service_type: str, language: str):
    service_prompts = {
        'guide': TEXTS[language]["enter_guide"],
        'transfer': TEXTS[language]["enter_transfer"],
        'excursions': TEXTS[language]["enter_excursions"],
        'extra': TEXTS[language]["enter_extra"]
    }

    # Добавляем примеры для английского языка
    if language == "en":
        examples = {
            'guide': TEXTS[language]["guide_example"],
            'transfer': TEXTS[language]["transfer_example"],
            'excursions': TEXTS[language]["excursions_example"],
            'extra': TEXTS[language]["extra_example"]
        }
        await message.answer(f"{service_prompts[service_type]}\n💡 {examples[service_type]}")
    else:
        await message.answer(service_prompts[service_type])

    state_mapping = {
        'guide': VoucherStates.waiting_for_guide_info,
        'transfer': VoucherStates.waiting_for_transfer_info,
        'excursions': VoucherStates.waiting_for_excursions_info,
        'extra': VoucherStates.waiting_for_extra_info
    }

    await state.set_state(state_mapping[service_type])

@dp.message(VoucherStates.waiting_for_guide_info)
async def process_guide_info(message: Message, state: FSMContext):
    await state.update_data(service_guide=message.text.strip())
    await process_next_service_after_input(message, state)

@dp.message(VoucherStates.waiting_for_transfer_info)
async def process_transfer_info(message: Message, state: FSMContext):
    await state.update_data(service_transfer=message.text.strip())
    await process_next_service_after_input(message, state)

@dp.message(VoucherStates.waiting_for_excursions_info)
async def process_excursions_info(message: Message, state: FSMContext):
    await state.update_data(service_excursions=message.text.strip())
    await process_next_service_after_input(message, state)

@dp.message(VoucherStates.waiting_for_extra_info)
async def process_extra_info(message: Message, state: FSMContext):
    await state.update_data(service_extra=message.text.strip())
    await process_next_service_after_input(message, state)

async def process_next_service_after_input(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_services = data.get('selected_services', [])
    language = data.get('language', 'ru')

    service_order = ['guide', 'transfer', 'excursions', 'extra']
    remaining_services = []

    for service in service_order:
        if service in selected_services and f'service_{service}' not in data:
            remaining_services.append(service)

    if remaining_services:
        await ask_service_info(message, state, remaining_services[0], language)
    else:
        await save_and_preview_data(message, state)

# === СОХРАНЕНИЕ И ПРЕВЬЮ ===
async def save_and_preview_data(message: Message, state: FSMContext):
    """Сохраняет данные и показывает превью"""
    data = await state.get_data()

    # Для одной страны копируем данные из полей _1 в поля без суффиксов
    countries_count = data.get('countries_count', 1)
    if countries_count == 1:
        for field in ["country", "city", "hotel", "dates", "stay", "roomcat", "meals", "booking"]:
            field_with_suffix = f"{field}_1"
            if field_with_suffix in data and data[field_with_suffix]:
                data[field] = data[field_with_suffix]

    # Определяем сценарий
    scenario_id = determine_scenario(data)
    data['scenario_id'] = scenario_id

    # Очищаем временные данные сервисов
    user_id = message.from_user.id
    if user_id in user_services:
        del user_services[user_id]

    # Создаем cache_id и сохраняем в кэш
    cache_id = str(uuid.uuid4())[:8]
    VOUCHER_CACHE[cache_id] = data

    # Показываем превью
    preview_text = generate_preview(data)
    language = data.get('language', 'ru')

    await message.answer(
        f"{TEXTS[language]['data_saved']}\n\n{preview_text}",
        reply_markup=get_edit_kb(cache_id)
    )
    await state.clear()

def determine_scenario(data: dict) -> int:
    countries_count = data.get('countries_count', 1)
    selected_services = data.get('selected_services', [])
    service_count = len(selected_services)

    if countries_count == 1:
        return min(service_count + 1, 5)
    else:
        return min(service_count + 6, 10)

def generate_preview(data: dict) -> str:
    clients = data.get('clients', [])
    scenario_id = data.get('scenario_id', 1)
    manager_key = data.get('manager_key', 'khadidzha')
    countries_count = data.get('countries_count', 1)
    language = data.get('language', 'ru')

    language_names = {
        'ru': '🇷🇺 Русский',
        'en': '🇬🇧 English'
    }

    clients_text = "\n".join([f"• {client}" for client in clients])

    preview = (
        f"📋 Сценарий {scenario_id}: {SCENARIOS[scenario_id]['name']}\n"
        f"🌐 Язык: {language_names.get(language, 'Русский')}\n"
        f"👨‍💼 Менеджер: {manager_key}\n\n"
        f"👥 Клиенты:\n{clients_text}\n\n"
    )

    for i in range(1, countries_count + 1):
        preview += f"🏨 Данные страны {i}:\n"
        preview += f"• Страна: {data.get(f'country_{i}', '—')}\n"
        preview += f"• Город: {data.get(f'city_{i}', '—')}\n"
        preview += f"• Отель: {data.get(f'hotel_{i}', '—')}\n"
        preview += f"• Даты: {data.get(f'dates_{i}', '—')}\n"
        preview += f"• Размещение: {data.get(f'stay_{i}', '—')}\n"
        preview += f"• Категория: {data.get(f'roomcat_{i}', '—')}\n"
        preview += f"• Питание: {data.get(f'meals_{i}', '—')}\n"
        preview += f"• Бронирование: {data.get(f'booking_{i}', '—')}\n\n"

    services_text = ""
    service_order = ['guide', 'transfer', 'excursions', 'extra']
    service_names = {
        'guide': '🧑‍💼 Гид',
        'transfer': '🚗 Трансфер',
        'excursions': '🏛️ Экскурсии',
        'extra': '📞 Доп. контакт'
    }

    for service in service_order:
        if data.get(f'service_{service}'):
            services_text += f"• {service_names[service]}: {data[f'service_{service}']}\n"

    if services_text:
        preview += f"🔧 Сервисы:\n{services_text}"
    else:
        preview += "🔧 Сервисы: не выбраны"

    return preview

# === ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ ВАУЧЕРА (остаются без изменений) ===
def _autocrop_alpha(im):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    bbox = im.split()[-1].getbbox()
    return im.crop(bbox) if bbox else im

def _paste_text_like(img_bg, asset, box, pad=(10,10,10,10)):
    x1,y1,x2,y2 = box
    L,T,R,B = pad
    W = max(1, (x2-x1) - L - R)
    H = max(1, (y2-y1) - T - B)

    asset = _autocrop_alpha(asset)
    k = min(W/asset.width, H/asset.height)
    new_size = (max(1,int(asset.width*k)), max(1,int(asset.height*k)))
    asset = asset.resize(new_size, Image.Resampling.LANCZOS)

    ax = x1 + L
    ay = y1 + T + (H - asset.height)//2
    img_bg.paste(asset, (ax, ay), asset)
    return img_bg

def generate_voucher_image(data: dict) -> str:
    """Функция генерации ваучера с поддержкой языков"""
    try:
        scenario_id = data.get('scenario_id', 1)
        language = data.get('language', 'ru')

        # Получаем путь к фону для выбранного языка
        bg_path = get_scenario_path(language, scenario_id)

        if not os.path.exists(bg_path):
            print(f"❌ Фон не найден: {bg_path}")
            # Пробуем найти на другом языке
            fallback_lang = 'en' if language == 'ru' else 'ru'
            fallback_path = get_scenario_path(fallback_lang, scenario_id)

            if os.path.exists(fallback_path):
                bg_path = fallback_path
                print(f"🔄 Используем фон на языке {fallback_lang}: {bg_path}")
            else:
                # Пробуем найти любой доступный фон
                for sc_id in range(1, 11):
                    for lang in ['ru', 'en']:
                        test_path = get_scenario_path(lang, sc_id)
                        if os.path.exists(test_path):
                            bg_path = test_path
                            scenario_id = sc_id
                            data['scenario_id'] = scenario_id
                            print(f"🔄 Используем сценарий {sc_id} на языке {lang}: {bg_path}")
                            break
                    else:
                        continue
                    break
                else:
                    print("❌ Не найден ни один фон!")
                    return None

        img = Image.open(bg_path).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Шрифты
        font_large = ImageFont.truetype(FORUM_TTF, 61)
        font_medium = ImageFont.truetype(FORUM_TTF, 68)
        font_small = ImageFont.truetype(FORUM_TTF, 65)

        coords_dict = globals().get(f"COORDS_SCENARIO_{scenario_id}", COORDS_SCENARIO_1)

        def draw_in_box(key_box, text, font):
            x1, y1, _, _ = key_box
            draw.text((x1 + 10, y1 + 10), text, font=font, fill=(0, 0, 0))

        # Клиенты
        if "clients" in coords_dict and "clients" in data:
            client_box = coords_dict["clients"]
            line_height = 70
            y = client_box[1] + 10
            for client in data["clients"]:
                line = client.upper()
                text_width = draw.textlength(line, font=font_large)
                x = client_box[2] - text_width - 20
                draw.text((x, y), line, font=font_large, fill=(0, 0, 0))
                y += line_height

        # Данные отелей (включая бронирование)
        has_multi = any(k.endswith("_1") for k in coords_dict.keys())

        if not has_multi:
            for field in ["country", "city", "hotel", "dates", "stay", "roomcat", "meals", "booking"]:
                field_value = data.get(field) or data.get(f"{field}_1")
                if field in coords_dict and field_value:
                    draw_in_box(coords_dict[field], field_value, font_medium)
        else:
            def draw_country_block(suffix: str):
                mapping = {
                    "country": f"country_{suffix}",
                    "city":    f"city_{suffix}",
                    "hotel":   f"hotel_{suffix}",
                    "dates":   f"dates_{suffix}",
                    "stay":    f"stay_{suffix}",
                    "roomcat": f"roomcat_{suffix}",
                    "meals":   f"meals_{suffix}",
                    "booking": f"booking_{suffix}",
                }
                for base, with_suf in mapping.items():
                    if with_suf in coords_dict and data.get(with_suf):
                        draw_in_box(coords_dict[with_suf], data[with_suf], font_medium)

            draw_country_block("1")
            draw_country_block("2")

        # Сервисы
        def draw_service_line_aligned(label_coords, value_coords, label_text, value_text, font):
            label_x = label_coords[0] + 10
            label_y = label_coords[1] + 10
            draw.text((label_x, label_y), label_text, font=font, fill=(0, 0, 0))

            label_width = draw.textlength(label_text, font=font)
            value_start_x = label_x + label_width + 40
            draw.text((value_start_x, label_y), value_text, font=font, fill=(0, 0, 0))

        service_order = ['guide', 'transfer', 'excursions', 'extra']
        service_index = 1

        for service in service_order:
            service_data = data.get(f'service_{service}')
            if service_data:
                label_key = f"service_label{'' if service_index == 1 else service_index}"
                value_key = f"service_value{'' if service_index == 1 else service_index}"

                if label_key in coords_dict and value_key in coords_dict:
                    service_name = {
                        'guide': 'Гид:',
                        'transfer': 'Трансфер:',
                        'excursions': 'Экскурсии:',
                        'extra': 'Доп. контакт:'
                    }.get(service, service)

                    draw_service_line_aligned(
                        coords_dict[label_key],
                        coords_dict[value_key],
                        service_name,
                        service_data,
                        font_small
                    )
                    service_index += 1

        # Менеджер
        if "manager_name" in coords_dict and "manager_phone" in coords_dict:
            manager_key = data.get('manager_key', 'khadidzha')
            img = insert_manager_assets(img, manager_key,
                                        coords_dict["manager_name"],
                                        coords_dict["manager_phone"])

        filename = f"voucher_{uuid.uuid4().hex[:8]}.png"
        img.save(filename, "PNG")
        print(f"✅ Ваучер сгенерирован: {filename}")
        return filename

    except Exception as e:
        print(f"❌ Ошибка генерации ваучера: {e}")
        import traceback
        traceback.print_exc()
        return None

def insert_manager_assets(img, manager_key, name_coords, phone_coords):
    try:
        fallback_manager = list(MANAGER_ASSETS.keys())[0]
        m = MANAGER_ASSETS.get(manager_key, MANAGER_ASSETS[fallback_manager])

        if os.path.exists(m["name"]):
            name_img = Image.open(m["name"]).convert("RGBA")
            img = _paste_text_like(img, name_img, name_coords, pad=(10, 10, 10, 10))

        if os.path.exists(m["phone"]):
            phone_img = Image.open(m["phone"]).convert("RGBA")
            img = _paste_text_like(img, phone_img, phone_coords, pad=(6, 4, 6, 4))

        return img
    except Exception as e:
        print(f"❌ Ошибка при вставке менеджера: {e}")
        return img

def create_clickable_pdf(image_path, scenario_id, output_path=None):
    """Создает PDF с кликабельными ссылками"""
    try:
        if output_path is None:
            output_path = f"voucher_scenario_{scenario_id}_{uuid.uuid4().hex[:8]}.pdf"

        c = canvas.Canvas(output_path, pagesize=A4)

        img = Image.open(image_path)
        img_width, img_height = img.size

        page_width, page_height = A4
        scale = min(page_width / img_width, page_height / img_height)
        new_width = img_width * scale
        new_height = img_height * scale

        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2

        c.drawImage(image_path, x, y, new_width, new_height)

        link_zones = LINK_ZONES.get(scenario_id, LINK_ZONES.get("default", {}))

        for link_type, zone_coords in link_zones.items():
            if link_type in LINKS:
                x1, y1, x2, y2 = zone_coords

                pdf_x1 = x + (x1 * scale)
                pdf_y1 = y + (img_height * scale) - (y2 * scale)
                pdf_x2 = x + (x2 * scale)
                pdf_y2 = y + (img_height * scale) - (y1 * scale)

                c.linkURL(
                    LINKS[link_type],
                    (pdf_x1, pdf_y1, pdf_x2, pdf_y2),
                    relative=0,
                    thickness=0
                )

        c.save()
        print(f"✅ PDF с ссылками создан: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Ошибка при создании PDF: {e}")
        return None

def png_to_pdf_with_links(png_path: str, scenario_id: int) -> str:
    """Конвертирует PNG в PDF с кликабельными ссылками"""
    try:
        pdf_path = create_clickable_pdf(png_path, scenario_id)
        return pdf_path
    except Exception as e:
        print(f"❌ Ошибка создания PDF с ссылками: {e}")
        return None

@dp.callback_query(F.data.startswith("generate:"))
async def generate_voucher(callback: CallbackQuery):
    cache_id = callback.data.split(":")[1]
    data = VOUCHER_CACHE.get(cache_id)

    if not data:
        await callback.message.answer("❌ Данные не найдены.")
        await callback.answer()
        return

    language = data.get('language', 'ru')

    await callback.message.answer(TEXTS[language]["generating"])

    image_path = generate_voucher_image(data)

    if not image_path or not os.path.exists(image_path):
        await callback.message.answer("❌ Ошибка при генерации изображения ваучера.")
        await callback.answer()
        return

    try:
        scenario_id = data.get('scenario_id', 1)
        pdf_path = png_to_pdf_with_links(image_path, scenario_id)

        if not pdf_path or not os.path.exists(pdf_path):
            await callback.message.answer("❌ Ошибка при создании PDF.")
            try:
                os.remove(image_path)
            except:
                pass
            await callback.answer()
            return

        with open(pdf_path, "rb") as f:
            buf = BufferedInputFile(f.read(), filename="voucher_amal.pdf")

        await callback.message.answer_document(
            buf,
            caption=TEXTS[language]["voucher_ready"],
            reply_markup=get_new_voucher_kb()
        )

        try:
            os.remove(image_path)
        except:
            pass
        try:
            os.remove(pdf_path)
        except:
            pass

        if cache_id in VOUCHER_CACHE:
            del VOUCHER_CACHE[cache_id]

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")
    finally:
        await callback.answer()

# === ОБРАБОТЧИКИ КНОПОК НАЗАД ===
@dp.callback_query(F.data == "back_to_managers")
async def back_to_managers(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        TEXTS["ru"]["choose_manager"],
        reply_markup=get_managers_kb()
    )
    await state.set_state(VoucherStates.waiting_for_manager)
    await callback.answer()

@dp.callback_query(F.data == "back_to_language")
async def back_to_language(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')

    await callback.message.answer(
        TEXTS[language]["choose_language"],
        reply_markup=get_language_kb()
    )
    await state.set_state(VoucherStates.waiting_for_language)
    await callback.answer()

@dp.callback_query(F.data == "back_to_countries")
async def back_to_countries(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')

    await callback.message.answer(
        TEXTS[language]["choose_countries"],
        reply_markup=get_countries_count_kb(language)
    )
    await state.set_state(VoucherStates.waiting_for_countries_count)
    await callback.answer()

@dp.callback_query(F.data == "back_to_clients_count")
async def back_to_clients_count(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'ru')

    await callback.message.answer(
        TEXTS[language]["choose_clients_count"],
        reply_markup=get_clients_count_kb(language)
    )
    await state.set_state(VoucherStates.waiting_for_clients_count)
    await callback.answer()

@dp.callback_query(F.data == "back_to_meals")
async def back_to_meals(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    countries_count = data.get('countries_count', 1)
    language = data.get('language', 'ru')

    if countries_count == 2:
        await callback.message.answer(TEXTS[language]["enter_meals"])
        await state.set_state(VoucherStates.waiting_for_meals_2)
    else:
        await callback.message.answer(TEXTS[language]["enter_meals"])
        await state.set_state(VoucherStates.waiting_for_meals_1)
    await callback.answer()


# === ЗАПУСК БОТА ===
async def main():
    print("✅ Бот AMAL запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())