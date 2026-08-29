import telebot
from telebot import types
import json
import os
import random
from datetime import datetime

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8658074950:AAHwVaOMhAW61ZIWeF7OU4ngaahDwSw48Co"

# ТВОЙ ID (главный владелец)
OWNER_ID = 7080227092

# ===== ПОСТОЯННЫЕ АДМИНЫ =====
PERMANENT_ADMINS = [7133785280, 6511034646, 1341766146]

TOURNAMENT_FILE = "tournament_data.json"
SAVE_FILE = "tournament_save.json"
ADMINS_FILE = "tournament_admins.json"
# =====================

bot = telebot.TeleBot(BOT_TOKEN)

# ===== РАБОТА С АДМИНАМИ =====
def load_admins():
    admins = PERMANENT_ADMINS.copy()
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            admins.extend(data.get("admins", []))
    return list(set(admins))

def save_admins(admins):
    dynamic = [a for a in admins if a not in PERMANENT_ADMINS]
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump({"admins": dynamic}, f, indent=2, ensure_ascii=False)

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    return user_id in load_admins()

def is_owner_or_admin(user_id):
    return is_owner(user_id) or is_admin(user_id)

def has_full_access(user_id):
    return is_owner(user_id)

def has_tournament_access(user_id):
    return is_owner_or_admin(user_id)

