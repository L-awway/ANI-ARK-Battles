import telebot
from telebot import types
import json
import os
import random
from datetime import datetime

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8658074950:AAHwVaOMhAW61ZIWeF7OU4ngaahDwSw48Co"
OWNER_ID = 7080227092
PERMANENT_ADMINS = [
    {"id": 7133785280, "name": "YarikFolze"},
    {"id": 6511034646, "name": "Reo-Mikage"},
    {"id": 1341766146, "name": "Art007"}
]

TOURNAMENT_FILE = "tournament_data.json"
SAVE_FILE = "tournament_save.json"
ADMINS_FILE = "tournament_admins.json"
# =====================

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# РАБОТА С АДМИНАМИ
# ============================================================

def load_admins():
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("admins", [])
        except:
            return []
    return []

def save_admins(admins):
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump({"admins": admins}, f, indent=2, ensure_ascii=False)

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    if is_owner(user_id):
        return True
    for admin in PERMANENT_ADMINS:
        if admin["id"] == user_id:
            return True
    return user_id in load_admins()

def is_owner_or_admin(user_id):
    return is_owner(user_id) or is_admin(user_id)

def has_full_access(user_id):
    return is_owner(user_id)

def has_tournament_access(user_id):
    return is_owner_or_admin(user_id)

# ============================================================
# РАБОТА С ДАННЫМИ
# ============================================================

