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

# ============================================================
# РАБОТА С АДМИНАМИ (ПОЛНОСТЬЮ ПЕРЕПИСАНО)
# ============================================================

def load_admins():
    """Загружает список админов из файла"""
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("admins", [])
        except:
            return []
    return []

def save_admins(admins):
    """Сохраняет список админов в файл"""
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump({"admins": admins}, f, indent=2, ensure_ascii=False)

def is_owner(user_id):
    """Проверяет, является ли пользователь владельцем"""
    return user_id == OWNER_ID

def is_admin(user_id):
    """Проверяет, является ли пользователь админом (включая постоянных)"""
    if user_id == OWNER_ID:
        return True
    if user_id in PERMANENT_ADMINS:
        return True
    return user_id in load_admins()

def is_owner_or_admin(user_id):
    """Проверяет, является ли пользователь владельцем или админом"""
    return is_owner(user_id) or is_admin(user_id)

def has_full_access(user_id):
    """Только владелец имеет полный доступ"""
    return is_owner(user_id)

def has_tournament_access(user_id):
    """Админы и владелец могут управлять турниром"""
    return is_owner_or_admin(user_id)

# ============================================================
# КОМАНДЫ УПРАВЛЕНИЯ АДМИНАМИ
# ============================================================

@bot.message_handler(commands=['fadd_admin_id'])
def add_admin_by_id(message):
    """Добавляет админа по ID (только владелец)"""
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
    """Удаляет админа по ID (только владелец)"""
    if not has_full_access(message.from_user.id):
        bot.reply_to(message, "⛔ Только владелец может удалять админов.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/fremove_admin_id 123456789`", parse_mode="Markdown")
        return

    try:
        user_id = int(parts[1])
        if user_id == OWNER_ID:
            bot.reply_to(message, "👑 Владельца нельзя удалить!")
            return
        
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
    """Показывает список админов (только владелец)"""
    if not has_full_access(message.from_user.id):
        bot.reply_to(message, "⛔ Только владелец может управлять админами!")
        return

    admins = load_admins()
    text = "👥 *СПИСОК АДМИНОВ*\n\n"
    
    # Показываем владельца
    try:
        owner = bot.get_chat(OWNER_ID)
        owner_name = owner.first_name or "Владелец"
        if owner.last_name:
            owner_name += f" {owner.last_name}"
        text += f"👑 *Владелец:* {owner_name}\n\n"
    except:
        text += f"👑 *Владелец:* ID: `{OWNER_ID}`\n\n"
    
    # Показываем постоянных админов
    if PERMANENT_ADMINS:
        text += "🔒 *Постоянные админы:*\n"
        for admin_id in PERMANENT_ADMINS:
            try:
                user = bot.get_chat(admin_id)
                user_name = user.first_name or "Админ"
                if user.last_name:
                    user_name += f" {user.last_name}"
                text += f"• {user_name}\n"
            except:
                text += f"• ID: `{admin_id}`\n"
        text += "\n"
    
    # Показываем динамических админов
    if not admins:
        text += "📭 Список добавленных админов пуст.\n"
        text += "ℹ️ Чтобы добавить админа: `/fadd_admin_id 123456789`"
    else:
        text += "➕ *Добавленные админы:*\n"
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
# РАБОТА С ТУРНИРОМ
# ============================================================

