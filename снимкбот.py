import logging
import sqlite3
import random
import asyncio
import json
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
SPREADSHEET_ID = "1oMohwWx3xIEt9N_s9NXMAerKM4JReqVLozadPC52ZJA"
# =====================================

# ============= КЛЮЧ =============
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
# =====================================

# ============= СМАЙЛИКИ =============
ITEM_EMOJIS = {
    "кепка": "🧢", "носки": "🧦", "кружка": "☕", "брелок": "🔑",
    "стикеры": "🎨", "снимочков": "🪙", "снимочки": "🪙", "ТЗ": "⏰",
    "статус": "📝", "опоздать": "⏳", "бонусный сундук": "🎁",
    "фото": "📸", "фриспин": "🎰", "музыку": "🎵", "джекпот": "💎",
}
# =====================================

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
        
        cursor = conn.execute("SELECT COUNT(*) FROM quotes")
        if cursor.fetchone()[0] == 0:
            sample = [
                ("А я думал, дедлайн — это имя!", 1, "Admin", datetime.now().isoformat()),
                ("Студсовет — это семья, где все друг друга крышуют", 1, "Admin", datetime.now().isoformat()),
            ]
            for text, aid, aname, date in sample:
                conn.execute("INSERT INTO quotes (text, author_id, author_name, date) VALUES (?, ?, ?, ?)",
                           (text, aid, aname, date))
            conn.commit()

# ============= GOOGLE SHEETS (фоновая запись) =============
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

def sync_to_google(user_id, new_value):
    """Синхронная отправка в Google (выполняется в отдельном потоке)"""
    client = get_gs_client()
    if not client:
        return
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