def load_tournament():
    try:
        if os.path.exists(TOURNAMENT_FILE):
            with open(TOURNAMENT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return None

def save_tournament(data):
    with open(TOURNAMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user_name_by_id(user_id):
    try:
        user = bot.get_chat(user_id)
        name = user.first_name or "Пользователь"
        if user.last_name:
            name += f" {user.last_name}"
        return name
    except:
        return f"ID: {user_id}"

def sort_teams(teams):
    return sorted(
        teams,
        key=lambda x: (
            x['points'],
            x['goals_for'] - x['goals_against'],
            x['goals_for'],
            x['wins']
        ),
        reverse=True
    )

# ============================================================
# ВОССТАНОВЛЕНИЕ ТУРНИРА (ВСТРОЕННЫЕ ДАННЫЕ)
# ============================================================

def restore_tournament():
    data = {
        "status": "groups",
        "total_players": 32,
        "groups_count": 8,
        "players": [
            "@ZERO_HZ", "@Yary_270", "@ReoCopyed", "@Limbibo",
            "@noobtobias", "@femfoy", "@MAKAR_REVOLUTION", "@ereneger13",
            "@erofffa", "@Sh4d0w_0x", "@ale7xey", "@Jimperqt",
            "@jade_leech001", "@egori_ii", "@Vixzow", "@Krist_youtube",
            "@Bad_gyutar", "@ronin2033", "@stepanik123", "@A_r_t_0_0_7",
            "@revolvrx", "@pasanbb", "@gyutarosolo", "@Red_Means_Love",
            "@NacamaML", "@velikiyarbuz", "@Hamster_qw", "@kapybaran7",
            "@Dottoreji", "@panda20k", "@beensuch", "@krer21001"
        ],
        "groups": {
            "A": {"teams": [{"name": "@ReoCopyed", "points": 7, "wins": 2, "draws": 1, "losses": 0, "goals_for": 5, "goals_against": 3, "played": 3}, {"name": "@Yary_270", "points": 6, "wins": 2, "draws": 0, "losses": 1, "goals_for": 4, "goals_against": 3, "played": 3}, {"name": "@ZERO_HZ", "points": 4, "wins": 1, "draws": 1, "losses": 1, "goals_for": 4, "goals_against": 4, "played": 3}, {"name": "@Limbibo", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 3, "played": 3}], "matches": [], "played": 6},
            "B": {"teams": [{"name": "@femfoy", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 3, "goals_against": 0, "played": 3}, {"name": "@noobtobias", "points": 2, "wins": 0, "draws": 2, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 3}, {"name": "@MAKAR_REVOLUTION", "points": 2, "wins": 0, "draws": 2, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 3}, {"name": "@ereneger13", "points": 2, "wins": 0, "draws": 2, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 3}], "matches": [], "played": 6},
            "C": {"teams": [{"name": "@erofffa", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 9, "goals_against": 3, "played": 3}, {"name": "@Jimperqt", "points": 4, "wins": 1, "draws": 1, "losses": 1, "goals_for": 7, "goals_against": 5, "played": 3}, {"name": "@Sh4d0w_0x", "points": 4, "wins": 1, "draws": 1, "losses": 1, "goals_for": 6, "goals_against": 5, "played": 3}, {"name": "@ale7xey", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 9, "played": 3}], "matches": [], "played": 6},
            "D": {"teams": [{"name": "@egori_ii", "points": 7, "wins": 2, "draws": 1, "losses": 0, "goals_for": 8, "goals_against": 2, "played": 3}, {"name": "@jade_leech001", "points": 7, "wins": 2, "draws": 1, "losses": 0, "goals_for": 8, "goals_against": 4, "played": 3}, {"name": "@Vixzow", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 3, "goals_against": 6, "played": 3}, {"name": "@Krist_youtube", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 2, "goals_against": 9, "played": 3}], "matches": [], "played": 6},
            "E": {"teams": [{"name": "@A_r_t_0_0_7", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 9, "goals_against": 2, "played": 3}, {"name": "@ronin2033", "points": 6, "wins": 2, "draws": 0, "losses": 1, "goals_for": 8, "goals_against": 3, "played": 3}, {"name": "@stepanik123", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 3, "goals_against": 6, "played": 3}, {"name": "@Bad_Gyutaro", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 9, "played": 3}], "matches": [], "played": 6},
            "F": {"teams": [{"name": "@revolvrx", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 8, "goals_against": 0, "played": 3}, {"name": "@pasanbb", "points": 6, "wins": 2, "draws": 0, "losses": 1, "goals_for": 6, "goals_against": 2, "played": 3}, {"name": "@Red_Means_Love", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 3, "goals_against": 6, "played": 3}, {"name": "@gyutarosolo", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 9, "played": 3}], "matches": [], "played": 6},
            "G": {"teams": [{"name": "@NacamaML", "points": 7, "wins": 2, "draws": 1, "losses": 0, "goals_for": 6, "goals_against": 4, "played": 3}, {"name": "@velikiyarbuz", "points": 5, "wins": 1, "draws": 2, "losses": 0, "goals_for": 7, "goals_against": 6, "played": 3}, {"name": "@kapybaran7", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 6, "goals_against": 7, "played": 3}, {"name": "@Hamster_qw", "points": 1, "wins": 0, "draws": 1, "losses": 2, "goals_for": 5, "goals_against": 7, "played": 3}], "matches": [], "played": 6},
            "H": {"teams": [{"name": "@Dottoreji", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 9, "goals_against": 4, "played": 3}, {"name": "@panda20k", "points": 6, "wins": 2, "draws": 0, "losses": 1, "goals_for": 7, "goals_against": 4, "played": 3}, {"name": "@krer21001", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 6, "goals_against": 5, "played": 3}, {"name": "@beensuch", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 9, "played": 3}], "matches": [], "played": 6}
        },
        "third_needed": 0,
        "playoff": None,
        "current_round": None
    }
    save_tournament(data)
    print("✅ Турнир восстановлен!")

# Если файла нет — восстанавливаем
if not os.path.exists(TOURNAMENT_FILE):
    restore_tournament()

# ============================================================
# ТАБЛИЦА ГРУПП
# ============================================================

def show_group_table(group_data, group_name=None):
    sorted_teams = sort_teams(group_data["teams"])
    text = f"🏆 *Группа {group_name}*\n\n" if group_name else ""
    text += "```\n"
    text += f"{'Команда':<18} {'Б':<3} {'О':<3} {'В':<3} {'Н':<3} {'П':<3} {'ВР':<3} {'ПРР':<3} {'Р':<4}\n"
    text += "-" * 55 + "\n"
    for team in sorted_teams:
        name = team['name'][:18]
        win_rounds = team['goals_for']
        lose_rounds = team['goals_against']
        diff = win_rounds - lose_rounds
        text += f"{name:<18} {team['played']:<3} {team['points']:<3} {team['wins']:<3} {team['draws']:<3} {team['losses']:<3} {win_rounds:<3} {lose_rounds:<3} {diff:>+3}\n"
    text += "```"
    return text

@bot.message_handler(commands=['fgroups'])
def show_groups(message):
    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Турнир не создан.")
        return

    text = "🏆 *ГРУППОВОЙ ЭТАП*\n\n"
    for group_name, group_data in sorted(data["groups"].items()):
        text += show_group_table(group_data, group_name) + "\n\n"

    bot.reply_to(message, text, parse_mode="Markdown")

# ============================================================
# ОСНОВНЫЕ КОМАНДЫ
# ============================================================

@bot.message_handler(commands=['fstart'])
def start(message):
    user_id = message.from_user.id
    is_owner_or_admin_flag = has_tournament_access(user_id)
    is_owner_flag = has_full_access(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_standings = types.KeyboardButton("📈 Таблица")
    btn_playoff = types.KeyboardButton("🏆 Плей-офф")
    markup.add(btn_standings, btn_playoff)
    
    if is_owner_flag:
        btn_admins = types.KeyboardButton("👥 Админы")
        markup.add(btn_admins)

    bot.reply_to(
        message,
        "🏆 *ТУРНИРНЫЙ БОТ*\n\n"
        "📌 *Команды:*\n"
        "`/fgroups` — таблица групп\n"
        "`/fplayoff` — плей-офф\n"
        "`/fresult_playoff @u1 @u2 3:1` — результат в плей-офф\n"
        "`/fresult_playoff_draw @u1 @u2 1:1 @winner` — ничья в плей-офф\n"
        "`/fnext_round` — следующий раунд\n"
        "`/fadmins_list` — список админов",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ============================================================
# ПЛЕЙ-ОФФ (С ТОЧНЫМИ ИМЕНАМИ)
# ============================================================

@bot.message_handler(commands=['fplayoff'])
def start_playoff(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Турнир не найден.")
        return

    if data["status"] == "playoff" and data.get("playoff"):
        show_playoff(message, data)
        return

    if data["status"] != "groups":
        bot.reply_to(message, "❌ Групповой этап ещё не завершён.")
        return

    # Проверяем, все ли матчи сыграны
    all_played = True
    for group_data in data["groups"].values():
        teams = len(group_data["teams"])
        expected = teams * (teams - 1) // 2
        if group_data["played"] < expected:
            all_played = False
            break

    if not all_played:
        bot.reply_to(
            message,
            "⚠️ *НЕ ВСЕ МАТЧИ СЫГРАНЫ!*\n\n"
            "Заполните все результаты в группах командой `/fresult`",
            parse_mode="Markdown"
        )
        return

    # ТОЧНЫЕ ИМЕНА из твоих групп (вручную)
    pairs = [
        {"p1": "@ReoCopyed", "p2": "@Sh4d0w_0x", "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "A"},
        {"p1": "@erofffa", "p2": "@jade_leech001", "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "B"},
        {"p1": "@femfoy", "p2": "@Yary_270", "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "C"},
        {"p1": "@egori_ii", "p2": "@Jimperqt", "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "D"},
        {"p1": "@A_r_t_0_0_7", "p2": "@pasanbb", "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "E"},
        {"p1": "@NacamaML", "p2": "@panda20k", "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "F"},
        {"p1": "@revolvrx", "p2": "@ronin2033", "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "G"},
        {"p1": "@Dottoreji", "p2": "@velikiyarbuz", "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "H"}
    ]

    data["status"] = "playoff"
    data["playoff"] = {
        "round": "1/8",
        "pairs": pairs,
        "winners": {},
        "quarter_winners": {},
        "third_place": None,
        "history": {}
    }
    save_tournament(data)

    show_playoff(message, data)

def show_playoff(message, data):
    playoff = data.get("playoff")
    if not playoff:
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    text = f"🏆 *ПЛЕЙ-ОФФ: {playoff['round'].upper()}*\n\n"

    for i, pair in enumerate(playoff["pairs"], 1):
        p1 = pair["p1"] or "?"
        p2 = pair["p2"] or "?"
        if pair["winner"]:
            winner = pair["winner"]
            status = f"✅ {pair['score1']}:{pair['score2']} → {winner}"
        else:
            status = "⏳ Не сыгран"
        label = pair.get("label", "")
        label_text = f" [{label}]" if label else ""
        text += f"🔥 {i}. {p1} — {p2}{label_text} | {status}\n"

    text += "\n📝 Команды:\n"
    text += "`/fresult_playoff @user1 @user2 3:1`\n"
    text += "`/fnext_round` — следующий раунд"

    bot.reply_to(message, text, parse_mode="Markdown")
# ============================================================
# КОМАНДА ДЛЯ ТРЕТЬЕГО МЕСТА
# ============================================================

@bot.message_handler(commands=['fresult_third_place'])
def result_third_place(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    playoff = data["playoff"]
    if not playoff.get("third_place"):
        bot.reply_to(message, "❌ Матч за 3-е место не найден.")
        return

    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, "❌ Используйте: `/fresult_third_place @user1 @user2 3:1`", parse_mode="Markdown")
        return

    p1 = parts[1]
    p2 = parts[2]

    try:
        score1, score2 = map(int, parts[3].split(':'))
        if score1 < 0 or score2 < 0:
            bot.reply_to(message, "❌ Счёт не может быть отрицательным")
            return
    except ValueError:
        bot.reply_to(message, "❌ Формат счёта: 3:1")
        return

    third = playoff["third_place"]
    if third["winner"]:
        bot.reply_to(message, "⚠️ Матч за 3-е место уже сыгран.")
        return

    if (third["p1"] != p1 and third["p1"] != p2) or (third["p2"] != p1 and third["p2"] != p2):
        bot.reply_to(message, "❌ Игроки не участвуют в матче за 3-е место.")
        return

    if score1 > score2:
        third["winner"] = third["p1"]
    elif score2 > score1:
        third["winner"] = third["p2"]
    else:
        bot.reply_to(message, "⚠️ Ничья! Используйте `/fresult_third_place_draw`", parse_mode="Markdown")
        return

    third["score1"] = score1
    third["score2"] = score2
    save_tournament(data)

    bot.reply_to(
        message,
        f"🥉 *Матч за 3-е место*\n"
        f"{third['p1']} {score1} : {score2} {third['p2']}\n"
        f"🥉 3-е место: {third['winner']}"
    )

@bot.message_handler(commands=['fresult_third_place_draw'])
def result_third_place_draw(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    playoff = data["playoff"]
    if not playoff.get("third_place"):
        bot.reply_to(message, "❌ Матч за 3-е место не найден.")
        return

    parts = message.text.split()
    if len(parts) < 5:
        bot.reply_to(message, "❌ Используйте: `/fresult_third_place_draw @user1 @user2 1:1 @winner`", parse_mode="Markdown")
        return

    p1 = parts[1]
    p2 = parts[2]

    try:
        score1, score2 = map(int, parts[3].split(':'))
    except ValueError:
        bot.reply_to(message, "❌ Формат счёта: 1:1")
        return

    winner = parts[4]
    if not winner.startswith('@'):
        bot.reply_to(message, "❌ Укажите победителя: @username")
        return

    third = playoff["third_place"]
    if third["winner"]:
        bot.reply_to(message, "⚠️ Матч уже сыгран.")
        return

    if winner != p1 and winner != p2:
        bot.reply_to(message, "❌ Победитель должен быть одним из участников.")
        return

    third["winner"] = winner
    third["score1"] = score1
    third["score2"] = score2
    save_tournament(data)

    bot.reply_to(
        message,
        f"🥉 *Матч за 3-е место*\n"
        f"{third['p1']} {score1} : {score2} {third['p2']}\n"
        f"🥉 3-е место: {winner}"
    )

# ============================================================
# АДМИНЫ
# ============================================================

@bot.message_handler(commands=['fadmins_list'])
def admins_list(message):
    if not has_full_access(message.from_user.id):
        bot.reply_to(message, "⛔ Только владелец может управлять админами!")
        return

    admins = load_admins()
    text = "👥 *СПИСОК АДМИНОВ*\n\n"
    text += f"👑 *Владелец:* {get_user_name_by_id(OWNER_ID)}\n\n"
    if PERMANENT_ADMINS:
        text += "🔒 *Постоянные админы:*\n"
        for admin in PERMANENT_ADMINS:
            text += f"• {admin['name']}\n"
        text += "\n"
    if not admins:
        text += "📭 Добавленных админов нет."
    else:
        text += "➕ *Добавленные админы:*\n"
        for i, admin_id in enumerate(admins, 1):
            try:
                user = bot.get_chat(admin_id)
                name = user.first_name or "Пользователь"
                if user.last_name:
                    name += f" {user.last_name}"
                text += f"{i}. {name}\n"
            except:
                text += f"{i}. ID: `{admin_id}`\n"
    bot.reply_to(message, text, parse_mode="Markdown")

# ============================================================
# КНОПКИ
# ============================================================

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    is_owner_or_admin_flag = has_tournament_access(user_id)
    is_owner_flag = has_full_access(user_id)

    if message.text == "📈 Таблица":
        show_groups(message)
    elif message.text == "🏆 Плей-офф":
        if not is_owner_or_admin_flag:
            bot.reply_to(message, "⛔ Доступ только у администраторов.")
            return
        start_playoff(message)
    elif message.text == "👥 Админы":
        if not is_owner_flag:
            bot.reply_to(message, "⛔ Только владелец может управлять админами!")
            return
        admins_list(message)

# ============================================================
# ЗАПУСК
# ============================================================

print("✅ Турнирный бот запущен!")
print("=" * 40)
bot.infinity_polling()
