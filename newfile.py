import asyncio
import json
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiofiles
import pytz

TOKEN = "8280629128:AAFpQOqFRMlkhiQapYQpvskyGgZ42T-DdU8"
ADMIN_ID = 1970260241
STATUS_FILE = "city_status.json"
LAST_LIST_MESSAGE_FILE = "last_list_message.json"
GROUP_ID = -1003346416057
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

bot = Bot(token=TOKEN)
dp = Dispatcher()

city_tags = {
    "👁️ Cherepovets": "череп, череповец",
    "👹 Magadan": "мага, магадан",
    "🏰 Podolsk": "подольск, подо",
    "🏙 Surgut": "сургут",
    "🏍 Izhevsk": "ижевск",
    "🎄 Tomsk": "томск",
    "🐿 Tver": "тверь",
    "🐦‍🔥 Vologda": "вологда",
    "🦁 Taganrog": "тага, таганрог, тгн",
    "🌼 Novgorod": "новгород, нвг",
    "🫐 Kaluga": "калуга",
    "😹 Vladimir": "владимир, влд",
    "🐲 Kostroma": "кострома, костро, кстрм",
    "🦎 Chita": "чита",
    "🧣 Astrakhan": "астра, астрахань, астр",
    "👜 Bratsk": "братск",
    "🥐 Tambov": "тамбов",
    "🥽 Yakutsk": "якутск",
    "🍭 Ulyanovsk": "уля, ульян, улья",
    "🎈 Lipetsk": "липа, липецк",
    "💦 Barnaul": "барно, барнаул, барна",
    "🏛 Yaroslavl": "яро, ярославль",
    "🦅 Orel": "орел, орёл",
    "🧸 Bryansk": "брянск",
    "🪭 Pskov": "псков",
    "🫚 Smolensk": "смола, смоленск",
    "🪼 Stavropol": "ставро, ставрополь",
    "🪅 Ivanovo": "иваново",
    "🪸 Tolyatti": "тольятти, толя, тлт",
    "🐋 Tyumen": "тюмень",
    "🌺 Kemerovo": "кемер, кемерово, кем",
    "🔫 Kirov": "киров",
    "🍖 Orenburg": "орена, оренбург, орен",
    "🥋 Arkhangelsk": "арх, архангельск",
    "🃏 Kursk": "курск",
    "🎳 Murmansk": "мурм, мурманск, мурма",
    "🎷 Penza": "пенза",
    "🎭 Ryazan": "рязань, ряз",
    "⛳️ Tula": "тула",
    "🏟 Perm": "перм, пермь",
    "🐨 Khabarovsk": "хаба, хабаровск",
    "🪄 Cheboksary": "чебы, чебоксары",
    "🖇 Krasnoyarsk": "красно, красноярск",
    "🕊 Chelyabinsk": "челяба, челябинск",
    "👒 Kaliningrad": "калина, калининград",
    "🧶 Vladivostok": "восток, владивосток",
    "🌂 Vladikavkaz": "кавказ, владикавказ",
    "⛑️ Mahachkala": "маха, махачкала, мхч",
    "🎓 Belgorod": "белг, белгород, белга",
    "👑 Voronezh": "воронеж, ворона, врн",
    "🎒 Volgograd": "влг, волгоград, волга",
    "🌪 Irkutsk": "ирк, иркутск",
    "🪙 Omsk": "омск",
    "🐉 Saratov": "сарат, саратов",
    "🍙 Grozny": "гроз, грозный, грз",
    "🍃 Novosib": "нск, новосибирск, новосиб",
    "🪿 Arzamas": "арз, арзамас",
    "🪻 Krasnodar": "крд, краснодар",
    "📗 Ekb": "екб",
    "🪺 Anapa": "анапа",
    "🍺 Rostov": "ростов, рост",
    "🎧 Samara": "самара",
    "🏛 Kazan": "казань",
    "🌊 Sochi": "сочи",
    "🌪 Ufa": "уфа ",
    "🌉 Spb": "спб",
    "🌇 Moscow": "мск, москва, москов",
    "🤎 Choco": "чоко ",
    "📕 Chilli": "чили",
    "❄️ Ice": "айс",
    "📓 Gray": "грэй, грей",
    "📘 Aqua": "аква",
    "🩶 Platinum": "плат",
    "💙 Azure": "азур",
    "💛️ Gold": "голд",
    "❤‍🔥 Crimson": "кримс",
    "🩷 Magenta": "магента",
    "🤍 White": "вайт",
    "💜 Indigo": "инд",
    "🖤 Black": "блэк, блек",
    "🍒 Cherry": "чери, черри",
    "💕 Pink": "пинк",
    "🍋 Lime": "лайм",
    "💜 Purple": "пурпл",
    "🧡 Orange": "оранж",
    "💛 Yellow": "елоу, ело",
    "💙 Blue": "блу",
    "💚 Green": "грин",
    "❤‍🩹 Red": "ред"
}

last_texts = {}
all_tags = {}
for city, tags_str in city_tags.items():
    tags = [tag.strip().lower() for tag in tags_str.split(",")]
    for tag in tags:
        all_tags[tag] = city

city_status = {}
group_membership_cache = {}