def update_user_snimochki(user_id, new_value):
    """Мгновенно обновляет кэш, в Google отправляет в фоне"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users_cache SET snimochki=? WHERE user_id=?", (new_value, user_id))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO users_cache (user_id, name, brs, snimochki) VALUES (?, ?, ?, ?)",
                          (user_id, f"User{user_id}", 0, new_value))
        conn.commit()
    
    async def bg():
        await asyncio.to_thread(sync_to_google, user_id, new_value)
    asyncio.create_task(bg())

def get_user_snimochki(user_id):
    with get_db() as conn:
        cursor = conn.execute("SELECT snimochki FROM users_cache WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 0

def sync_users_from_google():
    """Фоновая синхронизация всей таблицы (раз в минуту)"""
    client = get_gs_client()
    if not client:
        return
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("users")
        all_rows = sheet.get_all_values()
        if len(all_rows) < 2:
            return
        with get_db() as conn:
            conn.execute("DELETE FROM users_cache")
            for row in all_rows[1:]:
                if len(row) >= 4 and row[0].strip().isdigit():
                    uid = int(row[0])
                    name = row[1] if len(row) > 1 else f"User{uid}"
                    brs = int(row[2]) if len(row) > 2 and row[2].isdigit() else 0
                    snim = int(row[3]) if len(row) > 3 and row[3].lstrip('-').isdigit() else 0
                    conn.execute("INSERT INTO users_cache (user_id, name, brs, snimochki) VALUES (?, ?, ?, ?)",
                                (uid, name, brs, snim))
            conn.commit()
        logging.info("✅ Кэш обновлён из Google")
    except Exception as e:
        logging.error(f"❌ Ошибка синхронизации: {e}")

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
    groups = {}
    for it in items:
        groups.setdefault(it["rarity"], []).append(it)
    r = random.random()
    cum = 0
    sel = "обычный"
    for rarity, chance in rarity_chances.items():
        cum += chance
        if r < cum:
            sel = rarity
            break
    return random.choice(groups[sel]) if sel in groups else None

def spin_wheel():
    r = random.randint(1, 100)
    if r <= 50:
        return {"type": "snimochki", "value": 5, "name": "+5 снимочков"}
    elif r <= 65:
        return {"type": "item", "value": "кепка \"СНИМК\"", "name": "кепка \"СНИМК\""}
    elif r <= 75:
        return {"type": "snimochki", "value": 10, "name": "+10 снимочков"}
    elif r <= 85:
        return {"type": "nothing", "value": 0, "name": "ничего"}
    elif r <= 90:
        return {"type": "item", "value": "5 снимочков", "name": "5 снимочков (бонус)"}
    elif r <= 95:
        return {"type": "snimochki", "value": 15, "name": "+15 снимочков"}
    elif r <= 99:
        return {"type": "item", "value": "бонусный сундук", "name": "бонусный сундук"}
    else:
        return {"type": "jackpot", "value": 50, "name": "ДЖЕКПОТ! +50 снимочков"}

# ============= ИНВЕНТАРЬ =============
def get_inventory(user_id):
    with get_db() as conn:
        cur = conn.execute("SELECT items FROM inventory WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else ""

def update_inventory(user_id, items_dict):
    s = ",".join([f"{k}:{v}" for k, v in items_dict.items()])
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO inventory (user_id, items) VALUES (?, ?)", (user_id, s))
        conn.commit()

def parse_inventory(s):
    if not s:
        return {}
    res = {}
    for part in s.split(','):
        if ':' in part:
            name, cnt = part.split(':')
            res[name] = int(cnt)
    return res

def add_to_inventory(uid, name, cnt=1):
    d = parse_inventory(get_inventory(uid))
    d[name] = d.get(name, 0) + cnt
    update_inventory(uid, d)

def remove_from_inventory(uid, name, cnt=1):
    d = parse_inventory(get_inventory(uid))
    if name in d and d[name] >= cnt:
        d[name] -= cnt
        if d[name] <= 0:
            del d[name]
        update_inventory(uid, d)
        return True
    return False

def has_item(uid, name):
    return name in parse_inventory(get_inventory(uid))

def get_item_emoji(name):
    for k, em in ITEM_EMOJIS.items():
        if k in name.lower():
            return em
    return "📦"

# ============= КЛАВИАТУРЫ =============
def main_menu():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🎁 Открыть сундук (5)", callback_data="open_chest"),
          InlineKeyboardButton(text="🎲 Испытать удачу (3)", callback_data="spin"))
    b.row(InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
          InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inventory"))
    return b.as_markup()

def back():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="◀️ В меню", callback_data="menu"))
    return b.as_markup()

def chest_result():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🎁 Ещё сундук", callback_data="open_chest"),
          InlineKeyboardButton(text="🎲 Ещё удачу", callback_data="spin"))
    b.row(InlineKeyboardButton(text="◀️ В меню", callback_data="menu"))
    return b.as_markup()

# ============= КОМАНДЫ =============
@dp.message(Command("start"))
async def start_cmd(m: Message):
    uid = m.from_user.id
    name = m.from_user.full_name
    sn = get_user_snimochki(uid)
    await m.answer(f"👋 Привет, {name}!\n\n🪙 Твои снимочки: {sn}\n\n🎮 Выбери действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "menu")
async def menu_cb(cb: CallbackQuery):
    uid = cb.from_user.id
    name = cb.from_user.full_name
    sn = get_user_snimochki(uid)
    await cb.message.edit_text(f"👋 Привет, {name}!\n\n🪙 Твои снимочки: {sn}\n\n🎮 Выбери действие:", reply_markup=main_menu())
    await cb.answer()

@dp.callback_query(lambda c: c.data == "profile")
async def profile_cb(cb: CallbackQuery):
    uid = cb.from_user.id
    name = cb.from_user.full_name
    sn = get_user_snimochki(uid)
    inv = parse_inventory(get_inventory(uid))
    txt = "\n".join([f"• {get_item_emoji(it)} {it} ×{cnt}" for it, cnt in inv.items()]) if inv else "пусто"
    await cb.message.edit_text(f"👤 **{name}**\n🪙 Снимочки: {sn}\n\n🎒 **Инвентарь:**\n{txt}", reply_markup=back(), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(lambda c: c.data == "inventory")
async def inv_cb(cb: CallbackQuery):
    uid = cb.from_user.id
    inv = parse_inventory(get_inventory(uid))
    txt = "\n".join([f"• {get_item_emoji(it)} {it} ×{cnt}" for it, cnt in inv.items()]) if inv else "пусто"
    await cb.message.edit_text(f"🎒 **Твой инвентарь:**\n{txt}", reply_markup=back(), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(lambda c: c.data == "open_chest")
async def open_cb(cb: CallbackQuery):
    uid = cb.from_user.id
    sn = get_user_snimochki(uid)
    if sn < 5:
        await cb.message.edit_text("❌ Недостаточно снимочков! Сундук стоит 5.", reply_markup=back())
        await cb.answer()
        return
    item = open_chest()
    if item:
        update_user_snimochki(uid, sn - 5)
        add_to_inventory(uid, item["name"])
        em = get_item_emoji(item["name"])
        new_sn = sn - 5
        await cb.message.edit_text(
            f"🎁 Ты открываешь сундук...\n\n✨ Выпало: {em} {item['name']}\n\n🪙 Списано 5 снимочков\n💰 Новый баланс: {new_sn}\n🎒 {em} {item['name']} добавлен в инвентарь!",
            reply_markup=chest_result()
        )
    else:
        await cb.message.edit_text("❌ Ошибка", reply_markup=back())
    await cb.answer()

@dp.callback_query(lambda c: c.data == "spin")
async def spin_cb(cb: CallbackQuery):
    uid = cb.from_user.id
    sn = get_user_snimochki(uid)
    free = has_item(uid, "один фриспин")
    if not free and sn < 3:
        await cb.message.edit_text("❌ Недостаточно снимочков! Испытание удачи стоит 3.", reply_markup=back())
        await cb.answer()
        return
    res = spin_wheel()
    new_sn = sn
    if res["type"] == "snimochki":
        new_sn += res["value"]
        reward = f"🎉 Ты выиграл: 🪙 {res['name']}!"
    elif res["type"] == "jackpot":
        new_sn += res["value"]
        reward = f"💎 ДЖЕКПОТ! {res['name']}!"
    elif res["type"] == "item":
        add_to_inventory(uid, res["value"])
        em = get_item_emoji(res["value"])
        reward = f"🎉 Ты получил: {em} {res['name']}!"
    else:
        reward = "😢 В этот раз не повезло. Попробуй ещё!"
    if free:
        remove_from_inventory(uid, "один фриспин")
        cost = "🎰 Использован фриспин!"
    else:
        new_sn -= 3
        cost = "🪙 Потрачено 3 снимочка"
    update_user_snimochki(uid, new_sn)
    await cb.message.edit_text(f"🎲 Ты бросаешь кубик...\n\n{reward}\n\n{cost}\n💰 Новый баланс: {new_sn}", reply_markup=chest_result())
    await cb.answer()

# ============= ЦИТАТЫ =============
@dp.message(Command("цитата"))
async def quote_cmd(m: Message):
    if m.reply_to_message:
        txt = m.reply_to_message.text
        if not txt:
            await m.answer("❌ В исходном сообщении нет текста.")
            return
        aid = m.reply_to_message.from_user.id
        aname = m.reply_to_message.from_user.full_name
        with get_db() as conn:
            conn.execute("INSERT INTO quotes (text, author_id, author_name, date) VALUES (?, ?, ?, ?)",
                        (txt, aid, aname, datetime.now().isoformat()))
            conn.commit()
        await m.answer(f"✅ Цитата от {aname} добавлена!")
        return
    with get_db() as conn:
        cur = conn.execute("SELECT text, author_name FROM quotes ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        if row:
            await m.answer(f"💬 *{row[0]}*\n\n— {row[1]}", parse_mode="Markdown")
        else:
            await m.answer("📭 Цитат пока нет. Добавьте первую, ответив на сообщение командой /цитата")

# ============= ЦАРЬ ССГШКИ =============
@dp.message(Command("царь"))
async def king_cmd(m: Message):
    if m.chat.type == "private":
        await m.answer("👑 Эта команда работает только в групповом чате!")
        return
    today = datetime.now().date().isoformat()
    with get_db() as conn:
        cur = conn.execute("SELECT last_date, last_user_id FROM king WHERE id=1")
        row = cur.fetchone()
        if row and row[0] == today:
            await m.answer("⏳ Сегодня уже выбрали царя! Приходи завтра.")
            return
        cur = conn.execute("SELECT user_id, name FROM users_cache ORDER BY RANDOM() LIMIT 1")
        users = cur.fetchall()
        if not users:
            await m.answer("📭 Нет активистов в базе. Попросите кого-нибудь открыть сундук.")
            return
        kid, kname = users[0]
        cur_sn = get_user_snimochki(kid)
        update_user_snimochki(kid, cur_sn + 5)
        if row:
            conn.execute("UPDATE king SET last_date=?, last_user_id=? WHERE id=1", (today, kid))
        else:
            conn.execute("INSERT INTO king (id, last_date, last_user_id) VALUES (1, ?, ?)", (today, kid))
        conn.commit()
        await m.answer(f"👑 Царь ССГШки сегодня — {kname}! +5 снимочков!")

# ============= ФОН =============
async def bg_sync():
    while True:
        await asyncio.sleep(60)
        try:
            sync_users_from_google()
        except Exception as e:
            logging.error(f"Ошибка синхронизации: {e}")

async def main():
    init_db()
    sync_users_from_google()
    asyncio.create_task(bg_sync())
    print("🚀 Бот СНИМочки запущен! Нажми Ctrl+C для остановки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
