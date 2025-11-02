import os
import re
import uuid
import asyncio
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
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

from aiogram import Bot
bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

Image.MAX_IMAGE_PIXELS = None
FORUM_TTF = os.path.expanduser("Forum-Regular.ttf")

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
SCENARIOS = {
    1: {"name": "Превью вашего ваучера", "bg_path": "scen/scen1.png"},
    2: {"name": "Превью вашего ваучера", "bg_path": "scen/scen2.png"},
    3: {"name": "Превью вашего ваучера", "bg_path": "scen/scen3.png"},
    4: {"name": "Превью вашего ваучера", "bg_path": "scen/scen4.png"},
    5: {"name": "Превью вашего ваучера", "bg_path": "scen/scen5.png"},
    6: {"name": "Превью вашего ваучера", "bg_path": "scen/scen6.png"},
    7: {"name": "Превью вашего ваучера", "bg_path": "scen/scen7.png"},
    8: {"name": "Превью вашего ваучера", "bg_path": "scen/scen8.png"},
    9: {"name": "Превью вашего ваучера", "bg_path": "scen/scen9.png"},
    10: {"name": "Превью вашего ваучера", "bg_path": "scen/scen10.png"},
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
    "clients": (1480, 738, 2303, 995),
    "country": (1025, 1283, 1733, 1382),
    "city": (1025, 1401, 1326, 1500),
    "hotel": (1025, 1520, 1819, 1619),
    "dates": (1025, 1639, 1368, 1738),
    "stay": (1025, 1758, 1422, 1857),
    "roomcat": (1025, 1867, 1541, 1966),
    "meals": (1025, 1986, 1461, 2085),
    "service_label": (212, 2296, 373, 2383),
    "service_value": (426, 2296, 1434, 2383),
    "service_label2": (212, 2407, 548, 2494),
    "service_value2": (623, 2407, 1156, 2506),
    "service_label3": (212, 2519, 612, 2607),
    "service_value3": (623, 2523, 1141, 2610),
    "manager_name": (998, 2710, 1913, 2870),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_5 = {
    "clients": (1480, 738, 2303, 995),
    "country": (1025, 1283, 1733, 1382),
    "city": (1025, 1401, 1326, 1500),
    "hotel": (1025, 1520, 1819, 1619),
    "dates": (1025, 1639, 1368, 1738),
    "stay": (1025, 1758, 1422, 1857),
    "roomcat": (1025, 1867, 1541, 1966),
    "meals": (1025, 1986, 1461, 2085),
    "service_label": (216, 2219, 376, 2306),
    "service_value": (406, 2218, 1412, 2306),
    "service_label2": (216, 2324, 464, 2411),
    "service_value2": (523, 2328, 1529, 2415),
    "service_label3": (216, 2423, 541, 2510),
    "service_value3": (581, 2437, 1114, 2524),
    "service_label4": (216, 2535, 616, 2622),
    "service_value4": (611, 2539, 1129, 2616),
    "manager_name": (998, 2710, 1913, 2870),
    "manager_phone": (1936, 2855, 2283, 2946)
}

COORDS_SCENARIO_6 = {
    "clients": (1501, 558, 2336, 787),
    "country_1": (959, 1010, 1590, 1095),
    "city_1": (959, 1116, 1227, 1201),
    "hotel_1": (959, 1221, 1667, 1309),
    "dates_1": (959, 1327, 1265, 1415),
    "stay_1": (959, 1433, 1313, 1513),
    "roomcat_1": (959, 1530, 1419, 1615),
    "meals_1": (959, 1636, 1347, 1724),
    "country_2": (959, 1855, 1591, 1943),
    "city_2": (959, 1961, 1227, 2050),
    "hotel_2": (959, 2067, 1667, 2155),
    "dates_2": (959, 2173, 1265, 2261),
    "stay_2": (959, 2279, 1312, 2359),
    "roomcat_2": (959, 2376, 1419, 2464),
    "meals_2": (959, 2482, 1347, 2570),
    "manager_name": (1022, 2812, 1903, 2965),
    "manager_phone": (1966, 2988, 2315, 3081),
}

COORDS_SCENARIO_7 = {
    "clients": (1501, 470, 2336, 700),
    "country_1": (959, 861, 1591, 949),
    "city_1": (959, 966, 1228, 1055),
    "hotel_1": (959, 1073, 1668, 1161),
    "dates_1": (959, 1179, 1266, 1276),
    "stay_1": (959, 1284, 1314, 1364),
    "roomcat_1": (959, 1382, 1419, 1470),
    "meals_1": (959, 1488, 1347, 1575),
    "country_2": (959, 1643, 1591, 1731),
    "city_2": (959, 1749, 1227, 1837),
    "hotel_2": (959, 1854, 1668, 1942),
    "dates_2": (959, 1960, 1265, 2048),
    "stay_2": (959, 2066, 1312, 2146),
    "roomcat_2": (959, 2164, 1419, 2252),
    "meals_2": (959, 2270, 1347, 2358),
    "service_label": (271, 2524, 917, 2611),
    "service_value": (1153, 2524, 1673, 2611),
    "manager_name": (1022, 2812, 1903, 2965),
    "manager_phone": (1966, 2988, 2315, 3081),
}

COORDS_SCENARIO_8 = {
    "clients": (1481, 421, 2302, 646),
    "country_1": (959, 794, 1579, 881),
    "city_1": (959, 898, 1223, 985),
    "hotel_1": (959, 1002, 1654, 1089),
    "dates_1": (959, 1106, 1260, 1193),
    "stay_1": (959, 1210, 1306, 1287),
    "roomcat_1": (959, 1305, 1405, 1392),
    "meals_1": (959, 1410, 1335, 1496),
    "country_2": (959, 1601, 1579, 1688),
    "city_2": (959, 1705, 1223, 1792),
    "hotel_2": (959, 1809, 1654, 1896),
    "dates_2": (959, 1912, 1259, 2000),
    "stay_2": (959, 2017, 1307, 2095),
    "roomcat_2": (959, 2112, 1410, 2199),
    "meals_2": (959, 2216, 1340, 2303),
    "service_label": (213, 2467, 557, 2555),
    "service_value": (623, 2468, 1127, 2555),
    "service_label2": (213, 2567, 847, 2654),
    "service_value2": (954, 2567, 1960, 2654),
    "manager_name": (907, 2860, 1849, 3024),
    "manager_phone": (1916, 3048, 2289, 3147),
}

COORDS_SCENARIO_9 = {
    "clients": (1481, 421, 2302, 646),
    "country_1": (959, 794, 1579, 881),
    "city_1": (959, 898, 1223, 985),
    "hotel_1": (959, 1002, 1654, 1089),
    "dates_1": (959, 1106, 1260, 1193),
    "stay_1": (959, 1210, 1306, 1287),
    "roomcat_1": (959, 1305, 1405, 1392),
    "meals_1": (959, 1410, 1335, 1496),
    "country_2": (959, 1601, 1579, 1688),
    "city_2": (959, 1705, 1223, 1792),
    "hotel_2": (959, 1809, 1654, 1896),
    "dates_2": (959, 1912, 1259, 2000),
    "stay_2": (959, 2017, 1307, 2095),
    "roomcat_2": (959, 2112, 1410, 2199),
    "meals_2": (959, 2216, 1340, 2303),
    "service_label": (213, 2429, 373, 2516),
    "service_value": (427, 2429, 1433, 2516),
    "service_label2": (213, 2540, 556, 2627),
    "service_value2": (624, 2540, 1157, 2627),
    "service_label3": (213, 2652, 557, 2739),
    "service_value3": (624, 2652, 1143, 2739),
    "manager_name": (907, 2860, 1849, 3024),
    "manager_phone": (1916, 3048, 2289, 3147),
}

COORDS_SCENARIO_10 = {
    "clients": (1481, 360, 2301, 594),
    "country_1": (959, 737, 1579, 824),
    "city_1": (959, 848, 1223, 935),
    "hotel_1": (959, 947, 1654, 1034),
    "dates_1": (959, 1048, 1260, 1135),
    "stay_1": (959, 1151, 1306, 1229),
    "roomcat_1": (959, 1250, 1405, 1337),
    "meals_1": (959, 1356, 1335, 1443),
    "country_2": (959, 1494, 1579, 1581),
    "city_2": (959, 1598, 1223, 1685),
    "hotel_2": (959, 1702, 1654, 1789),
    "dates_2": (959, 1805, 1259, 1892),
    "stay_2": (959, 1909, 1307, 1987),
    "roomcat_2": (959, 2005, 1410, 2092),
    "meals_2": (959, 2109, 1340, 2196),
    "service_label": (265, 2339, 453, 2426),
    "service_value": (434, 2339, 733, 2426),
    "service_label2": (265, 2451, 614, 2537),
    "service_value2": (670, 2451, 1108, 2538),
    "service_label3": (265, 2564, 586, 2650),
    "service_value3": (633, 2564, 965, 2651),
    "service_label4": (265, 2681, 906, 2768),
    "service_value4": (928, 2681, 1260, 2768),
    "manager_name": (907, 2860, 1849, 3024),
    "manager_phone": (1916, 3048, 2289, 3147),
}

# === СОСТОЯНИЯ ===
class VoucherStates(StatesGroup):
    waiting_for_manager = State()
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
    waiting_for_country_2 = State()
    waiting_for_city_2 = State()
    waiting_for_hotel_2 = State()
    waiting_for_dates_2 = State()
    waiting_for_stay_2 = State()
    waiting_for_roomcat_2 = State()
    waiting_for_meals_2 = State()
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
            text=f"👨‍💼 {manager}",  # Убрали .capitalize()
            callback_data=f"manager:{manager}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_countries_count_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" 1 страна", callback_data="countries:1")],
        [InlineKeyboardButton(text=" 2 страны", callback_data="countries:2")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_managers")]
    ])

