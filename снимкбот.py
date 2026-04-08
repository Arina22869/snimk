import logging
import sqlite3
import random
import asyncio
import json
import traceback
import os
from contextlib import contextmanager
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import gspread
from google.oauth2.service_account import Credentials

# ============= НАСТРОЙКИ =============
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавьте переменную окружения BOT_TOKEN на сервере")

ADMIN_IDS = [1665864236]

# ID таблицы и ключ
SPREADSHEET_ID = "1oMohwWx3xIEt9N_s9NXMAerKM4JReqVLozadPC52ZJA"
# =====================================

# ============= КЛЮЧ (вшит) =============
KEY_JSON = '''{
  "type": "service_account",
  "project_id": "snimk-489208",
  "private_key_id": "a8ea7f1b203f733aed6a5d28e5a4df8d447bc1ee",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDo+F6ebOWUslrW\\nS3Mf6oIZL5fNZMYzMR2RagMORtid9LMcxPL55eT/DOhIDsd5WTZCHuyF/ppjZUAX\\nn6xEBG0LgvNs0pC3Tc1oRZ3EnnSX8zIqRIw+/2m7g3/2Mk9QmWZTQmcrY4SyCjZi\\nDsogM78ZjxBIiqPU0dgqA2JDSOVuNpz1wWKWQ/oliz9o2exPspdt+LAiE4j6SZHX\\nD7L56+AtsaZiOWAnJsDIdC/s+t5aSBwviTLrMCPVZrFBkjzz0palBmcL0rRTpzyS\\n03Gswz7QEiAp/qgszdbpZIufMDJdDn9NUvrICvWHx0vApDZVZyQuNWKeIkkDyVTG\\nN1Zny4LtAgMBAAECggEAKYzWj0nbvmP6+HpXa4tPLb/DwsGk6c9qNxuhtOOk0bMp\\nWMm1jiVW7Lg4G1XrdLSZDTznsVRB49VUk4IKXs0tR57Q3IlHfzHUnzK/Wyhpogoh\\nWdGE891o1aUz5sx9QeJCEjpnHSFwMrLIlT+PBCRGgn/2BwIXCydr9r5IwbhYFwo2\\nV2oVf46lKfKutGE5vcI3vQy6OTlEzdR+pPzWnQFPVBbcm7ZFMRU4UNYiB+H2k0Qg\\na65KYtg34cL8VWHW6B8JwYm9N1DGlYL/Vy/AJjZk12x9abGqW4d30rYIFsUBlpXU\\nv7+wGRoMindb1n0YovLY70Vg7esXiZIKHuJcF97BgQKBgQD8EBU6/9Lf09zi/83R\\n61G3NXVTeCVGGoVGr4UWAyq1b23MPC7hWtCqGi6GwbmfEFKoxKzGGTWyX03Atb7z\\nV0MYeWjZB2PV2Uj07ISFfkBcLbxjOn5JBcx0RiOXRjeoPC9HinLczWyG0m0p5UX/\\nKjF8xLOMmJPsc5iGHrvmiqtRrQKBgQDsm/EEGoHGt7QQJYwYT9A/NtluKhnB+rt9\\nVP/JMrk7LsrtduT385u3hBF+VBzptpk9aWDGz+JmpGltSosEGIxXd9WE+Hxc4Ns2\\nHPh6wLHBDTVygkwJOiErC/3cy+NMQO1WUtOuIXg159O/JgWhclYVDOCXDusuw0wG\\n7si9d8+eQQKBgQDpRFEBesLCVST0BluJS0ciT5y2lFeaWuzAD6sQRfn+UpLAEWop\\nL4wv/27TUvDfXZHBkdF6utXQrxYbo5aFSFpVifYX8xjXTPCRiVjS2ZXiOIlBI16/\\nYVhmuooxctALJzdx85R89rbaxl40CXQPwhJuLvMiyAkNJ6Udac/meKo3OQKBgAyG\\nMJrEAGyRWsGkCydaSi6ea6HuLpDbAcOflS6ENdPRJUKukW4igfKT1g02zJT+alwa\\n0NmVNWmzeDUlxfgAiKU0naO9N2//IvtZSznMK1yJo3OdPAMdBZZuuxBN5okpwqZY\\nGgZUlTVdQRMUIyYplC7nEJhOXNqL0eFoEE4fImlBAoGAZVAWas0/FEEy1JQHVKuJ\\n8DzTUcSQdImO1HSVKHFUmBW0ZcCSLLz/xnB7L3QcDHNBBdiFeXfubtrRE2LXiqpy\\nFiL/vTZp9tq3hwfjawXSAwkTZgeNJ43zaS/L4HJ+eCBlC0r4ZvzScqc71nXb3xfj\\n6B2CVecxeLkDRgnDq2krLgI=\\n-----END PRIVATE KEY-----\\n",
  "client_email": "snimk-386@snimk-489208.iam.gserviceaccount.com",
  "client_id": "115514717748293156637",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/snimk-386%40snimk-489208.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}'''