# ===== РАБОТА С ДАННЫМИ =====
def load_tournament():
    if os.path.exists(TOURNAMENT_FILE):
        with open(TOURNAMENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_tournament(data):
    with open(TOURNAMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
def get_display_name(username):
    return username.replace('@', '')

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

def show_group_table(group_data, group_name=None):
    sorted_teams = sort_teams(group_data["teams"])
    text = f"🏆 *Группа {group_name}*\n\n" if group_name else ""
    text += "```\n"
    text += f"{'Команда':<12} {'Б':<3} {'О':<3} {'В':<3} {'Н':<3} {'П':<3} {'ВР':<3} {'ПРР':<3} {'Р':<4}\n"
    text += "-" * 55 + "\n"
    for team in sorted_teams:
        name = get_display_name(team['name'])[:10]
        win_rounds = team['goals_for']
        lose_rounds = team['goals_against']
        diff = win_rounds - lose_rounds
        text += f"{name:<12} {team['played']:<3} {team['points']:<3} {team['wins']:<3} {team['draws']:<3} {team['losses']:<3} {win_rounds:<3} {lose_rounds:<3} {diff:>+3}\n"
    text += "```"
    return text

# ===== ВОССТАНОВЛЕНИЕ ТУРНИРА =====
def restore_tournament():
    data = {
        "status": "groups",
        "total_players": 32,
        "groups_count": 8,
        "players": [
            "@zero_hz", "@yary_270", "@reocopyed", "@limbibo",
            "@noobtobias", "@femfoy", "@makar_revo", "@ereneger13",
            "@erofffa", "@sh4d0w_0x", "@ale7xey", "@jimperqt",
            "@jade_leech", "@egori_ii", "@vixzow", "@krist_yout",
            "@bad_gyutar", "@ronin2033", "@stepanik12", "@a_r_t_0_0_",
            "@revolvrx", "@pasanbb", "@gyutarosol", "@red_means_",
            "@nacamaml", "@velikiyarb", "@hamster_qw", "@kapybaran7",
            "@dottoreji", "@panda20k", "@beensuch", "@krer21001"
        ],
        "groups": {
            "A": {"teams": [{"name": "@zero_hz", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@yary_270", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@reocopyed", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@limbibo", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}], "matches": [], "played": 0},
            "B": {"teams": [{"name": "@noobtobias", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@femfoy", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@makar_revo", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@ereneger13", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}], "matches": [], "played": 0},
            "C": {"teams": [{"name": "@erofffa", "points": 3, "wins": 1, "draws": 0, "losses": 0, "goals_for": 3, "goals_against": 2, "played": 1}, {"name": "@sh4d0w_0x", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@ale7xey", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@jimperqt", "points": 0, "wins": 0, "draws": 0, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 1}], "matches": [{"p1": "@erofffa", "p2": "@jimperqt", "score1": 3, "score2": 2}], "played": 1},
            "D": {"teams": [{"name": "@jade_leech", "points": 3, "wins": 1, "draws": 0, "losses": 0, "goals_for": 3, "goals_against": 2, "played": 1}, {"name": "@egori_ii", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@vixzow", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@krist_yout", "points": 0, "wins": 0, "draws": 0, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 1}], "matches": [{"p1": "@jade_leech", "p2": "@krist_yout", "score1": 3, "score2": 2}], "played": 1},
            "E": {"teams": [{"name": "@bad_gyutar", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@ronin2033", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@stepanik12", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@a_r_t_0_0_", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}], "matches": [], "played": 0},
            "F": {"teams": [{"name": "@revolvrx", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@pasanbb", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@gyutarosol", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@red_means_", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}], "matches": [], "played": 0},
            "G": {"teams": [{"name": "@nacamaml", "points": 3, "wins": 1, "draws": 0, "losses": 0, "goals_for": 2, "goals_against": 1, "played": 1}, {"name": "@velikiyarb", "points": 1, "wins": 0, "draws": 1, "losses": 0, "goals_for": 2, "goals_against": 2, "played": 1}, {"name": "@hamster_qw", "points": 1, "wins": 0, "draws": 1, "losses": 1, "goals_for": 3, "goals_against": 4, "played": 2}, {"name": "@kapybaran7", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}], "matches": [{"p1": "@nacamaml", "p2": "@hamster_qw", "score1": 2, "score2": 1}, {"p1": "@velikiyarb", "p2": "@hamster_qw", "score1": 2, "score2": 2}], "played": 2},
            "H": {"teams": [{"name": "@dottoreji", "points": 3, "wins": 1, "draws": 0, "losses": 0, "goals_for": 3, "goals_against": 2, "played": 1}, {"name": "@panda20k", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@beensuch", "points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "played": 0}, {"name": "@krer21001", "points": 0, "wins": 0, "draws": 0, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 1}], "matches": [{"p1": "@dottoreji", "p2": "@krer21001", "score1": 3, "score2": 2}], "played": 1}
        },
        "third_needed": 0,
        "playoff": None,
        "current_round": None
    }
    save_tournament(data)
    print("✅ Турнир восстановлен из сохранённых данных!")

if not os.path.exists(TOURNAMENT_FILE):
    restore_tournament()

# ============================================================
# БЛОК УПРАВЛЕНИЯ АДМИНАМИ (РАБОТАЕТ!)
# ============================================================

@bot.message_handler(commands=['fadd_admin_id'])
def add_admin_by_id(message):
    if not has_full_access(message.from_user.id):
        bot.reply_to(message, "⛔ Только владелец может добавлять админов.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/fadd_admin_id 123456789`", parse_mode="Markdown")
        return

    try:
        user_id = int(parts[1])
        if user_id == OWNER_ID:
            bot.reply_to(message, "👑 Владелец уже имеет все права!")
            return
        admins = load_admins()
        if user_id in admins:
            bot.reply_to(message, f"⚠️ Пользователь с ID {user_id} уже является админом.")
            return
        admins.append(user_id)
        save_admins(admins)
        bot.reply_to(message, f"✅ Админ с ID `{user_id}` добавлен!", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Введите корректный ID (только цифры)")

@bot.message_handler(commands=['fremove_admin_id'])
def remove_admin_by_id(message):
    if not has_full_access(message.from_user.id):
        bot.reply_to(message, "⛔ Только владелец может удалять админов.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/fremove_admin_id 123456789`", parse_mode="Markdown")
        return

    try:
        user_id = int(parts[1])
        admins = load_admins()
        if user_id not in admins:
            bot.reply_to(message, f"⚠️ Пользователь с ID {user_id} не является админом.")
            return
        admins.remove(user_id)
        save_admins(admins)
        bot.reply_to(message, f"✅ Админ с ID `{user_id}` удалён!", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Введите корректный ID (только цифры)")

@bot.message_handler(commands=['fadmins_list'])
def admins_list(message):
    if not has_full_access(message.from_user.id):
        bot.reply_to(message, "⛔ Только владелец может управлять админами!")
        return

    admins = load_admins()
    text = "👥 *СПИСОК АДМИНОВ*\n\n"
    
    try:
        owner = bot.get_chat(OWNER_ID)
        owner_name = owner.first_name or "Владелец"
        if owner.last_name:
            owner_name += f" {owner.last_name}"
        text += f"👑 *Владелец:* {owner_name}\n\n"
    except:
        text += f"👑 *Владелец:* ID: `{OWNER_ID}`\n\n"
    
    if not admins:
        text += "📭 Список админов пуст."
    else:
        text += "🛡️ *Администраторы:*\n"
        for i, admin_id in enumerate(admins, 1):
            try:
                user = bot.get_chat(admin_id)
                user_name = user.first_name or "Админ"
                if user.last_name:
                    user_name += f" {user.last_name}"
                text += f"{i}. {user_name}\n"
            except:
                text += f"{i}. ID: `{admin_id}`\n"
    
    bot.reply_to(message, text, parse_mode="Markdown")

# ============================================================
# ОСНОВНОЕ МЕНЮ
# ============================================================

@bot.message_handler(commands=['fstart'])
def start(message):
    user_id = message.from_user.id
    is_owner_or_admin_flag = has_tournament_access(user_id)
    is_owner_flag = has_full_access(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if is_owner_or_admin_flag:
        btn_create = types.KeyboardButton("🏆 Создать турнир")
        btn_add = types.KeyboardButton("➕ Добавить участника")
        btn_register = types.KeyboardButton("📋 Регистрация всех")
        btn_result = types.KeyboardButton("📝 Записать результат")
        btn_edit = types.KeyboardButton("✏️ Редактировать результат")
        btn_standings = types.KeyboardButton("📈 Таблица")
        btn_playoff = types.KeyboardButton("🏆 Плей-офф")
        markup.add(btn_create, btn_add, btn_register, btn_result, btn_edit, btn_standings, btn_playoff)
        
        if is_owner_flag:
            btn_reset = types.KeyboardButton("🔄 Сбросить турнир")
            btn_admins = types.KeyboardButton("👥 Админы")
            markup.add(btn_reset, btn_admins)
    else:
        btn_standings = types.KeyboardButton("📈 Таблица")
        btn_playoff = types.KeyboardButton("🏆 Плей-офф")
        markup.add(btn_standings, btn_playoff)

    bot.reply_to(
        message,
        "🏆 *ТУРНИРНЫЙ БОТ (f-версия)*\n\n"
        "📌 *Команды:*\n"
        "`/fcreate_tournament N` — создать турнир (16,24,32,48,64)\n"
        "`/fregister_players @u1 @u2 ...` — массовая регистрация\n"
        "`/fadd_player @user` — добавить участника\n"
        "`/fstart_groups` — запустить групповой этап\n"
        "`/fresult @u1 @u2 3:1` — записать результат\n"
        "`/fedit_result @u1 @u2 3:1` — перезаписать результат\n"
        "`/fgroups` — все группы\n"
        "`/fgroup A` — конкретная группа\n"
        "`/fplayoff` — плей-офф\n"
        "`/fresult_playoff @u1 @u2 3:1` — результат в плей-офф\n"
        "`/fresult_playoff_draw @u1 @u2 1:1 @winner` — ничья в плей-офф\n"
        "`/fgenerate_playoff` — сгенерировать все матчи плей-офф\n"
        "`/fnext_round` — следующий раунд\n"
        "`/fresult_third_place @u1 @u2 3:1` — матч за 3-е место\n"
        "`/fresult_third_place_draw @u1 @u2 1:1 @winner` — ничья за 3-е место\n"
        "`/freplace_player @старый @новый` — заменить участника\n"
        "`/fedit_playoff @u1 @u2 3:1` — перезаписать в плей-офф\n"
        "`/freplace_playoff @старый @новый` — заменить в плей-офф\n"
        "`/fsave_tournament` — сохранить турнир\n"
        "`/freset_tournament` — сбросить турнир (только владелец)\n"
        "`/fadd_admin_id` — добавить админа по ID (только владелец)\n"
        "`/fremove_admin_id` — удалить админа по ID (только владелец)\n"
        "`/fadmins_list` — список админов\n\n"
        "💡 *Поддерживаемые форматы:* 16, 24, 32, 48, 64",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ============================================================
# ГРУППОВОЙ ЭТАП (КОРОТКО)
# ============================================================

@bot.message_handler(commands=['fgroups'])
def show_groups(message):
    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Турнир не создан.")
        return

    if data["status"] not in ["groups", "playoff"]:
        bot.reply_to(message, "ℹ️ Групповой этап ещё не начался.")
        return

    text = "🏆 *ГРУППОВОЙ ЭТАП*\n\n"
    for group_name, group_data in sorted(data["groups"].items()):
        text += show_group_table(group_data, group_name) + "\n\n"

    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['fresult'])
def result(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "groups":
        bot.reply_to(message, "❌ Групповой этап не запущен.")
        return

    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(
            message,
            "❌ Используйте: `/fresult @user1 @user2 3:1`\n"
            "Например: `/fresult @ivan @petr 2:0`",
            parse_mode="Markdown"
        )
        return

    p1 = parts[1].lower()
    p2 = parts[2].lower()

    try:
        score1, score2 = map(int, parts[3].split(':'))
        if score1 < 0 or score2 < 0:
            bot.reply_to(message, "❌ Счёт не может быть отрицательным")
            return
    except ValueError:
        bot.reply_to(message, "❌ Формат счёта: 3:1")
        return

    found_group = None
    for group_name, group_data in data["groups"].items():
        team_names = [t['name'] for t in group_data["teams"]]
        if p1 in team_names and p2 in team_names:
            found_group = group_name
            break

    if not found_group:
        bot.reply_to(message, "❌ Игроки не найдены в одной группе.")
        return

    group = data["groups"][found_group]
    for match in group["matches"]:
        if (match['p1'] == p1 and match['p2'] == p2) or (match['p1'] == p2 and match['p2'] == p1):
            bot.reply_to(message, "⚠️ Этот матч уже сыгран!")
            return

    for team in group["teams"]:
        if team["name"] == p1:
            team["goals_for"] += score1
            team["goals_against"] += score2
            team["played"] += 1
            if score1 > score2:
                team["points"] += 3
                team["wins"] += 1
            elif score1 == score2:
                team["points"] += 1
                team["draws"] += 1
            else:
                team["losses"] += 1
        elif team["name"] == p2:
            team["goals_for"] += score2
            team["goals_against"] += score1
            team["played"] += 1
            if score2 > score1:
                team["points"] += 3
                team["wins"] += 1
            elif score2 == score1:
                team["points"] += 1
                team["draws"] += 1
            else:
                team["losses"] += 1

    group["matches"].append({
        "p1": p1,
        "p2": p2,
        "score1": score1,
        "score2": score2
    })
    group["played"] += 1

    save_tournament(data)

    display_p1 = get_display_name(p1)
    display_p2 = get_display_name(p2)

    bot.reply_to(
        message,
        f"✅ Результат записан!\n"
        f"{display_p1} {score1} : {score2} {display_p2}\n"
        f"📊 Группа {found_group}"
    )

@bot.message_handler(commands=['freset_tournament'])
def reset_tournament(message):
    if not has_full_access(message.from_user.id):
        bot.reply_to(message, "⛔ Только владелец может сбросить турнир!")
        return

    if os.path.exists(TOURNAMENT_FILE):
        os.remove(TOURNAMENT_FILE)
        bot.reply_to(message, "🗑️ Турнир полностью сброшен!")
    else:
        bot.reply_to(message, "ℹ️ Нет активного турнира для сброса.")

# ============================================================
# ПЛЕЙ-ОФФ (СОКРАЩЁННО)
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

    if data["status"] == "playoff":
        bot.reply_to(message, "⏳ Плей-офф уже запущен! Используйте `/fnext_round` для перехода.")
        return

    if data["status"] != "groups":
        bot.reply_to(message, "❌ Групповой этап ещё не завершён.")
        return

    bot.reply_to(
        message,
        "🏆 *ПЛЕЙ-ОФФ*\n\n"
        "⏳ Функция в разработке!\n"
        "Скоро здесь появится сетка 1/16, 1/8, 1/4, 1/2, финал и матч за 3-е место.",
        parse_mode="Markdown"
    )

# ============================================================
# ОБРАБОТЧИК КНОПОК
# ============================================================

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    is_owner_or_admin_flag = has_tournament_access(user_id)
    is_owner_flag = has_full_access(user_id)

    if message.text == "🏆 Создать турнир":
        if not is_owner_or_admin_flag:
            bot.reply_to(message, "⛔ Доступ только у администраторов.")
            return
        bot.reply_to(message, "📝 Напишите: `/fcreate_tournament N`\nНапример: `/fcreate_tournament 24`", parse_mode="Markdown")
    
    elif message.text == "➕ Добавить участника":
        if not is_owner_or_admin_flag:
            bot.reply_to(message, "⛔ Доступ только у администраторов.")
            return
        bot.reply_to(message, "📝 Напишите: `/fadd_player @username`", parse_mode="Markdown")
    
    elif message.text == "📋 Регистрация всех":
        if not is_owner_or_admin_flag:
            bot.reply_to(message, "⛔ Доступ только у администраторов.")
            return
        bot.reply_to(message, "📝 Напишите: `/fregister_players @user1 @user2 @user3 ...`", parse_mode="Markdown")
    
    elif message.text == "📝 Записать результат":
        if not is_owner_or_admin_flag:
            bot.reply_to(message, "⛔ Доступ только у администраторов.")
            return
        bot.reply_to(message, "📝 Напишите: `/fresult @user1 @user2 3:1`", parse_mode="Markdown")
    
    elif message.text == "✏️ Редактировать результат":
        if not is_owner_or_admin_flag:
            bot.reply_to(message, "⛔ Доступ только у администраторов.")
            return
        bot.reply_to(message, "📝 Напишите: `/fedit_result @user1 @user2 3:1`", parse_mode="Markdown")
    
    elif message.text == "📈 Таблица":
        show_groups(message)
    
    elif message.text == "🔄 Сбросить турнир":
        if not is_owner_flag:
            bot.reply_to(message, "⛔ Только владелец может сбросить турнир!")
            return
        reset_tournament(message)
    
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

# ===== ЗАПУСК =====
print("✅ Турнирный бот (f-версия) запущен!")
print(f"👑 Владелец: {OWNER_ID}")
print(f"🛡️ Постоянные админы: {PERMANENT_ADMINS}")
print("=" * 40)
bot.infinity_polling()