def get_clients_count_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 1 клиент", callback_data="clients:1")],
        [InlineKeyboardButton(text="👥 2 клиента", callback_data="clients:2")],
        [InlineKeyboardButton(text="👥 3 клиента", callback_data="clients:3")],
        [InlineKeyboardButton(text="👥 4 клиента", callback_data="clients:4")],
        [InlineKeyboardButton(text="👥 5+ клиентов", callback_data="clients:custom")],
        [InlineKeyboardButton(text="⬅️ Назад к странам", callback_data="back_to_countries")]
    ])

def get_clients_confirmation_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, всё верно", callback_data="clients_correct")],
        [InlineKeyboardButton(text="✏️ Нет, изменить имена", callback_data="clients_edit")],
        [InlineKeyboardButton(text="🔢 Изменить количество", callback_data="back_to_clients_count")]
    ])

@dp.callback_query(F.data == "back_to_clients_count")
async def back_to_clients_count(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "👥 Выберите количество клиентов:",
        reply_markup=get_clients_count_kb()
    )
    await state.set_state(VoucherStates.waiting_for_clients_count)
    await callback.answer()



def get_services_kb(user_id: int):
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
        buttons.append([InlineKeyboardButton(text="🚀 Продолжить с выбранными сервисами", callback_data="services_confirm")])

    buttons.append([InlineKeyboardButton(text="⏭️ Без сервисов", callback_data="services_none")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_meals")])

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
    """Клавиатура для создания нового ваучера"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Создать новый ваучер", callback_data="create_voucher")]
    ])


# === РЕДАКТИРОВАНИЕ ОСНОВНОЙ ЧАСТИ ===

def get_main_edit_kb(cache_id: str):
    """Клавиатура для редактирования основной части"""
    data = VOUCHER_CACHE.get(cache_id, {})
    countries_count = data.get('countries_count', 1)

    buttons = []

    if countries_count == 1:
        buttons.append([InlineKeyboardButton(text="🗺️ Изменить страну", callback_data=f"edit_main_field:{cache_id}:country_1")])
        buttons.append([InlineKeyboardButton(text="🏙️ Изменить город", callback_data=f"edit_main_field:{cache_id}:city_1")])
        buttons.append([InlineKeyboardButton(text="🏨 Изменить отель", callback_data=f"edit_main_field:{cache_id}:hotel_1")])
        buttons.append([InlineKeyboardButton(text="📅 Изменить даты", callback_data=f"edit_main_field:{cache_id}:dates_1")])
        buttons.append([InlineKeyboardButton(text="🛏️ Изменить размещение", callback_data=f"edit_main_field:{cache_id}:stay_1")])
        buttons.append([InlineKeyboardButton(text="⭐ Изменить категорию номера", callback_data=f"edit_main_field:{cache_id}:roomcat_1")])
        buttons.append([InlineKeyboardButton(text="🍽️ Изменить питание", callback_data=f"edit_main_field:{cache_id}:meals_1")])
    else:
        # Для двух стран показываем отдельно для каждой
        buttons.append([InlineKeyboardButton(text="🗺️ Изменить страну 1", callback_data=f"edit_main_field:{cache_id}:country_1")])
        buttons.append([InlineKeyboardButton(text="🏙️ Изменить город 1", callback_data=f"edit_main_field:{cache_id}:city_1")])
        buttons.append([InlineKeyboardButton(text="🏨 Изменить отель 1", callback_data=f"edit_main_field:{cache_id}:hotel_1")])
        buttons.append([InlineKeyboardButton(text="📅 Изменить даты 1", callback_data=f"edit_main_field:{cache_id}:dates_1")])
        buttons.append([InlineKeyboardButton(text="🛏️ Изменить размещение 1", callback_data=f"edit_main_field:{cache_id}:stay_1")])
        buttons.append([InlineKeyboardButton(text="⭐ Изменить категорию 1", callback_data=f"edit_main_field:{cache_id}:roomcat_1")])
        buttons.append([InlineKeyboardButton(text="🍽️ Изменить питание 1", callback_data=f"edit_main_field:{cache_id}:meals_1")])

        buttons.append([InlineKeyboardButton(text="🗺️ Изменить страну 2", callback_data=f"edit_main_field:{cache_id}:country_2")])
        buttons.append([InlineKeyboardButton(text="🏙️ Изменить город 2", callback_data=f"edit_main_field:{cache_id}:city_2")])
        buttons.append([InlineKeyboardButton(text="🏨 Изменить отель 2", callback_data=f"edit_main_field:{cache_id}:hotel_2")])
        buttons.append([InlineKeyboardButton(text="📅 Изменить даты 2", callback_data=f"edit_main_field:{cache_id}:dates_2")])
        buttons.append([InlineKeyboardButton(text="🛏️ Изменить размещение 2", callback_data=f"edit_main_field:{cache_id}:stay_2")])
        buttons.append([InlineKeyboardButton(text="⭐ Изменить категорию 2", callback_data=f"edit_main_field:{cache_id}:roomcat_2")])
        buttons.append([InlineKeyboardButton(text="🍽️ Изменить питание 2", callback_data=f"edit_main_field:{cache_id}:meals_2")])

    buttons.append([InlineKeyboardButton(text="🌍 Изменить количество стран", callback_data=f"edit_countries_count:{cache_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад к редактированию", callback_data=f"edit_back:{cache_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.callback_query(F.data.startswith("edit_main:"))
async def edit_main_start(callback: CallbackQuery, state: FSMContext):
    """Начало редактирования основной части"""
    cache_id = callback.data.split(":")[1]
    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        return

    data = VOUCHER_CACHE[cache_id]
    countries_count = data.get('countries_count', 1)

    # Показываем текущие данные
    preview_text = "📋 Текущие данные:\n\n"

    if countries_count == 1:
        preview_text += f"• Страна: {data.get('country_1', '—')}\n"
        preview_text += f"• Город: {data.get('city_1', '—')}\n"
        preview_text += f"• Отель: {data.get('hotel_1', '—')}\n"
        preview_text += f"• Даты: {data.get('dates_1', '—')}\n"
        preview_text += f"• Размещение: {data.get('stay_1', '—')}\n"
        preview_text += f"• Категория: {data.get('roomcat_1', '—')}\n"
        preview_text += f"• Питание: {data.get('meals_1', '—')}\n"
    else:
        preview_text += " Страна 1:\n"
        preview_text += f"• Страна: {data.get('country_1', '—')}\n"
        preview_text += f"• Город: {data.get('city_1', '—')}\n"
        preview_text += f"• Отель: {data.get('hotel_1', '—')}\n"
        preview_text += f"• Даты: {data.get('dates_1', '—')}\n"
        preview_text += f"• Размещение: {data.get('stay_1', '—')}\n"
        preview_text += f"• Категория: {data.get('roomcat_1', '—')}\n"
        preview_text += f"• Питание: {data.get('meals_1', '—')}\n\n"

        preview_text += " Страна 2:\n"
        preview_text += f"• Страна: {data.get('country_2', '—')}\n"
        preview_text += f"• Город: {data.get('city_2', '—')}\n"
        preview_text += f"• Отель: {data.get('hotel_2', '—')}\n"
        preview_text += f"• Даты: {data.get('dates_2', '—')}\n"
        preview_text += f"• Размещение: {data.get('stay_2', '—')}\n"
        preview_text += f"• Категория: {data.get('roomcat_2', '—')}\n"
        preview_text += f"• Питание: {data.get('meals_2', '—')}\n"

    await callback.message.edit_text(
        f"{preview_text}\nВыберите что хотите изменить:",
        reply_markup=get_main_edit_kb(cache_id)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_main_field:"))
async def edit_main_field(callback: CallbackQuery, state: FSMContext):
    """Редактирование конкретного поля основной части"""
    _, cache_id, field = callback.data.split(":")

    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        await callback.answer()
        return

    data = VOUCHER_CACHE[cache_id]
    current_value = data.get(field, "")

    field_names = {
        'country_1': 'страну', 'country_2': 'страну 2',
        'city_1': 'город', 'city_2': 'город 2',
        'hotel_1': 'отель', 'hotel_2': 'отель 2',
        'dates_1': 'даты', 'dates_2': 'даты 2',
        'stay_1': 'размещение', 'stay_2': 'размещение 2',
        'roomcat_1': 'категорию номера', 'roomcat_2': 'категорию номера 2',
        'meals_1': 'питание', 'meals_2': 'питание 2'
    }

    placeholders = {
        'country_1': 'Например: ОАЭ', 'country_2': 'Например: Турция',
        'city_1': 'Например: Дубай', 'city_2': 'Например: Стамбул',
        'hotel_1': 'Например: Burj Al Arab', 'hotel_2': 'Например: Four Seasons',
        'dates_1': 'Например: 15.12.2024 - 22.12.2024', 'dates_2': 'Например: 23.12.2024 - 30.12.2024',
        'stay_1': 'Например: Standard Room', 'stay_2': 'Например: Deluxe Suite',
        'roomcat_1': 'Например: 5*', 'roomcat_2': 'Например: 5*',
        'meals_1': 'Например: Завтрак', 'meals_2': 'Например: Все включено'
    }

    await callback.message.answer(
        f"✏️ Введите новое значение для {field_names.get(field, 'поля')}:\n\n"
        f"Текущее значение: {current_value or '—'}\n\n"
        f"💡 {placeholders.get(field, 'Введите значение')}"
    )

    await state.update_data(
        edit_cache_id=cache_id,
        edit_main_field=field
    )
    await state.set_state(EditVoucherStates.editing_hotel_country)  # Используем существующее состояние
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_countries_count:"))
async def edit_countries_count(callback: CallbackQuery, state: FSMContext):
    """Изменение количества стран"""
    cache_id = callback.data.split(":")[1]

    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        await callback.answer()
        return

    await callback.message.edit_text(
        "🌍 Выберите количество стран:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=" 1 страна", callback_data=f"set_countries:{cache_id}:1")],
            [InlineKeyboardButton(text=" 2 страны", callback_data=f"set_countries:{cache_id}:2")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"edit_main:{cache_id}")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("set_countries:"))
async def set_countries_count(callback: CallbackQuery, state: FSMContext):
    """Установка количества стран"""
    _, cache_id, count = callback.data.split(":")
    countries_count = int(count)

    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        await callback.answer()
        return

    data = VOUCHER_CACHE[cache_id]
    old_count = data.get('countries_count', 1)
    data['countries_count'] = countries_count

    # Если переключаем с 1 страны на 2, копируем данные в блок страны 2
    if old_count == 1 and countries_count == 2:
        for field in ['country', 'city', 'hotel', 'dates', 'stay', 'roomcat', 'meals']:
            if field in data:
                data[f"{field}_2"] = data[field]

    # Если переключаем с 2 стран на 1, очищаем данные страны 2
    elif old_count == 2 and countries_count == 1:
        for field in ['country', 'city', 'hotel', 'dates', 'stay', 'roomcat', 'meals']:
            data[f"{field}_2"] = ""

    VOUCHER_CACHE[cache_id] = data

    await callback.answer(f"✅ Установлено {countries_count} стран")
    await edit_main_start(callback, state)

@dp.callback_query(F.data.startswith("edit_back:"))
async def edit_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат к основному меню редактирования"""
    cache_id = callback.data.split(":")[1]
    await send_preview_for_cache(callback.message, cache_id)
    await callback.answer()

@dp.message(EditVoucherStates.editing_hotel_country)
async def edit_main_field_input(message: Message, state: FSMContext):
    """Обработка ввода значения для поля основной части"""
    data = await state.get_data()
    cache_id = data.get("edit_cache_id")
    field = data.get("edit_main_field")

    if not cache_id or cache_id not in VOUCHER_CACHE:
        await message.answer("❌ Ваучер не найден.")
        await state.clear()
        return

    if not field:
        await message.answer("❌ Ошибка: поле не указано.")
        await state.clear()
        return

    # Сохраняем значение
    VOUCHER_CACHE[cache_id][field] = message.text.strip()

    field_names = {
        'country_1': 'страны', 'country_2': 'страны 2',
        'city_1': 'города', 'city_2': 'города 2',
        'hotel_1': 'отеля', 'hotel_2': 'отеля 2',
        'dates_1': 'дат', 'dates_2': 'дат 2',
        'stay_1': 'размещения', 'stay_2': 'размещения 2',
        'roomcat_1': 'категории номера', 'roomcat_2': 'категории номера 2',
        'meals_1': 'питания', 'meals_2': 'питания 2'
    }

    await message.answer(f"✅ Значение {field_names.get(field, 'поля')} обновлено!")
    await state.clear()

    # Возвращаемся к редактированию основной части
    await edit_main_start_simple(message, cache_id)

async def edit_main_start_simple(message: Message, cache_id: str):
    """Показ меню редактирования основной части"""
    if cache_id not in VOUCHER_CACHE:
        await message.answer("❌ Ваучер не найден.")
        return

    data = VOUCHER_CACHE[cache_id]
    countries_count = data.get('countries_count', 1)

    preview_text = "📋 Текущие данные:\n\n"

    if countries_count == 1:
        preview_text += f"• Страна: {data.get('country_1', '—')}\n"
        preview_text += f"• Город: {data.get('city_1', '—')}\n"
        preview_text += f"• Отель: {data.get('hotel_1', '—')}\n"
        preview_text += f"• Даты: {data.get('dates_1', '—')}\n"
        preview_text += f"• Размещение: {data.get('stay_1', '—')}\n"
        preview_text += f"• Категория: {data.get('roomcat_1', '—')}\n"
        preview_text += f"• Питание: {data.get('meals_1', '—')}\n"
    else:
        preview_text += " Страна 1:\n"
        preview_text += f"• Страна: {data.get('country_1', '—')}\n"
        preview_text += f"• Город: {data.get('city_1', '—')}\n"
        preview_text += f"• Отель: {data.get('hotel_1', '—')}\n"
        preview_text += f"• Даты: {data.get('dates_1', '—')}\n"
        preview_text += f"• Размещение: {data.get('stay_1', '—')}\n"
        preview_text += f"• Категория: {data.get('roomcat_1', '—')}\n"
        preview_text += f"• Питание: {data.get('meals_1', '—')}\n\n"

        preview_text += " Страна 2:\n"
        preview_text += f"• Страна: {data.get('country_2', '—')}\n"
        preview_text += f"• Город: {data.get('city_2', '—')}\n"
        preview_text += f"• Отель: {data.get('hotel_2', '—')}\n"
        preview_text += f"• Даты: {data.get('dates_2', '—')}\n"
        preview_text += f"• Размещение: {data.get('stay_2', '—')}\n"
        preview_text += f"• Категория: {data.get('roomcat_2', '—')}\n"
        preview_text += f"• Питание: {data.get('meals_2', '—')}\n"

    await message.answer(
        f"{preview_text}\nВыберите что хотите изменить:",
        reply_markup=get_main_edit_kb(cache_id)
    )


# === ОСНОВНЫЕ ОБРАБОТЧИКИ ===
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "🕌 Ассаляму алейкум ва рахматуЛлахи ва баракятуху!\n\n"
        "Добро пожаловать в конструктор ваучеров AMAL!",
        reply_markup=get_main_menu_kb()
    )

@dp.callback_query(F.data == "create_voucher")
async def start_voucher_creation(callback: CallbackQuery, state: FSMContext):
    # Очищаем состояние на всякий случай
    await state.clear()

    # Очищаем сервисы пользователя если есть
    user_id = callback.from_user.id
    if user_id in user_services:
        del user_services[user_id]

    await callback.message.answer(
        "👨‍💼 Кто будет делать ваучер? Выберите менеджера:",
        reply_markup=get_managers_kb()
    )
    await state.set_state(VoucherStates.waiting_for_manager)
    await callback.answer("🚀 Начинаем создание нового ваучера!")

@dp.callback_query(F.data.startswith("manager:"))
async def process_manager_selection(callback: CallbackQuery, state: FSMContext):
    manager_key = callback.data.split(":")[1]
    await state.update_data(manager_key=manager_key)

    await callback.message.answer(
        "🌍 На сколько стран делаем ваучер?",
        reply_markup=get_countries_count_kb()
    )
    await state.set_state(VoucherStates.waiting_for_countries_count)
    await callback.answer()

@dp.callback_query(F.data.startswith("countries:"))
async def process_countries_count(callback: CallbackQuery, state: FSMContext):
    countries_count = int(callback.data.split(":")[1])
    await state.update_data(countries_count=countries_count)

    await callback.message.answer(
        "👥 На сколько клиентов делаем ваучер?",
        reply_markup=get_clients_count_kb()
    )
    await state.set_state(VoucherStates.waiting_for_clients_count)
    await callback.answer()

@dp.callback_query(F.data.startswith("clients:"))
async def process_clients_count(callback: CallbackQuery, state: FSMContext):
    clients_count = callback.data.split(":")[1]

    if clients_count == "custom":
        await callback.message.answer(
            "👥 Введите число клиентов (например: 6)"
        )
        await state.set_state(VoucherStates.waiting_for_clients_count)
    else:
        count = int(clients_count)

        # Примеры именно ЧЕРЕЗ ЗАПЯТУЮ
        if count == 1:
            example = "Имя Фамилия "
        elif count == 2:
            example = "Имя Фамилия 1, Имя Фамилия 2"
        else:
            example = "Имя Фамилия 1, Имя Фамилия 2, Имя Фамилия 3"

        await callback.message.answer(
            f"👥 Введите ФИО {count} клиента(ов) ЧЕРЕЗ ЗАПЯТУЮ.\n\n"
            f"📝 Пример: {example}"
        )
        await state.update_data(clients_count=count)
        await state.set_state(VoucherStates.waiting_for_clients)

    await callback.answer()


@dp.message(VoucherStates.waiting_for_clients)
async def handle_clients(message: Message, state: FSMContext):
    # Принимаем и запятую, и переносы строк — но подсказываем везде именно «через запятую»
    clients = [c.strip() for c in re.split(r'[,;\n]+', message.text) if c.strip()]

    if not clients:
        await message.answer("❌ Вы не ввели ни одного имени. Введите ФИО через запятую:")
        return

    data = await state.get_data()
    expected_count = data.get('clients_count')

    if expected_count and len(clients) != expected_count:
        await message.answer(
            f"❌ Количество не совпадает!\n"
            f"Вы выбрали: {expected_count}\n"
            f"Вы ввели: {len(clients)}\n\n"
            f"Пожалуйста, введите ровно {expected_count} ФИО ЧЕРЕЗ ЗАПЯТУЮ:"
        )
        return

    await state.update_data(clients=clients)

    clients_text = ", ".join(clients)  # показываем красиво в одну строку
    await message.answer(
        f"✅ Список клиентов сохранён!\n\n"
        f"👥 Проверьте: {clients_text}\n\n"
        f"Всё верно?",
        reply_markup=get_clients_confirmation_kb()
    )
    await state.set_state(VoucherStates.waiting_for_clients_confirmation)


@dp.message(VoucherStates.waiting_for_clients_count)
async def process_custom_clients_count(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        if count <= 0:
            await message.answer("❌ Число должно быть больше 0. Введите снова:")
            return

        await message.answer(
            f"👥 Введите ФИО {count} клиента(ов) ЧЕРЕЗ ЗАПЯТУЮ.\n\n"
            f"📝 Пример: Имя Фамилия 1, Имя Фамилия 2"
        )
        await state.update_data(clients_count=count)
        await state.set_state(VoucherStates.waiting_for_clients)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число:")



@dp.callback_query(F.data == "clients_correct")
async def confirm_clients(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🌍 Введите название страны:")
    await state.set_state(VoucherStates.waiting_for_country_1)
    await callback.answer()

@dp.callback_query(F.data == "clients_edit")
async def edit_clients(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("👥 Введите имена клиентов через запятую:")
    await state.set_state(VoucherStates.waiting_for_clients)
    await callback.answer()

# === ОБРАБОТЧИКИ ДЛЯ ДАННЫХ СТРАНЫ 1 ===
@dp.message(VoucherStates.waiting_for_country_1)
async def process_country_1(message: Message, state: FSMContext):
    await state.update_data(country_1=message.text.strip())
    await message.answer("🏙️ Введите город:")
    await state.set_state(VoucherStates.waiting_for_city_1)

@dp.message(VoucherStates.waiting_for_city_1)
async def process_city_1(message: Message, state: FSMContext):
    await state.update_data(city_1=message.text.strip())
    await message.answer("🏨 Введите название отеля:")
    await state.set_state(VoucherStates.waiting_for_hotel_1)

@dp.message(VoucherStates.waiting_for_hotel_1)
async def process_hotel_1(message: Message, state: FSMContext):
    await state.update_data(hotel_1=message.text.strip())
    await message.answer("📅 Введите даты пребывания:")
    await state.set_state(VoucherStates.waiting_for_dates_1)

@dp.message(VoucherStates.waiting_for_dates_1)
async def process_dates_1(message: Message, state: FSMContext):
    await state.update_data(dates_1=message.text.strip())
    await message.answer("🛏️ Введите тип размещения:")
    await state.set_state(VoucherStates.waiting_for_stay_1)

@dp.message(VoucherStates.waiting_for_stay_1)
async def process_stay_1(message: Message, state: FSMContext):
    await state.update_data(stay_1=message.text.strip())
    await message.answer("⭐ Введите категорию номера:")
    await state.set_state(VoucherStates.waiting_for_roomcat_1)

@dp.message(VoucherStates.waiting_for_roomcat_1)
async def process_roomcat_1(message: Message, state: FSMContext):
    await state.update_data(roomcat_1=message.text.strip())
    await message.answer("🍽️ Введите тип питания:")
    await state.set_state(VoucherStates.waiting_for_meals_1)

@dp.message(VoucherStates.waiting_for_meals_1)
async def process_meals_1(message: Message, state: FSMContext):
    await state.update_data(meals_1=message.text.strip())

    data = await state.get_data()
    countries_count = data.get('countries_count', 1)

    if countries_count == 2:
        await message.answer("🌍 Введите название второй страны:")
        await state.set_state(VoucherStates.waiting_for_country_2)
    else:
        user_services[message.from_user.id] = set()
        await message.answer(
            "🔧 Выберите дополнительные сервисы:",
            reply_markup=get_services_kb(message.from_user.id)
        )
        await state.set_state(VoucherStates.waiting_for_services_selection)

# === ОБРАБОТЧИКИ ДЛЯ ДАННЫХ СТРАНЫ 2 ===
@dp.message(VoucherStates.waiting_for_country_2)
async def process_country_2(message: Message, state: FSMContext):
    await state.update_data(country_2=message.text.strip())
    await message.answer("🏙️ Введите город для второй страны:")
    await state.set_state(VoucherStates.waiting_for_city_2)

@dp.message(VoucherStates.waiting_for_city_2)
async def process_city_2(message: Message, state: FSMContext):
    await state.update_data(city_2=message.text.strip())
    await message.answer("🏨 Введите название отеля для второй страны:")
    await state.set_state(VoucherStates.waiting_for_hotel_2)

@dp.message(VoucherStates.waiting_for_hotel_2)
async def process_hotel_2(message: Message, state: FSMContext):
    await state.update_data(hotel_2=message.text.strip())
    await message.answer("📅 Введите даты пребывания для второй страны:")
    await state.set_state(VoucherStates.waiting_for_dates_2)

@dp.message(VoucherStates.waiting_for_dates_2)
async def process_dates_2(message: Message, state: FSMContext):
    await state.update_data(dates_2=message.text.strip())
    await message.answer("🛏️ Введите тип размещения для второй страны:")
    await state.set_state(VoucherStates.waiting_for_stay_2)

@dp.message(VoucherStates.waiting_for_stay_2)
async def process_stay_2(message: Message, state: FSMContext):
    await state.update_data(stay_2=message.text.strip())
    await message.answer("⭐ Введите категорию номера для второй страны:")
    await state.set_state(VoucherStates.waiting_for_roomcat_2)

@dp.message(VoucherStates.waiting_for_roomcat_2)
async def process_roomcat_2(message: Message, state: FSMContext):
    await state.update_data(roomcat_2=message.text.strip())
    await message.answer("🍽️ Введите тип питания для второй страны:")
    await state.set_state(VoucherStates.waiting_for_meals_2)

@dp.message(VoucherStates.waiting_for_meals_2)
async def process_meals_2(message: Message, state: FSMContext):
    await state.update_data(meals_2=message.text.strip())

    user_services[message.from_user.id] = set()
    await message.answer(
        "🔧 Выберите дополнительные сервисы:",
        reply_markup=get_services_kb(message.from_user.id)
    )
    await state.set_state(VoucherStates.waiting_for_services_selection)

# === ОБРАБОТЧИКИ СЕРВИСОВ ===
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

    await callback.message.edit_reply_markup(reply_markup=get_services_kb(user_id))
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

    service_order = ['guide', 'transfer', 'excursions', 'extra']

    for service in service_order:
        if service in selected_services and f'service_{service}' not in data:
            await ask_service_info(callback.message, state, service)
            return

    await save_and_preview_data(callback.message, state)

async def ask_service_info(message: Message, state: FSMContext, service_type: str):
    service_prompts = {
        'guide': "🧑‍💼 Введите информацию о гиде:",
        'transfer': "🚗 Введите информацию о трансфере:",
        'excursions': "🏛️ Введите информацию об экскурсиях:",
        'extra': "📞 Введите дополнительный контакт менеджера:"
    }

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

    service_order = ['guide', 'transfer', 'excursions', 'extra']
    remaining_services = []

    for service in service_order:
        if service in selected_services and f'service_{service}' not in data:
            remaining_services.append(service)

    if remaining_services:
        await ask_service_info(message, state, remaining_services[0])
    else:
        await save_and_preview_data(message, state)

# Утилиты для предпросмотра и сценария
async def send_preview_for_cache(message: Message, cache_id: str):
    data = VOUCHER_CACHE.get(cache_id)
    if not data:
        await message.answer("❌ Кэш не найден.")
        return
    # Пересчёт сценария
    data['scenario_id'] = determine_scenario(data)
    preview_text = generate_preview(data)
    await message.answer(f"✅ Обновлено!\n\n{preview_text}", reply_markup=get_edit_kb(cache_id))

# ---------- 1) Редактировать клиентов ----------
@dp.callback_query(F.data.startswith("edit_clients:"))
async def edit_clients_start(callback: CallbackQuery, state: FSMContext):
    cache_id = callback.data.split(":")[1]
    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        return
    await state.update_data(edit_cache_id=cache_id)
    cur = VOUCHER_CACHE[cache_id].get("clients", [])
    current_line = ", ".join(cur) if cur else "—"
    text = (
        "👥 Введите НОВЫЙ список клиентов ЧЕРЕЗ ЗАПЯТУЮ.\n"
        "Например: Имя Фамилия 1, Имя Фамилия 2\n\n"
        f"Текущий: {current_line}"
    )
    await callback.message.edit_text(text)
    await state.set_state(EditVoucherStates.editing_clients)
    await callback.answer()


@dp.message(EditVoucherStates.editing_clients)
async def edit_clients_apply(message: Message, state: FSMContext):
    data = await state.get_data()
    cache_id = data.get("edit_cache_id")
    if not cache_id or cache_id not in VOUCHER_CACHE:
        await message.answer("❌ Кэш не найден.")
        await state.clear()
        return

    clients = [c.strip() for c in message.text.split(",") if c.strip()]
    if not clients:
        await message.answer("❌ Пустой список. Введите ФИО через запятую:")
        return

    VOUCHER_CACHE[cache_id]["clients"] = clients
    VOUCHER_CACHE[cache_id]["clients_count"] = len(clients)

    await state.clear()
    await send_preview_for_cache(message, cache_id)

# ---------- 2) Редактировать данные отеля ----------
def _hotel_block_kb(cache_id: str):
    d = VOUCHER_CACHE[cache_id]
    cnt = d.get("countries_count", 1) or 1
    rows = []
    rows.append([InlineKeyboardButton(text="🗺️ Блок страны 1", callback_data=f"hotel_block:{cache_id}:1")])
    if cnt == 2:
        rows.append([InlineKeyboardButton(text="🗺️ Блок страны 2", callback_data=f"hotel_block:{cache_id}:2")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@dp.callback_query(F.data.startswith("edit_hotel:"))
async def edit_hotel_start(callback: CallbackQuery, state: FSMContext):
    cache_id = callback.data.split(":")[1]
    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        return
    await state.update_data(edit_cache_id=cache_id)
    d = VOUCHER_CACHE[cache_id]
    if (d.get("countries_count") or 1) == 2:
        await callback.message.answer("Выберите, какой блок редактировать:", reply_markup=_hotel_block_kb(cache_id))
        await state.set_state(EditVoucherStates.editing_hotel_choose_block)
    else:
        # одна страна → сразу в блок 1
        await _hotel_edit_chain_begin(callback.message, state, cache_id, 1)
    await callback.answer()

@dp.callback_query(F.data.startswith("hotel_block:"))
async def edit_hotel_pick_block(callback: CallbackQuery, state: FSMContext):
    _, cache_id, block = callback.data.split(":")
    await _hotel_edit_chain_begin(callback.message, state, cache_id, int(block))
    await callback.answer()

async def _hotel_edit_chain_begin(message: Message, state: FSMContext, cache_id: str, block: int):
    if cache_id not in VOUCHER_CACHE:
        await message.answer("❌ Ваучер не найден.")
        return
    await state.update_data(edit_cache_id=cache_id, edit_block=block)
    d = VOUCHER_CACHE[cache_id]
    pfx = f"_{block}" if (d.get("countries_count") or 1) == 2 else "_1"
    # Показать текущие значения
    cur = {
        "country": d.get(f"country{pfx}", d.get("country", "—")),
        "city":    d.get(f"city{pfx}",    d.get("city", "—")),
        "hotel":   d.get(f"hotel{pfx}",   d.get("hotel", "—")),
        "dates":   d.get(f"dates{pfx}",   d.get("dates", "—")),
        "stay":    d.get(f"stay{pfx}",    d.get("stay", "—")),
        "roomcat": d.get(f"roomcat{pfx}", d.get("roomcat", "—")),
        "meals":   d.get(f"meals{pfx}",   d.get("meals", "—")),
    }
    await message.answer(
        "✏️ Редактирование блока страны "
        f"{block}.\n"
        "Отправьте новое значение для поля «Страна».\n"
        "Если хотите оставить без изменений — отправьте «-».\n\n"
        f"Текущее значение: {cur['country']}"
    )
    await state.set_state(EditVoucherStates.editing_hotel_country)

@dp.message(EditVoucherStates.editing_hotel_country)
async def _hotel_country_set(message: Message, state: FSMContext):
    await _hotel_set_and_ask_next(message, state, field="country",
                                  next_state=EditVoucherStates.editing_hotel_city,
                                  next_prompt="🏙️ Введите город (или «-» чтобы пропустить)")

@dp.message(EditVoucherStates.editing_hotel_city)
async def _hotel_city_set(message: Message, state: FSMContext):
    await _hotel_set_and_ask_next(message, state, field="city",
                                  next_state=EditVoucherStates.editing_hotel_name,
                                  next_prompt="🏨 Введите название отеля (или «-»)")

@dp.message(EditVoucherStates.editing_hotel_name)
async def _hotel_name_set(message: Message, state: FSMContext):
    await _hotel_set_and_ask_next(message, state, field="hotel",
                                  next_state=EditVoucherStates.editing_hotel_dates,
                                  next_prompt="📅 Введите даты (или «-»)")

@dp.message(EditVoucherStates.editing_hotel_dates)
async def _hotel_dates_set(message: Message, state: FSMContext):
    await _hotel_set_and_ask_next(message, state, field="dates",
                                  next_state=EditVoucherStates.editing_hotel_stay,
                                  next_prompt="🛏️ Введите размещение (или «-»)")

@dp.message(EditVoucherStates.editing_hotel_stay)
async def _hotel_stay_set(message: Message, state: FSMContext):
    await _hotel_set_and_ask_next(message, state, field="stay",
                                  next_state=EditVoucherStates.editing_hotel_roomcat,
                                  next_prompt="⭐ Введите категорию номера (или «-»)")

@dp.message(EditVoucherStates.editing_hotel_roomcat)
async def _hotel_roomcat_set(message: Message, state: FSMContext):
    await _hotel_set_and_ask_next(message, state, field="roomcat",
                                  next_state=EditVoucherStates.editing_hotel_meals,
                                  next_prompt="🍽️ Введите питание (или «-»)")

@dp.message(EditVoucherStates.editing_hotel_meals)
async def _hotel_meals_set(message: Message, state: FSMContext):
    # Последнее поле — после него показываем превью
    await _hotel_set_and_finish(message, state, field="meals")

async def _hotel_set_and_ask_next(message: Message, state: FSMContext, field: str, next_state: State, next_prompt: str):
    st = await state.get_data()
    cache_id = st.get("edit_cache_id")
    block = int(st.get("edit_block", 1))
    if not cache_id or cache_id not in VOUCHER_CACHE:
        await message.answer("❌ Ваучер не найден.")
        await state.clear()
        return

    txt = message.text.strip()
    if txt != "-":
        _hotel_set_field(cache_id, block, field, txt)

    await state.set_state(next_state)
    await message.answer(next_prompt)

async def _hotel_set_and_finish(message: Message, state: FSMContext, field: str):
    st = await state.get_data()
    cache_id = st.get("edit_cache_id")
    block = int(st.get("edit_block", 1))
    if not cache_id or cache_id not in VOUCHER_CACHE:
        await message.answer("❌ Ваучер не найден.")
        await state.clear()
        return

    txt = message.text.strip()
    if txt != "-":
        _hotel_set_field(cache_id, block, field, txt)

    await state.clear()
    await send_preview_for_cache(message, cache_id)

def _hotel_set_field(cache_id: str, block: int, field: str, value: str):
    """Записывает поле страны 1/2 с правильным ключом"""
    d = VOUCHER_CACHE[cache_id]
    cnt = d.get("countries_count", 1) or 1
    if cnt == 1:
        # зеркалим и в _1, и в без-суффиксные — для совместимости
        d[field] = value
        d[f"{field}_1"] = value
    else:
        d[f"{field}_{block}"] = value

# ---------- 3) Редактировать сервисы ----------
# === УЛУЧШЕННЫЕ ФУНКЦИИ ДЛЯ РЕДАКТИРОВАНИЯ СЕРВИСОВ ===

def get_services_edit_kb(cache_id: str, selected_services: list):
    """Клавиатура для выбора сервисов при редактировании"""
    buttons = []
    service_names = {
        'guide': '🧑‍💼 Гид',
        'transfer': '🚗 Трансфер',
        'excursions': '🏛️ Экскурсии',
        'extra': '📞 Доп. контакт'
    }

    for service_type, service_name in service_names.items():
        is_selected = service_type in selected_services
        icon = "✅" if is_selected else "☑️"
        text = f"{icon} {service_name}"
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f"edit_service_toggle:{cache_id}:{service_type}"
        )])

    if selected_services:
        buttons.append([InlineKeyboardButton(
            text="✏️ Редактировать выбранные сервисы",
            callback_data=f"edit_services_configure:{cache_id}"
        )])

    buttons.append([InlineKeyboardButton(
        text="✅ Завершить редактирование",
        callback_data=f"edit_services_done:{cache_id}"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_service_edit_kb(cache_id: str, service_type: str):
    """Клавиатура для редактирования конкретного сервиса"""
    service_names = {
        'guide': 'гида',
        'transfer': 'трансфера',
        'excursions': 'экскурсий',
        'extra': 'доп. контакта'
    }

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"✏️ Изменить {service_names[service_type]}",
            callback_data=f"edit_service_change:{cache_id}:{service_type}"
        )],
        [InlineKeyboardButton(
            text="❌ Удалить этот сервис",
            callback_data=f"edit_service_remove:{cache_id}:{service_type}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Назад к списку сервисов",
            callback_data=f"edit_services_back:{cache_id}"
        )]
    ])

@dp.callback_query(F.data.startswith("edit_services:"))
async def edit_services_start(callback: CallbackQuery, state: FSMContext):
    """Начало редактирования сервисов"""
    cache_id = callback.data.split(":")[1]
    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        return

    data = VOUCHER_CACHE[cache_id]
    selected_services = data.get("selected_services", [])

    # Показываем текущее состояние
    current_services = []
    for service in ['guide', 'transfer', 'excursions', 'extra']:
        if service in selected_services:
            value = data.get(f"service_{service}", "—")
            service_names = {
                'guide': '🧑‍💼 Гид',
                'transfer': '🚗 Трансфер',
                'excursions': '🏛️ Экскурсии',
                'extra': '📞 Доп. контакт'
            }
            current_services.append(f"• {service_names[service]}: {value}")

    preview_text = "Текущие сервисы:\n" + "\n".join(current_services) if current_services else "❌ Сервисы не выбраны"

    await callback.message.answer(
        f"🔧 Редактирование сервисов\n\n{preview_text}\n\n"
        "Выберите сервисы для включения в ваучер:",
        reply_markup=get_services_edit_kb(cache_id, selected_services)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_service_toggle:"))
async def edit_service_toggle(callback: CallbackQuery, state: FSMContext):
    """Включение/выключение сервиса"""
    _, cache_id, service_type = callback.data.split(":")

    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        await callback.answer()
        return

    data = VOUCHER_CACHE[cache_id]
    selected_services = data.get("selected_services", [])

    if service_type in selected_services:
        selected_services.remove(service_type)
        # Удаляем данные сервиса
        if f"service_{service_type}" in data:
            del data[f"service_{service_type}"]
    else:
        selected_services.append(service_type)

    data["selected_services"] = selected_services
    VOUCHER_CACHE[cache_id] = data

    await callback.message.edit_reply_markup(
        reply_markup=get_services_edit_kb(cache_id, selected_services)
    )
    await callback.answer(f"✅ Сервис {'добавлен' if service_type in selected_services else 'удалён'}")

@dp.callback_query(F.data.startswith("edit_services_configure:"))
async def edit_services_configure(callback: CallbackQuery, state: FSMContext):
    """Настройка выбранных сервисов"""
    cache_id = callback.data.split(":")[1]

    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        await callback.answer()
        return

    data = VOUCHER_CACHE[cache_id]
    selected_services = data.get("selected_services", [])

    if not selected_services:
        await callback.answer("❌ Нет выбранных сервисов для настройки")
        return

    # Показываем меню для редактирования каждого сервиса
    buttons = []
    service_names = {
        'guide': '🧑‍💼 Гид',
        'transfer': '🚗 Трансфер',
        'excursions': '🏛️ Экскурсии',
        'extra': '📞 Доп. контакт'
    }

    for service_type in selected_services:
        current_value = data.get(f"service_{service_type}", "—")
        buttons.append([InlineKeyboardButton(
            text=f"{service_names[service_type]}: {current_value[:30]}{'...' if len(current_value) > 30 else ''}",
            callback_data=f"edit_service_detail:{cache_id}:{service_type}"
        )])

    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=f"edit_services_back:{cache_id}"
    )])

    await callback.message.edit_text(
        "✏️ Выберите сервис для редактирования:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_service_detail:"))