# ================================================

# ============= Смайлики =============
ITEM_EMOJIS = {
    "кепка": "🧢", "носки": "🧦", "кружка": "☕", "брелок": "🔑",
    "стикеры": "🎨", "снимочков": "🪙", "снимочки": "🪙", "ТЗ": "⏰",
    "статус": "📝", "опоздать": "⏳", "бонусный сундук": "🎁",
    "фото": "📸", "фриспин": "🎰", "музыку": "🎵", "джекпот": "💎",
}
# =================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ============= БАЗА ДАННЫХ =============
@contextmanager
def get_db():
    conn = sqlite3.connect('snimochki.db')
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS inventory (user_id INTEGER PRIMARY KEY, items TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS users_cache (user_id INTEGER PRIMARY KEY, name TEXT, brs INTEGER, snimochki INTEGER)')
        conn.execute('''CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            author_id INTEGER,
            author_name TEXT,
            date TEXT
        )''')
        conn.execute('CREATE TABLE IF NOT EXISTS king (id INTEGER PRIMARY KEY, last_date TEXT, last_user_id INTEGER)')
        conn.commit()
        
        # Добавим пару тестовых цитат
        cursor = conn.execute("SELECT COUNT(*) FROM quotes")
        if cursor.fetchone()[0] == 0:
            sample_quotes = [
                ("А я думал, дедлайн — это имя!", 1, "Admin", datetime.now().isoformat()),
                ("Студсовет — это семья, где все друг друга крышуют", 1, "Admin", datetime.now().isoformat()),
                ("ТЗ — это техническое задание, а не Трудно Забить", 1, "Admin", datetime.now().isoformat()),
            ]
            for text, author_id, author_name, date in sample_quotes:
                conn.execute("INSERT INTO quotes (text, author_id, author_name, date) VALUES (?, ?, ?, ?)",
                           (text, author_id, author_name, date))
            conn.commit()

# ============= GOOGLE SHEETS =============
def get_gs_client():
    try:
        creds_dict = json.loads(KEY_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
            "https://spreadsheets.google.com/feeds"
        ])
        return gspread.authorize(creds)
    except Exception as e:
        logging.error(f"❌ Ошибка подключения: {e}")
        return None

def sync_users_from_google():
    client = get_gs_client()
    if not client: return
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("users")
        all_rows = sheet.get_all_values()
        if len(all_rows) < 2: return
        with get_db() as conn:
            conn.execute("DELETE FROM users_cache")
            for row in all_rows[1:]:
                if len(row) >= 4 and row[0].strip().isdigit():
                    user_id = int(row[0])
                    name = row[1] if len(row) > 1 else f"User{user_id}"
                    brs = int(row[2]) if len(row) > 2 and row[2].isdigit() else 0
                    snimochki = int(row[3]) if len(row) > 3 and row[3].lstrip('-').isdigit() else 0
                    conn.execute("INSERT OR REPLACE INTO users_cache (user_id, name, brs, snimochki) VALUES (?, ?, ?, ?)",
                                (user_id, name, brs, snimochki))
            conn.commit()
        logging.info("✅ Кэш обновлён")
    except Exception as e:
        logging.error(f"❌ Ошибка синхронизации: {e}")