async def load_statuses():
    global city_status
    if os.path.exists(STATUS_FILE):
        try:
            async with aiofiles.open(STATUS_FILE, 'r', encoding='utf-8') as f:
                content = await f.read()
                saved_statuses = json.loads(content)
                city_status = {city: saved_statuses.get(city, "") for city in city_tags.keys()}
        except Exception as e:
            print(f"Ошибка при загрузке слетов: {e}")
            city_status = {city: "" for city in city_tags.keys()}
    else:
        city_status = {city: "" for city in city_tags.keys()}
    return city_status

async def save_statuses():
    try:
        async with aiofiles.open(STATUS_FILE, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(city_status, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Ошибка при сохранении слетов: {e}")

async def load_last_list_message():
    if os.path.exists(LAST_LIST_MESSAGE_FILE):
        try:
            async with aiofiles.open(LAST_LIST_MESSAGE_FILE, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except:
            return {}
    return {}

async def save_last_list_message(chat_id, message_id):
    last_messages = await load_last_list_message()
    last_messages[str(chat_id)] = message_id
    async with aiofiles.open(LAST_LIST_MESSAGE_FILE, 'w') as f:
        await f.write(json.dumps(last_messages))
def format_status(status):
    if not status:
        return ""
    if status.lower() == "0" or status == "❌":
        return "❌"
    return f"{status}✅"

def is_message_from_current_night(message: Message):
    """Проверяет, что сообщение было отправлено в текущую ночь (00:00-05:00)"""
    try:
        msg_date = message.date.astimezone(MOSCOW_TZ)
        now_moscow = datetime.now(MOSCOW_TZ)
        
        return (msg_date.date() == now_moscow.date() and 
                0 <= msg_date.hour < 5)
    except Exception as e:
        print(f"Ошибка проверки времени сообщения: {e}")
        return False

async def check_group_membership(user_id):
    if user_id in group_membership_cache:
        cache_data = group_membership_cache[user_id]
        if isinstance(cache_data, tuple) and len(cache_data) == 2:
            status, timestamp = cache_data
            if datetime.now().timestamp() - timestamp < 3600:
                return status in ['member', 'administrator', 'creator']
    
    try:
        chat_member = await bot.get_chat_member(GROUP_ID, user_id)
        status = chat_member.status
        group_membership_cache[user_id] = (status, datetime.now().timestamp())
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка при проверке участника группы: {e}")
        return False

def generate_status_text():
    response = "Слеты на сегодня\n\n"
    for city in city_status:
        status = format_status(city_status[city])
        response += f"{city} - {status}\n"
    return response

async def update_list_message(chat_id):
    new_text = generate_status_text()
    last_messages = await load_last_list_message()
    message_id = last_messages.get(str(chat_id))
    
    if not message_id:
        return
    
    try:
        if last_texts.get(chat_id) == new_text:
            return
            
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=new_text,
            parse_mode='Markdown'
        )
        last_texts[chat_id] = new_text
    except Exception as e:
        print(f"Ошибка при обновлении сообщения: {e}")

@dp.message(Command("start"))
async def cmd_start(message: Message):
    help_text = (
        "Не пишите /getlist каждый раз.\n"
        "*Для конченых (Закрепляете один лист и он изменяет сам слеты в этом листе)\n"
        "/getlist - Текущие слеты\n"
        "/tags - Список тегов серверов\n"
        "/reset - Сбросить слеты (доступно админу)\n\n"
        "Работает с 00:00 до 05:00 по МСК!"
    )
    await message.answer(help_text)

@dp.message(Command("getlist"))
async def cmd_getlist(message: Message):
    text = generate_status_text()
    msg = await message.answer(text, parse_mode='Markdown')
    
    await save_last_list_message(message.chat.id, msg.message_id)
    last_texts[message.chat.id] = text

@dp.message(Command("tags"))
async def cmd_tags(message: Message):
    response = "*Список тегов для серверов:*\n\n"
    for city, tags_str in city_tags.items():
        response += f"{city} -> {tags_str}\n"
    await message.answer(response)

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У тебя нет прав для этой команды.")
        return

    try:
        global city_status
        city_status = {city: "" for city in city_status.keys()}
        await save_statuses()
        await message.answer("Очищено")
        await update_list_message(message.chat.id)
    except Exception as e:
        await message.answer(f"Ошибка при очистке слетов: {str(e)}")

@dp.message(F.text)
async def handle_city_tag(message: Message):
    """Обработка сообщений с тегами городов"""

    if message.text.startswith('/'):
        return
    
    if not await check_group_membership(message.from_user.id):
        return

    if not is_message_from_current_night(message):
        return
    
    text = message.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return
    
    tag = parts[0].strip().lower()
    status = parts[1].strip()
    
    if tag in all_tags:
        city = all_tags[tag]
        city_status[city] = status
        await save_statuses()
        
        emoji = "❌" if status.lower() in ["0"] or status == "❌" else "✅"
        reply = f"{emoji} Слет для {city} записан: {format_status(status)}"
        await message.reply(reply)
        
        chats_to_update = await load_last_list_message()
        for chat_id in chats_to_update.keys():
            await update_list_message(int(chat_id))

async def cache_cleaner():
    while True:
        current_time = datetime.now().timestamp()
        for user_id in list(group_membership_cache.keys()):
            cache_data = group_membership_cache.get(user_id)
            if cache_data and isinstance(cache_data, tuple) and len(cache_data) == 2:
                _, timestamp = cache_data
                if current_time - timestamp > 3600:
                    del group_membership_cache[user_id]
        await asyncio.sleep(3600)

async def main():
    await load_statuses()
    
    asyncio.create_task(cache_cleaner())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())