async def edit_service_detail(callback: CallbackQuery, state: FSMContext):
    """Детальное редактирование конкретного сервиса"""
    _, cache_id, service_type = callback.data.split(":")

    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        await callback.answer()
        return

    data = VOUCHER_CACHE[cache_id]
    current_value = data.get(f"service_{service_type}", "")

    service_names = {
        'guide': 'гида',
        'transfer': 'трансфера',
        'excursions': 'экскурсий',
        'extra': 'дополнительного контакта'
    }

    placeholders = {
        'guide': "Например: Русскоязычный гид, 5 часов в день",
        'transfer': "Например: Встреча в аэропорту, машина бизнес-класса",
        'excursions': "Например: Обзорная экскурсия по городу, посещение музеев",
        'extra': "Например: +7 777 123 45 67 (WhatsApp)"
    }

    await callback.message.edit_text(
        f"✏️ Редактирование {service_names[service_type]}\n\n"
        f"Текущее значение: {current_value or '—'}\n\n"
        f"Введите новое значение:\n💡 {placeholders[service_type]}",
        reply_markup=get_service_edit_kb(cache_id, service_type)
    )

    await state.update_data(
        edit_cache_id=cache_id,
        edit_service_type=service_type
    )
    await state.set_state(EditVoucherStates.editing_services_bulk)
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_service_change:"))
async def edit_service_change(callback: CallbackQuery, state: FSMContext):
    """Запрос на изменение значения сервиса"""
    _, cache_id, service_type = callback.data.split(":")

    service_names = {
        'guide': 'гида',
        'transfer': 'трансфера',
        'excursions': 'экскурсий',
        'extra': 'дополнительного контакта'
    }

    placeholders = {
        'guide': "Например: Русскоязычный гид, 5 часов в день",
        'transfer': "Например: Встреча в аэропорту, машина бизнес-класса",
        'excursions': "Например: Обзорная экскурсия по городу, посещение музеев",
        'extra': "Например: +7 777 123 45 67 (WhatsApp)"
    }

    await callback.message.answer(
        f"✏️ Введите новое значение для {service_names[service_type]}:\n\n"
        f"💡 {placeholders[service_type]}"
    )

    await state.update_data(
        edit_cache_id=cache_id,
        edit_service_type=service_type
    )
    await state.set_state(EditVoucherStates.editing_services_bulk)
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_service_remove:"))
async def edit_service_remove(callback: CallbackQuery, state: FSMContext):
    """Удаление сервиса"""
    _, cache_id, service_type = callback.data.split(":")

    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        await callback.answer()
        return

    data = VOUCHER_CACHE[cache_id]
    selected_services = data.get("selected_services", [])

    if service_type in selected_services:
        selected_services.remove(service_type)
        data["selected_services"] = selected_services

    if f"service_{service_type}" in data:
        del data[f"service_{service_type}"]

    service_names = {
        'guide': 'Гид',
        'transfer': 'Трансфер',
        'excursions': 'Экскурсии',
        'extra': 'Доп. контакт'
    }

    await callback.answer(f"✅ {service_names[service_type]} удалён")
    await edit_services_start(callback, state)