def get_user_snimochki(user_id):
    with get_db() as conn:
        cursor = conn.execute("SELECT snimochki FROM users_cache WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 0

def update_user_snimochki(user_id, new_value):
    with get_db() as conn:
        conn.execute("UPDATE users_cache SET snimochki=? WHERE user_id=?", (new_value, user_id))
        if conn.rowcount == 0:
            conn.execute("INSERT INTO users_cache (user_id, name, brs, snimochki) VALUES (?, ?, ?, ?)",
                        (user_id, f"User{user_id}", 0, new_value))
        conn.commit()
    
    async def background_update():
        client = get_gs_client()
        if not client: return
        try:
            sheet = client.open_by_key(SPREADSHEET_ID).worksheet("users")
            all_rows = sheet.get_all_values()
            user_id_str = str(user_id)
            row_num = None
            for i, row in enumerate(all_rows, start=1):
                if row and row[0] == user_id_str:
                    row_num = i
                    break
            if row_num:
                sheet.update_cell(row_num, 4, str(new_value))
            else:
                sheet.append_row([str(user_id), f"User{user_id}", "0", str(new_value), ""])
            logging.info(f"✅ Google обновлён: {user_id} -> {new_value}")
        except Exception as e:
            logging.error(f"❌ Ошибка обновления Google: {e}")
    
    asyncio.create_task(background_update())

# ============= ИГРОВАЯ ЛОГИКА =============
def open_chest():
    items = [
        {"name": "кепка \"СНИМК\"", "rarity": "обычный"},
        {"name": "носки \"СНИМК\"", "rarity": "обычный"},
        {"name": "кружка \"СНИМК\"", "rarity": "обычный"},
        {"name": "брелок \"СНИМК\"", "rarity": "обычный"},
        {"name": "стикеры \"СНИМК\"", "rarity": "обычный"},
        {"name": "5 снимочков", "rarity": "редкий"},
        {"name": "10 снимочков", "rarity": "редкий"},
        {"name": "просрочить ТЗ на 2 часа", "rarity": "редкий"},
        {"name": "поменять статус в чате", "rarity": "редкий"},
        {"name": "легально опоздать", "rarity": "редкий"},
        {"name": "15 снимочков", "rarity": "очень редкий"},
        {"name": "бонусный сундук", "rarity": "очень редкий"},
        {"name": "фото с председателем", "rarity": "очень редкий"},
        {"name": "один фриспин", "rarity": "очень редкий"},
        {"name": "два фриспина", "rarity": "легендарный"},
        {"name": "право выбрать музыку", "rarity": "легендарный"},
        {"name": "20 снимочков", "rarity": "легендарный"},
    ]
    rarity_chances = {"обычный": 0.5, "редкий": 0.3, "очень редкий": 0.15, "легендарный": 0.05}
    rarity_groups = {}
    for item in items:
        rarity_groups.setdefault(item["rarity"], []).append(item)
    rand = random.random()
    cumulative = 0
    selected_rarity = "обычный"
    for rarity, chance in rarity_chances.items():
        cumulative += chance
        if rand < cumulative:
            selected_rarity = rarity
            break
    if selected_rarity in rarity_groups:
        return random.choice(rarity_groups[selected_rarity])
    return None

def spin_wheel():
    rand = random.randint(1, 100)
    if rand <= 50:
        return {"type": "snimochki", "value": 5, "name": "+5 снимочков"}
    elif rand <= 65:
        return {"type": "item", "value": "кепка \"СНИМК\"", "name": "кепка \"СНИМК\""}
    elif rand <= 75:
        return {"type": "snimochki", "value": 10, "name": "+10 снимочков"}
    elif rand <= 85:
        return {"type": "nothing", "value": 0, "name": "ничего"}
    elif rand <= 90:
        return {"type": "item", "value": "5 снимочков", "name": "5 снимочков (бонус)"}
    elif rand <= 95:
        return {"type": "snimochki", "value": 15, "name": "+15 снимочков"}
    elif rand <= 99:
        return {"type": "item", "value": "бонусный сундук", "name": "бонусный сундук"}
    else:
        return {"type": "jackpot", "value": 50, "name": "ДЖЕКПОТ! +50 снимочков"}

# ============= ИНВЕНТАРЬ =============
def get_inventory(user_id):
    with get_db() as conn:
        cursor = conn.execute("SELECT items FROM inventory WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else ""

def update_inventory(user_id, items_dict):
    items_str = ",".join([f"{name}:{count}" for name, count in items_dict.items()])
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO inventory (user_id, items) VALUES (?, ?)", (user_id, items_str))
        conn.commit()

def parse_inventory(items_str):
    if not items_str:
        return {}
    result = {}
    for item in items_str.split(','):
        if ':' in item:
            name, count = item.split(':')
            result[name] = int(count)
    return result

def add_to_inventory(user_id, item_name, count=1):
    items_dict = parse_inventory(get_inventory(user_id))
    items_dict[item_name] = items_dict.get(item_name, 0) + count
    update_inventory(user_id, items_dict)

def remove_from_inventory(user_id, item_name, count=1):
    items_dict = parse_inventory(get_inventory(user_id))
    if item_name in items_dict and items_dict[item_name] >= count:
        items_dict[item_name] -= count
        if items_dict[item_name] <= 0:
            del items_dict[item_name]
        update_inventory(user_id, items_dict)
        return True
    return False

def has_item(user_id, item_name):
    items_dict = parse_inventory(get_inventory(user_id))
    return item_name in items_dict and items_dict[item_name] > 0

def get_item_emoji(item_name):
    for key, emoji in ITEM_EMOJIS.items():
        if key in item_name.lower():
            return emoji
    return "📦"

# ============= КЛАВИАТУРЫ =============
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎁 Открыть сундук (5)", callback_data="open_chest"),
                InlineKeyboardButton(text="🎲 Испытать удачу (3)", callback_data="spin"))
    builder.row(InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
                InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inventory"))
    return builder.as_markup()

def back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="menu"))
    return builder.as_markup()