def load_tournament():
    if os.path.exists(TOURNAMENT_FILE):
        with open(TOURNAMENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_tournament(data):
    with open(TOURNAMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

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

# ============================================================
# ВОССТАНОВЛЕНИЕ ТУРНИРА
# ============================================================

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
# ГРУППОВОЙ ЭТАП
# ============================================================

@bot.message_handler(commands=['fcreate_tournament'])
def create_tournament(message):
    user_id = message.from_user.id
    if not has_tournament_access(user_id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    existing = load_tournament()
    if existing:
        bot.reply_to(
            message,
            "⚠️ *Турнир уже существует!*\n\n"
            "Чтобы создать новый, сначала сбросьте старый:\n"
            "`/freset_tournament` (только владелец)",
            parse_mode="Markdown"
        )
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/fcreate_tournament N`\nНапример: `/fcreate_tournament 24`", parse_mode="Markdown")
        return

    try:
        total = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ Введите число")
        return

    supported = [16, 24, 32, 48, 64]
    if total not in supported:
        bot.reply_to(
            message,
            f"❌ Поддерживаются только: {', '.join(map(str, supported))}\n"
            f"Ваше число: {total}",
            parse_mode="Markdown"
        )
        return

    if total % 4 != 0:
        bot.reply_to(message, "❌ Число должно быть кратно 4")
        return

    groups_count = total // 4
    total_playoff = groups_count * 2
    powers = [8, 16, 32, 64]
    target = next(p for p in powers if p >= total_playoff)
    third_needed = target - total_playoff

    if third_needed > groups_count:
        bot.reply_to(
            message,
            f"⚠️ Для {total} участников нужно {third_needed} команд с 3-х мест, "
            f"но доступно только {groups_count}. Попробуйте другое число."
        )
        return

    data = {
        "status": "waiting",
        "total_players": total,
        "groups_count": groups_count,
        "players": [],
        "groups": {},
        "third_needed": third_needed,
        "playoff": None,
        "current_round": None
    }

    for i in range(groups_count):
        letter = chr(65 + i)
        data["groups"][letter] = {
            "teams": [],
            "matches": [],
            "played": 0
        }

    save_tournament(data)
    bot.reply_to(
        message,
        f"🏆 *Турнир создан!*\n"
        f"📊 Участников: {total}\n"
        f"📋 Групп: {groups_count}\n"
        f"📌 Статус: ожидание участников\n\n"
        f"➕ Добавьте участников: `/fregister_players @user1 @user2 ...`",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['fstart_groups'])
def start_groups(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Сначала создайте турнир.")
        return

    if data["status"] != "waiting":
        bot.reply_to(message, "❌ Турнир уже запущен.")
        return

    if len(data["players"]) < data["total_players"]:
        bot.reply_to(
            message,
            f"❌ Недостаточно участников!\n"
            f"Добавлено: {len(data['players'])}\n"
            f"Нужно: {data['total_players']}"
        )
        return

    players = data["players"].copy()
    random.shuffle(players)

    group_size = data["total_players"] // data["groups_count"]

    for i, group_letter in enumerate(sorted(data["groups"].keys())):
        start = i * group_size
        end = start + group_size
        group_players = players[start:end]

        for player in group_players:
            data["groups"][group_letter]["teams"].append({
                "name": player,
                "points": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "played": 0
            })

    data["status"] = "groups"
    save_tournament(data)

    text = "🏆 *ГРУППОВОЙ ЭТАП ЗАПУЩЕН!*\n\n"
    for group_name, group_data in data["groups"].items():
        team_names = [get_display_name(t['name']) for t in group_data["teams"]]
        text += f"📋 *Группа {group_name}:* {', '.join(team_names)}\n"

    text += "\n📝 Записывайте результаты: `/fresult @user1 @user2 3:1`"
    bot.reply_to(message, text, parse_mode="Markdown")

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

@bot.message_handler(commands=['fgroup'])
def show_group(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/fgroup A`\nНапример: `/fgroup A`", parse_mode="Markdown")
        return

    group_letter = parts[1].upper()
    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Турнир не создан.")
        return

    if group_letter not in data["groups"]:
        bot.reply_to(message, f"❌ Группа {group_letter} не найдена.")
        return

    group_data = data["groups"][group_letter]
    text = show_group_table(group_data, group_letter)

    if group_data["matches"]:
        text += "\n📝 *Сыгранные матчи:*\n"
        for match in group_data["matches"]:
            p1 = get_display_name(match['p1'])
            p2 = get_display_name(match['p2'])
            text += f"{p1} {match['score1']} : {match['score2']} {p2}\n"

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
    found_p1 = None
    found_p2 = None
    
    for group_name, group_data in data["groups"].items():
        # Приводим все имена к нижнему регистру для поиска
        team_names_lower = [t['name'].lower() for t in group_data["teams"]]
        if p1 in team_names_lower and p2 in team_names_lower:
            found_group = group_name
            # Находим оригинальные имена
            for team in group_data["teams"]:
                if team['name'].lower() == p1:
                    found_p1 = team['name']
                if team['name'].lower() == p2:
                    found_p2 = team['name']
            break

    if not found_group:
        bot.reply_to(message, "❌ Игроки не найдены в одной группе.\n\nПроверьте написание: имена должны быть как в таблице.\nПример: `/fresult @nacamaml @velikiyarb 2:2`", parse_mode="Markdown")
        return

    group = data["groups"][found_group]
    
    # Проверяем, не сыгран ли уже матч
    for match in group["matches"]:
        if (match['p1'].lower() == p1 and match['p2'].lower() == p2) or (match['p1'].lower() == p2 and match['p2'].lower() == p1):
            bot.reply_to(message, "⚠️ Этот матч уже сыгран!")
            return

    # Обновляем статистику (используем оригинальные имена)
    for team in group["teams"]:
        if team["name"].lower() == p1:
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
        elif team["name"].lower() == p2:
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
        "p1": found_p1,
        "p2": found_p2,
        "score1": score1,
        "score2": score2
    })
    group["played"] += 1

    save_tournament(data)

    display_p1 = get_display_name(found_p1)
    display_p2 = get_display_name(found_p2)

    bot.reply_to(
        message,
        f"✅ Результат записан!\n"
        f"{display_p1} {score1} : {score2} {display_p2}\n"
        f"📊 Группа {found_group}"
    )
    
@bot.message_handler(commands=['fedit_result'])
def edit_result(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "groups":
        bot.reply_to(message, "❌ Групповой этап не запущен.")
        return

    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, "❌ Используйте: `/fedit_result @user1 @user2 3:1`", parse_mode="Markdown")
        return

    p1 = parts[1].lower()
    p2 = parts[2].lower()

    try:
        new_score1, new_score2 = map(int, parts[3].split(':'))
        if new_score1 < 0 or new_score2 < 0:
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
    old_match = None
    for match in group["matches"]:
        if (match['p1'] == p1 and match['p2'] == p2) or (match['p1'] == p2 and match['p2'] == p1):
            old_match = match
            break

    if not old_match:
        bot.reply_to(message, "❌ Матч не найден.")
        return

    old_score1 = old_match["score1"]
    old_score2 = old_match["score2"]

    for team in group["teams"]:
        if team["name"] == p1:
            team["goals_for"] -= old_score1
            team["goals_against"] -= old_score2
            team["played"] -= 1
            if old_score1 > old_score2:
                team["points"] -= 3
                team["wins"] -= 1
            elif old_score1 == old_score2:
                team["points"] -= 1
                team["draws"] -= 1
            else:
                team["losses"] -= 1
        elif team["name"] == p2:
            team["goals_for"] -= old_score2
            team["goals_against"] -= old_score1
            team["played"] -= 1
            if old_score2 > old_score1:
                team["points"] -= 3
                team["wins"] -= 1
            elif old_score2 == old_score1:
                team["points"] -= 1
                team["draws"] -= 1
            else:
                team["losses"] -= 1

    for team in group["teams"]:
        if team["name"] == p1:
            team["goals_for"] += new_score1
            team["goals_against"] += new_score2
            team["played"] += 1
            if new_score1 > new_score2:
                team["points"] += 3
                team["wins"] += 1
            elif new_score1 == new_score2:
                team["points"] += 1
                team["draws"] += 1
            else:
                team["losses"] += 1
        elif team["name"] == p2:
            team["goals_for"] += new_score2
            team["goals_against"] += new_score1
            team["played"] += 1
            if new_score2 > new_score1:
                team["points"] += 3
                team["wins"] += 1
            elif new_score2 == new_score1:
                team["points"] += 1
                team["draws"] += 1
            else:
                team["losses"] += 1

    old_match["score1"] = new_score1
    old_match["score2"] = new_score2

    save_tournament(data)

    display_p1 = get_display_name(p1)
    display_p2 = get_display_name(p2)

    bot.reply_to(
        message,
        f"✏️ Результат изменён!\n"
        f"{display_p1} {old_score1}:{old_score2} {display_p2} → {new_score1}:{new_score2}\n"
        f"📊 Группа {found_group}"
    )

@bot.message_handler(commands=['fadd_player'])
def add_player(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Сначала создайте турнир: /fcreate_tournament")
        return

    if data["status"] != "waiting":
        bot.reply_to(message, "❌ Турнир уже начался! Нельзя добавлять участников.")
        return

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].startswith('@'):
        bot.reply_to(message, "❌ Используйте: `/fadd_player @username`", parse_mode="Markdown")
        return

    username = parts[1].lower()

    if username in data["players"]:
        bot.reply_to(message, f"⚠️ {username} уже добавлен.")
        return

    if len(data["players"]) >= data["total_players"]:
        bot.reply_to(message, f"❌ Турнир заполнен! Максимум: {data['total_players']}")
        return

    data["players"].append(username)
    save_tournament(data)

    remaining = data["total_players"] - len(data["players"])
    bot.reply_to(
        message,
        f"✅ Добавлен: {username}\n"
        f"📊 Всего: {len(data['players'])}/{data['total_players']}\n"
        f"📌 Осталось: {remaining}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['fregister_players'])
def register_players(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Сначала создайте турнир: /fcreate_tournament")
        return

    if data["status"] != "waiting":
        bot.reply_to(message, "❌ Турнир уже начался! Нельзя добавлять участников.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/fregister_players @user1 @user2 @user3 ...`", parse_mode="Markdown")
        return

    new_players = []
    for p in parts[1:]:
        if p.startswith('@'):
            username = p.lower()
            if username not in data["players"] and len(data["players"]) < data["total_players"]:
                data["players"].append(username)
                new_players.append(username)

    if not new_players:
        bot.reply_to(message, "⚠️ Никто не добавлен. Возможно, все уже зарегистрированы или турнир заполнен.")
        return

    save_tournament(data)
    remaining = data["total_players"] - len(data["players"])
    bot.reply_to(
        message,
        f"✅ Добавлено {len(new_players)} участников!\n"
        f"📊 Всего: {len(data['players'])}/{data['total_players']}\n"
        f"📌 Осталось: {remaining}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['freplace_player'])
def replace_player(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Турнир не найден.")
        return

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "❌ Используйте: `/freplace_player @старый @новый`", parse_mode="Markdown")
        return

    old_name = parts[1].lower()
    new_name = parts[2].lower()

    if not old_name.startswith('@') or not new_name.startswith('@'):
        bot.reply_to(message, "❌ Оба должны быть @username")
        return

    found = False
    if old_name in data["players"]:
        data["players"] = [new_name if x == old_name else x for x in data["players"]]
        found = True

    for group_data in data["groups"].values():
        for team in group_data["teams"]:
            if team["name"] == old_name:
                team["name"] = new_name
                found = True
        for match in group_data["matches"]:
            if match["p1"] == old_name:
                match["p1"] = new_name
                found = True
            if match["p2"] == old_name:
                match["p2"] = new_name
                found = True

    if data.get("playoff"):
        playoff = data["playoff"]
        for pair in playoff.get("pairs", []):
            if pair["p1"] == old_name:
                pair["p1"] = new_name
                found = True
            if pair["p2"] == old_name:
                pair["p2"] = new_name
                found = True
            if pair["winner"] == old_name:
                pair["winner"] = new_name
                found = True
        for match_list in playoff.get("history", {}).values():
            for match in match_list:
                if match["p1"] == old_name:
                    match["p1"] = new_name
                    found = True
                if match["p2"] == old_name:
                    match["p2"] = new_name
                    found = True
                if match["winner"] == old_name:
                    match["winner"] = new_name
                    found = True

    if not found:
        bot.reply_to(message, f"❌ Пользователь {old_name} не найден в турнире.")
        return

    save_tournament(data)
    bot.reply_to(
        message,
        f"✅ Замена выполнена!\n"
        f"{old_name} → {new_name}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['fsave_tournament'])
def save_tournament_to_file(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Нет активного турнира.")
        return

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    bot.reply_to(message, "✅ Турнир сохранён в файл `tournament_save.json`", parse_mode="Markdown")

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
# ПЛЕЙ-ОФФ
# ============================================================

ROUND_NAMES = ["1/16", "1/8", "1/4", "1/2", "Финал", "Матч за 3-е место"]

def get_qualified_teams(data):
    qualified = []
    third_placed = []

    for group_name, group_data in data["groups"].items():
        sorted_teams = sort_teams(group_data["teams"])
        
        if len(sorted_teams) >= 1:
            qualified.append({
                "name": sorted_teams[0]["name"],
                "group": group_name,
                "place": 1,
                "points": sorted_teams[0]["points"],
                "diff": sorted_teams[0]["goals_for"] - sorted_teams[0]["goals_against"],
                "goals_for": sorted_teams[0]["goals_for"]
            })
        if len(sorted_teams) >= 2:
            qualified.append({
                "name": sorted_teams[1]["name"],
                "group": group_name,
                "place": 2,
                "points": sorted_teams[1]["points"],
                "diff": sorted_teams[1]["goals_for"] - sorted_teams[1]["goals_against"],
                "goals_for": sorted_teams[1]["goals_for"]
            })
        if len(sorted_teams) >= 3:
            third_placed.append({
                "name": sorted_teams[2]["name"],
                "group": group_name,
                "place": 3,
                "points": sorted_teams[2]["points"],
                "diff": sorted_teams[2]["goals_for"] - sorted_teams[2]["goals_against"],
                "goals_for": sorted_teams[2]["goals_for"]
            })

    third_placed.sort(key=lambda x: (x["points"], x["diff"], x["goals_for"]), reverse=True)

    total_qualified = len(qualified)
    powers = [8, 16, 32, 64]
    target = next((p for p in powers if p >= total_qualified), 16)
    third_needed = target - total_qualified

    for i in range(min(third_needed, len(third_placed))):
        qualified.append(third_placed[i])

    return qualified

def generate_playoff_pairs(qualified, groups_count):
    if len(qualified) < 2:
        return [], ""

    total = len(qualified)
    
    if total == 32:
        first_round = "1/16"
    elif total == 16:
        first_round = "1/8"
    elif total == 8:
        first_round = "1/4"
    else:
        first_round = "1/8"

    first_place = [t for t in qualified if t["place"] == 1]
    second_place = [t for t in qualified if t["place"] == 2]
    third_place = [t for t in qualified if t["place"] == 3]

    first_place.sort(key=lambda x: x["group"])
    second_place.sort(key=lambda x: x["group"])
    third_place.sort(key=lambda x: x["group"])

    pairs = []

    if third_place:
        for i in range(min(len(first_place), len(third_place))):
            pairs.append({
                "p1": first_place[i]["name"],
                "p2": third_place[i]["name"],
                "winner": None,
                "score1": None,
                "score2": None,
                "is_draw": False
            })
        
        remaining_first = first_place[len(third_place):]
        remaining_second = second_place[:len(remaining_first)]
        for i in range(len(remaining_first)):
            if i < len(remaining_second):
                pairs.append({
                    "p1": remaining_first[i]["name"],
                    "p2": remaining_second[i]["name"],
                    "winner": None,
                    "score1": None,
                    "score2": None,
                    "is_draw": False
                })
        
        if len(pairs) < total // 2:
            remaining_second = second_place[len(remaining_first):]
            for i in range(0, len(remaining_second), 2):
                if i + 1 < len(remaining_second):
                    pairs.append({
                        "p1": remaining_second[i]["name"],
                        "p2": remaining_second[i + 1]["name"],
                        "winner": None,
                        "score1": None,
                        "score2": None,
                        "is_draw": False
                    })
    else:
        for i in range(len(first_place)):
            if i < len(second_place):
                j = (i + 1) % len(second_place)
                pairs.append({
                    "p1": first_place[i]["name"],
                    "p2": second_place[j]["name"],
                    "winner": None,
                    "score1": None,
                    "score2": None,
                    "is_draw": False
                })

    return pairs, first_round

def check_groups_complete(data):
    incomplete = []
    total_matches = 0
    played_matches = 0
    
    for group_name, group_data in data["groups"].items():
        teams = group_data["teams"]
        n = len(teams)
        expected = n * (n - 1) // 2
        played = group_data["played"]
        
        total_matches += expected
        played_matches += played
        
        if played < expected:
            played_pairs = set()
            for match in group_data["matches"]:
                p1 = match["p1"]
                p2 = match["p2"]
                if p1 > p2:
                    p1, p2 = p2, p1
                played_pairs.add((p1, p2))
            
            missing = []
            for i in range(n):
                for j in range(i + 1, n):
                    p1 = teams[i]["name"]
                    p2 = teams[j]["name"]
                    if p1 > p2:
                        p1, p2 = p2, p1
                    if (p1, p2) not in played_pairs:
                        missing.append(f"{get_display_name(p1)} — {get_display_name(p2)}")
            
            if missing:
                incomplete.append(f"Группа {group_name}: {', '.join(missing)}")
    
    return incomplete, total_matches, played_matches

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
        show_playoff_full(message, data)
        return

    if data["status"] != "groups":
        bot.reply_to(message, "❌ Групповой этап ещё не завершён.")
        return

    incomplete, total, played = check_groups_complete(data)
    
    if incomplete:
        text = "⚠️ *НЕ ВСЕ МАТЧИ СЫГРАНЫ!*\n\n"
        text += f"📊 Сыграно: {played}/{total} матчей\n\n"
        text += "❌ *Не сыграны:*\n"
        for item in incomplete:
            text += f"• {item}\n"
        text += "\n📝 Запишите все результаты командой `/fresult`"
        bot.reply_to(message, text, parse_mode="Markdown")
        return

    qualified = get_qualified_teams(data)
    if len(qualified) < 2:
        bot.reply_to(message, "❌ Недостаточно команд для плей-офф.")
        return

    pairs, first_round = generate_playoff_pairs(qualified, data["groups_count"])
    if not pairs:
        bot.reply_to(message, "❌ Не удалось сгенерировать пары.")
        return

    data["status"] = "playoff"
    data["playoff"] = {
        "round": first_round,
        "pairs": pairs,
        "winners": [],
        "history": {}
    }
    save_tournament(data)

    show_playoff_full(message, data)

def show_playoff_full(message, data):
    playoff = data["playoff"]
    if not playoff:
        return

    text = f"🏆 *ПЛЕЙ-ОФФ: {playoff['round'].upper()}*\n\n"

    for i, pair in enumerate(playoff["pairs"], 1):
        p1 = get_display_name(pair["p1"])
        p2 = get_display_name(pair["p2"])
        if pair["winner"]:
            winner = get_display_name(pair["winner"])
            if pair.get("is_draw", False):
                status = f"🎲 {pair['score1']}:{pair['score2']} → Победа: {winner} (по буллитам/кубам)"
            else:
                status = f"✅ {pair['score1']}:{pair['score2']} → Победитель: {winner}"
        else:
            status = "⏳ Не сыгран"
        text += f"🔥 {i}. {p1} — {p2} | {status}\n"

    if playoff.get("history"):
        text += "\n📜 *ИСТОРИЯ МАТЧЕЙ:*\n"
        for round_name, matches in playoff["history"].items():
            if matches:
                text += f"\n📋 *{round_name}*\n"
                for match in matches:
                    p1 = get_display_name(match["p1"])
                    p2 = get_display_name(match["p2"])
                    winner = get_display_name(match["winner"])
                    if match.get("is_draw", False):
                        text += f"  🎲 {p1} {match['score1']}:{match['score2']} {p2} → {winner} (по буллитам/кубам)\n"
                    else:
                        text += f"  ✅ {p1} {match['score1']}:{match['score2']} {p2} → {winner}\n"

    text += "\n📝 Команды:\n"
    text += "`/fresult_playoff @user1 @user2 3:1` — записать результат\n"
    text += "`/fresult_playoff_draw @user1 @user2 1:1 @winner` — ничья с победителем\n"
    text += "`/fgenerate_playoff` — автоматически заполнить все матчи\n"
    text += "`/fnext_round` — перейти к следующему раунду"

    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['fresult_playoff'])
def result_playoff(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, "❌ Используйте: `/fresult_playoff @user1 @user2 3:1`", parse_mode="Markdown")
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

    playoff = data["playoff"]
    found_pair = None
    for pair in playoff["pairs"]:
        if pair["winner"]:
            continue
        if (pair["p1"] == p1 and pair["p2"] == p2) or (pair["p1"] == p2 and pair["p2"] == p1):
            found_pair = pair
            break

    if not found_pair:
        bot.reply_to(message, "❌ Такая пара не найдена или уже сыграна.")
        return

    if score1 > score2:
        found_pair["winner"] = p1
    elif score2 > score1:
        found_pair["winner"] = p2
    else:
        bot.reply_to(message, "⚠️ В плей-офф ничья! Используйте команду для ничьи с указанием победителя:\n`/fresult_playoff_draw @user1 @user2 1:1 @winner`", parse_mode="Markdown")
        return

    found_pair["score1"] = score1
    found_pair["score2"] = score2
    found_pair["is_draw"] = False

    current_round = playoff["round"]
    if current_round not in playoff["history"]:
        playoff["history"][current_round] = []
    playoff["history"][current_round].append({
        "p1": p1,
        "p2": p2,
        "score1": score1,
        "score2": score2,
        "winner": found_pair["winner"],
        "is_draw": False
    })

    playoff["winners"].append(found_pair["winner"])
    save_tournament(data)

    all_played = all(p["winner"] for p in playoff["pairs"])
    display_p1 = get_display_name(p1)
    display_p2 = get_display_name(p2)
    winner = get_display_name(found_pair["winner"])

    if all_played:
        bot.reply_to(
            message,
            f"✅ Результат записан!\n{display_p1} {score1} : {score2} {display_p2}\n🏆 Победитель: {winner}\n\n📌 Все матчи сыграны! Напишите `/fnext_round` для перехода."
        )
    else:
        bot.reply_to(message, f"✅ {display_p1} {score1} : {score2} {display_p2}\n🏆 Победитель: {winner}")

@bot.message_handler(commands=['fresult_playoff_draw'])
def result_playoff_draw(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    parts = message.text.split()
    if len(parts) < 5:
        bot.reply_to(message, "❌ Используйте: `/fresult_playoff_draw @user1 @user2 1:1 @winner`", parse_mode="Markdown")
        return

    p1 = parts[1].lower()
    p2 = parts[2].lower()

    try:
        score1, score2 = map(int, parts[3].split(':'))
        if score1 < 0 or score2 < 0:
            bot.reply_to(message, "❌ Счёт не может быть отрицательным")
            return
    except ValueError:
        bot.reply_to(message, "❌ Формат счёта: 1:1")
        return

    winner = parts[4].lower()
    if not winner.startswith('@'):
        bot.reply_to(message, "❌ Укажите победителя: @username")
        return

    if winner != p1 and winner != p2:
        bot.reply_to(message, "❌ Победитель должен быть одним из участников матча.")
        return

    playoff = data["playoff"]
    found_pair = None
    for pair in playoff["pairs"]:
        if pair["winner"]:
            continue
        if (pair["p1"] == p1 and pair["p2"] == p2) or (pair["p1"] == p2 and pair["p2"] == p1):
            found_pair = pair
            break

    if not found_pair:
        bot.reply_to(message, "❌ Такая пара не найдена или уже сыграна.")
        return

    found_pair["winner"] = winner
    found_pair["score1"] = score1
    found_pair["score2"] = score2
    found_pair["is_draw"] = True

    current_round = playoff["round"]
    if current_round not in playoff["history"]:
        playoff["history"][current_round] = []
    playoff["history"][current_round].append({
        "p1": p1,
        "p2": p2,
        "score1": score1,
        "score2": score2,
        "winner": winner,
        "is_draw": True
    })

    playoff["winners"].append(winner)
    save_tournament(data)

    all_played = all(p["winner"] for p in playoff["pairs"])
    display_p1 = get_display_name(p1)
    display_p2 = get_display_name(p2)
    winner_display = get_display_name(winner)

    if all_played:
        bot.reply_to(
            message,
            f"✅ Ничья записана!\n{display_p1} {score1} : {score2} {display_p2}\n🎲 Победитель по буллитам/кубам: {winner_display}\n\n📌 Все матчи сыграны! Напишите `/fnext_round` для перехода."
        )
    else:
        bot.reply_to(message, f"✅ Ничья: {display_p1} {score1} : {score2} {display_p2}\n🎲 Победитель: {winner_display}")

@bot.message_handler(commands=['fgenerate_playoff'])
def generate_playoff_results(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    max_rounds = 10
    round_counter = 0
    
    while round_counter < max_rounds:
        playoff = data["playoff"]
        
        unplayed = [p for p in playoff["pairs"] if not p["winner"]]
        if unplayed:
            generated = 0
            for pair in unplayed:
                score1 = random.randint(0, 3)
                score2 = random.randint(0, 2)
                if score1 > score2:
                    pair["winner"] = pair["p1"]
                elif score2 > score1:
                    pair["winner"] = pair["p2"]
                else:
                    pair["winner"] = random.choice([pair["p1"], pair["p2"]])
                    pair["is_draw"] = True
                pair["score1"] = score1
                pair["score2"] = score2
                
                current_round = playoff["round"]
                if current_round not in playoff["history"]:
                    playoff["history"][current_round] = []
                playoff["history"][current_round].append({
                    "p1": pair["p1"],
                    "p2": pair["p2"],
                    "score1": score1,
                    "score2": score2,
                    "winner": pair["winner"],
                    "is_draw": pair["is_draw"]
                })
                
                playoff["winners"].append(pair["winner"])
                generated += 1
            save_tournament(data)
            bot.reply_to(message, f"✅ Сгенерировано {generated} матчей в раунде {playoff['round']}!")
        
        if not advance_playoff(data):
            break
        
        save_tournament(data)
        
        if data["status"] != "playoff":
            break
        
        round_counter += 1

    bot.reply_to(message, "✅ Все матчи плей-офф сгенерированы!")

def advance_playoff(data):
    playoff = data["playoff"]
    
    for pair in playoff["pairs"]:
        if not pair["winner"]:
            return False

    winners = [p["winner"] for p in playoff["pairs"]]
    losers = [p["p1"] if p["winner"] == p["p2"] else p["p2"] for p in playoff["pairs"]]
    
    round_names = ["1/16", "1/8", "1/4", "1/2"]
    
    if playoff["round"] == "1/2":
        if "third_place_match" not in playoff:
            playoff["finalists"] = winners[:2]
            playoff["third_place_match"] = {
                "p1": losers[0],
                "p2": losers[1],
                "winner": None,
                "score1": None,
                "score2": None,
                "is_draw": False
            }
            playoff["status"] = "third_place"
            save_tournament(data)
            return False
        
        third_match = playoff["third_place_match"]
        if not third_match["winner"]:
            return False
        
        if "Матч за 3-е место" not in playoff["history"]:
            playoff["history"]["Матч за 3-е место"] = []
        playoff["history"]["Матч за 3-е место"].append({
            "p1": third_match["p1"],
            "p2": third_match["p2"],
            "score1": third_match["score1"],
            "score2": third_match["score2"],
            "winner": third_match["winner"],
            "is_draw": third_match["is_draw"]
        })
        
        playoff["round"] = "Финал"
        playoff["pairs"] = [{
            "p1": playoff["finalists"][0],
            "p2": playoff["finalists"][1],
            "winner": None,
            "score1": None,
            "score2": None,
            "is_draw": False
        }]
        playoff["winners"] = []
        playoff["status"] = "final"
        save_tournament(data)
        return False
    
    if playoff["round"] == "Финал":
        if winners:
            champion = winners[0]
            data["status"] = "finished"
            
            if playoff["pairs"]:
                final_pair = playoff["pairs"][0]
                if "Финал" not in playoff["history"]:
                    playoff["history"]["Финал"] = []
                playoff["history"]["Финал"].append({
                    "p1": final_pair["p1"],
                    "p2": final_pair["p2"],
                    "score1": final_pair["score1"],
                    "score2": final_pair["score2"],
                    "winner": final_pair["winner"],
                    "is_draw": final_pair.get("is_draw", False)
                })
            
            save_tournament(data)
            return True
    
    current_idx = round_names.index(playoff["round"])
    next_idx = current_idx + 1
    
    if next_idx >= len(round_names):
        data["status"] = "finished"
        save_tournament(data)
        return True
    
    new_pairs = []
    for i in range(0, len(winners), 2):
        if i + 1 < len(winners):
            new_pairs.append({
                "p1": winners[i],
                "p2": winners[i + 1],
                "winner": None,
                "score1": None,
                "score2": None,
                "is_draw": False
            })
    
    playoff["round"] = round_names[next_idx]
    playoff["pairs"] = new_pairs
    playoff["winners"] = []
    save_tournament(data)
    return True

@bot.message_handler(commands=['fresult_third_place'])
def result_third_place(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    if "third_place_match" not in data["playoff"]:
        bot.reply_to(message, "❌ Матч за 3-е место не найден.")
        return

    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, "❌ Используйте: `/fresult_third_place @user1 @user2 3:1`", parse_mode="Markdown")
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

    third_match = data["playoff"]["third_place_match"]
    if third_match["winner"]:
        bot.reply_to(message, "⚠️ Матч за 3-е место уже сыгран.")
        return

    if (third_match["p1"] != p1 and third_match["p1"] != p2) or (third_match["p2"] != p1 and third_match["p2"] != p2):
        bot.reply_to(message, "❌ Игроки не участвуют в матче за 3-е место.")
        return

    if score1 > score2:
        third_match["winner"] = p1
    elif score2 > score1:
        third_match["winner"] = p2
    else:
        bot.reply_to(message, "⚠️ В матче за 3-е место ничья! Используйте `/fresult_third_place_draw`", parse_mode="Markdown")
        return

    third_match["score1"] = score1
    third_match["score2"] = score2
    third_match["is_draw"] = False

    if "Матч за 3-е место" not in data["playoff"]["history"]:
        data["playoff"]["history"]["Матч за 3-е место"] = []
    data["playoff"]["history"]["Матч за 3-е место"].append({
        "p1": p1,
        "p2": p2,
        "score1": score1,
        "score2": score2,
        "winner": third_match["winner"],
        "is_draw": False
    })

    save_tournament(data)

    winner = get_display_name(third_match["winner"])
    bot.reply_to(
        message,
        f"🥉 *Результат матча за 3-е место*\n"
        f"{get_display_name(p1)} {score1} : {score2} {get_display_name(p2)}\n"
        f"🥉 3-е место: {winner}\n\n"
        f"📌 Теперь напишите `/fnext_round` для финала!"
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

    if "third_place_match" not in data["playoff"]:
        bot.reply_to(message, "❌ Матч за 3-е место не найден.")
        return

    parts = message.text.split()
    if len(parts) < 5:
        bot.reply_to(message, "❌ Используйте: `/fresult_third_place_draw @user1 @user2 1:1 @winner`", parse_mode="Markdown")
        return

    p1 = parts[1].lower()
    p2 = parts[2].lower()

    try:
        score1, score2 = map(int, parts[3].split(':'))
    except ValueError:
        bot.reply_to(message, "❌ Формат счёта: 1:1")
        return

    winner = parts[4].lower()
    if not winner.startswith('@'):
        bot.reply_to(message, "❌ Укажите победителя: @username")
        return

    if winner != p1 and winner != p2:
        bot.reply_to(message, "❌ Победитель должен быть одним из участников.")
        return

    third_match = data["playoff"]["third_place_match"]
    if third_match["winner"]:
        bot.reply_to(message, "⚠️ Матч уже сыгран.")
        return

    third_match["winner"] = winner
    third_match["score1"] = score1
    third_match["score2"] = score2
    third_match["is_draw"] = True

    if "Матч за 3-е место" not in data["playoff"]["history"]:
        data["playoff"]["history"]["Матч за 3-е место"] = []
    data["playoff"]["history"]["Матч за 3-е место"].append({
        "p1": p1,
        "p2": p2,
        "score1": score1,
        "score2": score2,
        "winner": winner,
        "is_draw": True
    })

    save_tournament(data)

    bot.reply_to(
        message,
        f"🥉 *Результат матча за 3-е место*\n"
        f"{get_display_name(p1)} {score1} : {score2} {get_display_name(p2)}\n"
        f"🥉 3-е место: {get_display_name(winner)}\n\n"
        f"📌 Теперь напишите `/fnext_round` для финала!"
    )

@bot.message_handler(commands=['fnext_round'])
def next_round(message):
    if not has_tournament_access(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у администраторов.")
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    playoff = data["playoff"]
    for pair in playoff["pairs"]:
        if not pair["winner"]:
            bot.reply_to(message, "⚠️ Не все матчи сыграны! Запишите результаты или используйте `/fgenerate_playoff`.")
            return

    if not advance_playoff(data):
        data = load_tournament()
        if data and data["status"] == "finished":
            champion = data["playoff"]["history"].get("Финал", [{}])[0].get("winner", "неизвестен") if data["playoff"]["history"] else "неизвестен"
            bot.reply_to(
                message,
                f"🏆 *ТУРНИР ЗАВЕРШЁН!*\n\n"
                f"👑 *ЧЕМПИОН:* {get_display_name(champion)}!\n\n"
                f"🥈 2-е место: {get_display_name(data['playoff']['finalists'][1]) if 'finalists' in data['playoff'] else 'неизвестен'}\n"
                f"🥉 3-е место: {get_display_name(data['playoff']['third_place_match']['winner']) if 'third_place_match' in data['playoff'] and data['playoff']['third_place_match']['winner'] else 'неизвестен'}\n\n"
                f"📜 Посмотреть историю матчей: `/fplayoff`"
            )
            return
        elif data and data["status"] == "playoff":
            if "third_place_match" in data["playoff"] and not data["playoff"]["third_place_match"]["winner"]:
                third_match = data["playoff"]["third_place_match"]
                text = "🥉 *МАТЧ ЗА 3-Е МЕСТО*\n\n"
                p1 = get_display_name(third_match["p1"])
                p2 = get_display_name(third_match["p2"])
                text += f"🔥 {p1} — {p2}\n"
                text += "\n📝 Запишите результат:\n"
                text += "`/fresult_third_place @user1 @user2 3:1`\n"
                text += "Или ничью: `/fresult_third_place_draw @user1 @user2 1:1 @winner`"
                bot.reply_to(message, text, parse_mode="Markdown")
            else:
                show_playoff_full(message, data)
    else:
        data = load_tournament()
        if data and data["status"] == "playoff":
            show_playoff_full(message, data)

# ============================================================
# ОБРАБОТЧИК КНОПОК (ПЕРЕПИСАН)
# ============================================================

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    is_owner_or_admin_flag = has_tournament_access(user_id)
    is_owner_flag = has_full_access(user_id)

    # Отладочное сообщение (можно убрать после проверки)
    # bot.reply_to(message, f"🔍 Нажата кнопка: {message.text}")

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
    
    else:
        # Если кнопка не распознана
        bot.reply_to(message, f"ℹ️ Неизвестная кнопка: {message.text}")
        
# ============================================================
# ЗАПУСК
# ============================================================

print("✅ Турнирный бот (f-версия) запущен!")
print(f"👑 Владелец: {OWNER_ID}")
print(f"🛡️ Постоянные админы: {PERMANENT_ADMINS}")
print("=" * 40)
bot.infinity_polling()