@dp.callback_query(F.data.startswith("edit_services_back:"))
async def edit_services_back(callback: CallbackQuery, state: FSMContext):
    """Возврат к списку сервисов"""
    cache_id = callback.data.split(":")[1]
    await edit_services_start(callback, state)

@dp.callback_query(F.data.startswith("edit_services_done:"))
async def edit_services_done(callback: CallbackQuery, state: FSMContext):
    """Завершение редактирования сервисов"""
    cache_id = callback.data.split(":")[1]
    await send_preview_for_cache(callback.message, cache_id)
    await callback.answer("✅ Изменения сервисов сохранены")

@dp.message(EditVoucherStates.editing_services_bulk)
async def edit_service_value_input(message: Message, state: FSMContext):
    """Обработка ввода значения для сервиса"""
    data = await state.get_data()
    cache_id = data.get("edit_cache_id")
    service_type = data.get("edit_service_type")

    if not cache_id or cache_id not in VOUCHER_CACHE:
        await message.answer("❌ Ваучер не найден.")
        await state.clear()
        return

    if not service_type:
        await message.answer("❌ Ошибка: тип сервиса не указан.")
        await state.clear()
        return

    # Сохраняем значение
    VOUCHER_CACHE[cache_id][f"service_{service_type}"] = message.text.strip()

    # Убедимся, что сервис в списке выбранных
    if service_type not in VOUCHER_CACHE[cache_id].get("selected_services", []):
        if "selected_services" not in VOUCHER_CACHE[cache_id]:
            VOUCHER_CACHE[cache_id]["selected_services"] = []
        VOUCHER_CACHE[cache_id]["selected_services"].append(service_type)

    service_names = {
        'guide': 'гида',
        'transfer': 'трансфера',
        'excursions': 'экскурсий',
        'extra': 'дополнительного контакта'
    }

    await message.answer(f"✅ Значение {service_names[service_type]} обновлено!")
    await state.clear()

    # Возвращаемся к редактированию этого сервиса
    await edit_service_detail_simple(message, cache_id, service_type)