def chest_result_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎁 Ещё сундук", callback_data="open_chest"),
                InlineKeyboardButton(text="🎲 Ещё удачу", callback_data="spin"))
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="menu"))
    return builder.as_markup()

# ============= КОМАНДЫ =============
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    snimochki = get_user_snimochki(user_id)
    await message.answer(f"👋 Привет, {name}!\n\n🪙 Твои снимочки: {snimochki}\n\n🎮 Выбери действие:", reply_markup=main_menu_keyboard())

@dp.callback_query(lambda c: c.data == "menu")
async def back_to_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    name = callback.from_user.full_name
    snimochki = get_user_snimochki(user_id)
    await callback.message.edit_text(f"👋 Привет, {name}!\n\n🪙 Твои снимочки: {snimochki}\n\n🎮 Выбери действие:", reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    name = callback.from_user.full_name
    snimochki = get_user_snimochki(user_id)
    items_dict = parse_inventory(get_inventory(user_id))
    inventory_text = "\n".join([f"• {get_item_emoji(item)} {item} ×{count}" for item, count in items_dict.items()]) if items_dict else "пусто"
    await callback.message.edit_text(f"👤 **{name}**\n🪙 Снимочки: {snimochki}\n\n🎒 **Инвентарь:**\n{inventory_text}", reply_markup=back_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "inventory")
async def show_inventory(callback: CallbackQuery):
    user_id = callback.from_user.id
    items_dict = parse_inventory(get_inventory(user_id))
    inventory_text = "\n".join([f"• {get_item_emoji(item)} {item} ×{count}" for item, count in items_dict.items()]) if items_dict else "пусто"
    await callback.message.edit_text(f"🎒 **Твой инвентарь:**\n{inventory_text}", reply_markup=back_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "open_chest")
async def open_chest_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    snimochki = get_user_snimochki(user_id)
    if snimochki < 5:
        await callback.message.edit_text("❌ Недостаточно снимочков! Сундук стоит 5 снимочков.", reply_markup=back_keyboard())
        await callback.answer()
        return
    item = open_chest()
    if item:
        update_user_snimochki(user_id, snimochki - 5)
        add_to_inventory(user_id, item["name"])
        emoji = get_item_emoji(item["name"])
        new_balance = snimochki - 5
        await callback.message.edit_text(
            f"🎁 Ты открываешь сундук...\n\n✨ Выпало: {emoji} {item['name']}\n\n🪙 Списано 5 снимочков\n💰 Новый баланс: {new_balance}\n🎒 {emoji} {item['name']} добавлен в инвентарь!",
            reply_markup=chest_result_keyboard()
        )
    else:
        await callback.message.edit_text("❌ Ошибка", reply_markup=back_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "spin")
async def spin_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    snimochki = get_user_snimochki(user_id)
    has_freespin = has_item(user_id, "один фриспин")
    if not has_freespin and snimochki < 3:
        await callback.message.edit_text("❌ Недостаточно снимочков! Испытание удачи стоит 3 снимочка.", reply_markup=back_keyboard())
        await callback.answer()
        return
    result = spin_wheel()
    new_snimochki = snimochki
    if result["type"] == "snimochki":
        new_snimochki += result["value"]
        reward_text = f"🎉 Ты выиграл: 🪙 {result['name']}!"
    elif result["type"] == "jackpot":
        new_snimochki += result["value"]
        reward_text = f"💎 ДЖЕКПОТ! {result['name']}!"
    elif result["type"] == "item":
        add_to_inventory(user_id, result["value"])
        emoji = get_item_emoji(result["value"])
        reward_text = f"🎉 Ты получил: {emoji} {result['name']}!"
    else:
        reward_text = "😢 В этот раз не повезло. Попробуй ещё!"
    if has_freespin:
        remove_from_inventory(user_id, "один фриспин")
        cost_text = "🎰 Использован фриспин!"
    else:
        new_snimochki -= 3
        cost_text = "🪙 Потрачено 3 снимочка"
    update_user_snimochki(user_id, new_snimochki)
    await callback.message.edit_text(f"🎲 Ты бросаешь кубик...\n\n{reward_text}\n\n{cost_text}\n💰 Новый баланс: {new_snimochki}", reply_markup=chest_result_keyboard())
    await callback.answer()

# ---- ЦИТАТЫ ----
@dp.message(Command("цитата"))
async def cmd_quote(message: Message):
    if message.reply_to_message:
        original_text = message.reply_to_message.text
        if not original_text:
            await message.answer("❌ В исходном сообщении нет текста для цитаты.")
            return
        author_id = message.reply_to_message.from_user.id
        author_name = message.reply_to_message.from_user.full_name
        with get_db() as conn:
            conn.execute("INSERT INTO quotes (text, author_id, author_name, date) VALUES (?, ?, ?, ?)",
                        (original_text, author_id, author_name, datetime.now().isoformat()))
            conn.commit()
        await message.answer(f"✅ Цитата от {author_name} добавлена!")
        return
    with get_db() as conn:
        cursor = conn.execute("SELECT text, author_name FROM quotes ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        if row:
            await message.answer(f"💬 *{row[0]}*\n\n— {row[1]}", parse_mode="Markdown")
        else:
            await message.answer("📭 Цитат пока нет. Добавьте первую, ответив на сообщение командой /цитата")

# ---- ЦАРЬ ССГШКИ ----
@dp.message(Command("царь"))
async def cmd_king(message: Message):
    if message.chat.type == "private":
        await message.answer("👑 Эта команда работает только в групповом чате!")
        return
    today = datetime.now().date().isoformat()
    with get_db() as conn:
        cursor = conn.execute("SELECT last_date, last_user_id FROM king WHERE id=1")
        row = cursor.fetchone()
        if row and row[0] == today:
            await message.answer("⏳ Сегодня уже выбрали царя! Приходи завтра.")
            return
        cursor = conn.execute("SELECT user_id, name FROM users_cache ORDER BY RANDOM() LIMIT 1")
        users = cursor.fetchall()
        if not users:
            await message.answer("📭 Нет активистов в базе. Попросите кого-нибудь открыть сундук или подождите синхронизации.")
            return
        king_id, king_name = users[0]
        current = get_user_snimochki(king_id)
        update_user_snimochki(king_id, current + 5)
        if row:
            conn.execute("UPDATE king SET last_date=?, last_user_id=? WHERE id=1", (today, king_id))
        else:
            conn.execute("INSERT INTO king (id, last_date, last_user_id) VALUES (1, ?, ?)", (today, king_id))
        conn.commit()
        await message.answer(f"👑 Царь ССГШки сегодня — {king_name}! +5 снимочков!")

# ============= ФОНОВАЯ СИНХРОНИЗАЦИЯ =============
async def background_sync():
    while True:
        await asyncio.sleep(60)
        try:
            sync_users_from_google()
        except Exception as e:
            logging.error(f"Ошибка фоновой синхронизации: {e}")

# ============= ЗАПУСК =============
async def main():
    init_db()
    sync_users_from_google()
    asyncio.create_task(background_sync())
    print("🚀 Бот СНИМочки запущен! Нажми Ctrl+C для остановки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