async def edit_service_detail_simple(message: Message, cache_id: str, service_type: str):
    """Показ деталей сервиса после редактирования"""
    data = VOUCHER_CACHE[cache_id]
    current_value = data.get(f"service_{service_type}", "")

    service_names = {
        'guide': 'гида',
        'transfer': 'трансфера',
        'excursions': 'экскурсий',
        'extra': 'дополнительного контакта'
    }

    await message.answer(
        f"✏️ Редактирование {service_names[service_type]}\n\n"
        f"Текущее значение: {current_value}\n\n"
        "Выберите действие:",
        reply_markup=get_service_edit_kb(cache_id, service_type)
    )

def _managers_edit_kb(cache_id: str):
    rows = []
    for m in MANAGER_ASSETS.keys():
        rows.append([InlineKeyboardButton(text=f"👤 {m}",  # Убрали .capitalize()
                                          callback_data=f"manager_set:{cache_id}:{m}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@dp.callback_query(F.data.startswith("edit_manager:"))
async def edit_manager_start(callback: CallbackQuery, state: FSMContext):
    cache_id = callback.data.split(":")[1]
    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        return
    await callback.message.answer("Выберите менеджера:", reply_markup=_managers_edit_kb(cache_id))
    await callback.answer()

@dp.callback_query(F.data.startswith("manager_set:"))
async def edit_manager_apply(callback: CallbackQuery, state: FSMContext):
    _, cache_id, manager = callback.data.split(":")
    if cache_id not in VOUCHER_CACHE:
        await callback.message.answer("❌ Ваучер не найден.")
        await callback.answer()
        return
    VOUCHER_CACHE[cache_id]["manager_key"] = manager
    await send_preview_for_cache(callback.message, cache_id)
    await callback.answer("✅ Менеджер обновлён")
# === ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ ВАУЧЕРА ===
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

# === ИСПРАВЛЕННАЯ ФУНКЦИЯ ГЕНЕРАЦИИ ВАУЧЕРА ===
def generate_voucher_image(data: dict) -> str:
    """ИСПРАВЛЕННАЯ функция генерации ваучера на основе рабочей логики"""
    try:
        scenario_id = data.get('scenario_id', 1)
        bg_path = SCENARIOS[scenario_id]["bg_path"]

        if not os.path.exists(bg_path):
            print(f"❌ Фон не найден: {bg_path}")
            # Пробуем найти любой доступный фон
            for sc_id, config in SCENARIOS.items():
                if os.path.exists(config["bg_path"]):
                    bg_path = config["bg_path"]
                    print(f"🔄 Используем фон сценария {sc_id}: {bg_path}")
                    break
            else:
                print("❌ Не найден ни один фон!")
                return None

        img = Image.open(bg_path).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Шрифты
        font_large = ImageFont.truetype(FORUM_TTF, 61)   # клиенты (КАПС)
        font_medium = ImageFont.truetype(FORUM_TTF, 68)  # значения в таблицах
        font_small = ImageFont.truetype(FORUM_TTF, 65)   # сервисные строки

        coords_dict = globals().get(f"COORDS_SCENARIO_{scenario_id}", COORDS_SCENARIO_1)

        # Утилита для рисования строки в прямоугольнике (левый верх + отступы)
        def draw_in_box(key_box, text, font):
            x1, y1, _, _ = key_box
            draw.text((x1 + 10, y1 + 10), text, font=font, fill=(0, 0, 0))

        # === 1) Клиенты (правая колонка, выравнивание по правому краю)
        # === 1) Клиенты (правая колонка, выравнивание по правому краю)
        if "clients" in coords_dict and "clients" in data:
            client_box = coords_dict["clients"]
            line_height = 70
            y = client_box[1] + 10
            for client in data["clients"]:
                line = client.upper()  # ВСЕГДА КАПСОМ на изображении
                text_width = draw.textlength(line, font=font_large)
                x = client_box[2] - text_width - 20
                draw.text((x, y), line, font=font_large, fill=(0, 0, 0))
                y += line_height


        # === 2) Определяем, однотабличный режим или мульти-страны (_1/_2)
        has_multi = any(k.endswith("_1") for k in coords_dict.keys())

        if not has_multi:
            # Одна страна - используем поля без суффиксов
            for field in ["country", "city", "hotel", "dates", "stay", "roomcat", "meals"]:
                # Для одной страны данные хранятся в полях без суффиксов
                field_value = data.get(field) or data.get(f"{field}_1")
                if field in coords_dict and field_value:
                    draw_in_box(coords_dict[field], field_value, font_medium)
        else:
            # Две страны - используем поля с суффиксами _1 и _2
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
                    if with_suf in coords_dict and data.get(with_suf):
                        draw_in_box(coords_dict[with_suf], data[with_suf], font_medium)

            # Верхний блок (_1) и нижний блок (_2)
            draw_country_block("1")
            draw_country_block("2")

        # === 3) Сервисные строки с ВЫРАВНИВАНИЕМ ===
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

        # Рисуем сервисы в правильном порядке
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

        # === 4) ВСТАВКА МЕНЕДЖЕРА ===
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

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ОТРИСОВКИ ===

def grow_box(box, dleft=0, dtop=0, dright=0, dbottom=0):
    x1,y1,x2,y2 = box
    return (x1 - dleft, y1 - dtop, x2 + dright, y2 + dbottom)

# Увеличиваем боксы для телефонов менеджеров
ALL_COORDS = [
    COORDS_SCENARIO_1, COORDS_SCENARIO_2, COORDS_SCENARIO_3, COORDS_SCENARIO_4, COORDS_SCENARIO_5,
    COORDS_SCENARIO_6, COORDS_SCENARIO_7, COORDS_SCENARIO_8, COORDS_SCENARIO_9, COORDS_SCENARIO_10,
]

def bump_all_phone_boxes(dright=20, dbottom=8):
    """Увеличить бокс телефона для всех сценариев (вправо и вниз)."""
    for C in ALL_COORDS:
        if "manager_phone" in C:
            C["manager_phone"] = grow_box(C["manager_phone"], dright=dright, dbottom=dbottom)

# Вызываем один раз при инициализации
bump_all_phone_boxes(dright=20, dbottom=8)

PAD_NAME  = (10,10,10,10)   # как было
PAD_PHONE = (6,4,6,4)       # меньше отступ — больше видимый размер

def insert_manager_assets(img, manager_key, name_coords, phone_coords):
    try:
        # Используем первый менеджера из списка как fallback
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


# === ИСПРАВЛЕННАЯ ФУНКЦИЯ СОХРАНЕНИЯ ДАННЫХ ===
async def save_and_preview_data(message: Message, state: FSMContext):
    """Сохраняет данные и показывает превью"""
    data = await state.get_data()

    # Для одной страны копируем данные из полей _1 в поля без суффиксов
    countries_count = data.get('countries_count', 1)
    if countries_count == 1:
        # Копируем данные из country_1, city_1 и т.д. в country, city и т.д.
        for field in ["country", "city", "hotel", "dates", "stay", "roomcat", "meals"]:
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
    await message.answer(
        f"✅ Все данные сохранены!\n\n{preview_text}",
        reply_markup=get_edit_kb(cache_id)
    )
    await state.clear()


def create_clickable_pdf(image_path, scenario_id, output_path=None):
    """Создает PDF с кликабельными ссылками"""
    try:
        if output_path is None:
            output_path = f"voucher_scenario_{scenario_id}_{uuid.uuid4().hex[:8]}.pdf"

        c = canvas.Canvas(output_path, pagesize=A4)

        # Добавляем изображение
        img = Image.open(image_path)
        img_width, img_height = img.size

        page_width, page_height = A4
        scale = min(page_width / img_width, page_height / img_height)
        new_width = img_width * scale
        new_height = img_height * scale

        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2

        c.drawImage(image_path, x, y, new_width, new_height)

        # Добавляем кликабельные зоны
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

# === СОХРАНЕНИЕ И ПРЕВЬЮ ===

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

    clients_text = "\n".join([f"• {client}" for client in clients])

    preview = (
        f"📋 Сценарий {scenario_id}: {SCENARIOS[scenario_id]['name']}\n\n"
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
        preview += f"• Питание: {data.get(f'meals_{i}', '—')}\n\n"

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

# === ГЕНЕРАЦИЯ ВАУЧЕРА ===
@dp.callback_query(F.data.startswith("generate:"))
async def generate_voucher(callback: CallbackQuery):
    cache_id = callback.data.split(":")[1]
    data = VOUCHER_CACHE.get(cache_id)

    if not data:
        await callback.message.answer("❌ Данные не найдены.")
        await callback.answer()
        return

    # Детальная отладочная информация
    debug_info = (
        f"🔍 Отладка данных:\n"
        f"• Сценарий: {data.get('scenario_id')}\n"
        f"• Клиенты: {data.get('clients', [])}\n"
        f"• Страны: {data.get('countries_count')}\n"
        f"• Сервисы: {data.get('selected_services', [])}\n"
        f"• Менеджер: {data.get('manager_key')}\n"
        f"• Данные страны 1: {data.get('country_1')}, {data.get('city_1')}\n"
        f"• Данные страны 2: {data.get('country_2')}, {data.get('city_2')}"
    )
    print(debug_info)  # Выводим в консоль для отладки

    await callback.message.answer("🔄 Генерирую ваучер...")

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

        # Отправляем документ с кнопкой создания нового ваучера
        await callback.message.answer_document(
            buf,
            caption="✅ Ваш ваучер готов!\n\nХотите создать ещё один ваучер?",
            reply_markup=get_new_voucher_kb()
        )

        # Очищаем временные файлы
        try:
            os.remove(image_path)
        except:
            pass
        try:
            os.remove(pdf_path)
        except:
            pass

        # Очищаем кэш этого ваучера
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
        "👨‍💼 Выберите менеджера:",
        reply_markup=get_managers_kb()
    )
    await state.set_state(VoucherStates.waiting_for_manager)
    await callback.answer()

@dp.callback_query(F.data == "back_to_countries")
async def back_to_countries(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🌍 На сколько стран делаем ваучер?",
        reply_markup=get_countries_count_kb()
    )
    await state.set_state(VoucherStates.waiting_for_countries_count)
    await callback.answer()

@dp.callback_query(F.data == "back_to_meals")
async def back_to_meals(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    countries_count = data.get('countries_count', 1)

    if countries_count == 2:
        await callback.message.answer("🍽️ Введите тип питания для второй страны:")
        await state.set_state(VoucherStates.waiting_for_meals_2)
    else:
        await callback.message.answer("🍽️ Введите тип питания:")
        await state.set_state(VoucherStates.waiting_for_meals_1)
    await callback.answer()

# === ЗАПУСК БОТА ===
async def main():
    print("✅ Бот AMAL запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())