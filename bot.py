import telebot
from telebot import types
import json
import os
from datetime import datetime

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8658074950:AAHwVaOMhAW61ZIWeF7OU4ngaahDwSw48Co"

# ТВОЙ ID (главный админ)
OWNER_ID = 7080227092

TOURNAMENT_FILE = "tournament_data.json"
# =====================

bot = telebot.TeleBot(BOT_TOKEN)

# ===== РАБОТА С ДАННЫМИ =====
def load_tournament():
    if os.path.exists(TOURNAMENT_FILE):
        with open(TOURNAMENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_tournament(data):
    with open(TOURNAMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_admin(message):
    return message.from_user.id == OWNER_ID

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
def get_display_name(username):
    """Убирает @ из имени для отображения"""
    return username.replace('@', '')

def get_team_standing(team_name, group_data):
    """Получает статистику команды в группе"""
    for team in group_data['teams']:
        if team['name'] == team_name:
            return team
    return None

def sort_teams(teams):
    """
    Сортирует команды по:
    1. Очки (больше = лучше)
    2. Разница забитых/пропущенных (больше = лучше)
    3. Забитые голы (больше = лучше)
    4. Победы (больше = лучше)
    """
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

# ===== КОМАНДА /start =====
@bot.message_handler(commands=['start'])
def start(message):
    if not is_admin(message):
        bot.reply_to(message, "⛔ Доступ только у администратора.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_create = types.KeyboardButton("🏆 Создать турнир")
    btn_add = types.KeyboardButton("➕ Добавить участника")
    btn_groups = types.KeyboardButton("📊 Группы")
    btn_result = types.KeyboardButton("📝 Записать результат")
    btn_standings = types.KeyboardButton("📈 Таблица")
    btn_reset = types.KeyboardButton("🔄 Сбросить турнир")
    btn_playoff = types.KeyboardButton("🏆 Плей-офф")
    markup.add(btn_create, btn_add, btn_groups, btn_result, btn_standings, btn_playoff, btn_reset)

    bot.reply_to(
        message,
        "🏆 *ТУРНИРНЫЙ БОТ*\n\n"
        "📌 *Команды:*\n"
        "`/create_tournament 24` — создать турнир на N участников\n"
        "`/add_player @user` — добавить участника\n"
        "`/remove_player @user` — удалить участника\n"
        "`/start_groups` — запустить групповой этап\n"
        "`/result @user1 @user2 3:1` — записать результат\n"
        "`/groups` — показать все группы\n"
        "`/group A` — показать конкретную группу\n"
        "`/standings` — общая таблица\n"
        "`/playoff` — плей-офф\n"
        "`/reset_tournament` — сбросить турнир\n\n"
        "💡 *Поддерживаемые форматы:* 16, 24, 32, 48, 64",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ===== КОМАНДА /create_tournament =====
@bot.message_handler(commands=['create_tournament'])
def create_tournament(message):
    if not is_admin(message):
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/create_tournament N`\nНапример: `/create_tournament 24`", parse_mode="Markdown")
        return

    try:
        total = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ Введите число")
        return

    # Проверяем поддерживаемые форматы
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

    # Определяем, сколько 3-х мест нужно
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

    # Создаём турнир
    data = {
        "status": "waiting",  # waiting, groups, playoff, finished
        "total_players": total,
        "groups_count": groups_count,
        "players": [],
        "groups": {},
        "third_needed": third_needed,
        "playoff": None,
        "current_round": None
    }

    # Создаём пустые группы
    for i in range(groups_count):
        letter = chr(65 + i)  # A, B, C, D, ...
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
        f"➕ Добавьте участников: `/add_player @user`",
        parse_mode="Markdown"
    )

# ===== КОМАНДА /add_player =====
@bot.message_handler(commands=['add_player'])
def add_player(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Сначала создайте турнир: /create_tournament")
        return

    if data["status"] != "waiting":
        bot.reply_to(message, "❌ Турнир уже начался! Нельзя добавлять участников.")
        return

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].startswith('@'):
        bot.reply_to(message, "❌ Используйте: `/add_player @username`", parse_mode="Markdown")
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

# ===== КОМАНДА /start_groups =====
@bot.message_handler(commands=['start_groups'])
def start_groups(message):
    if not is_admin(message):
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

    # Разбиваем на группы (рандомно)
    import random
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

    # Выводим группы
    text = "🏆 *ГРУППОВОЙ ЭТАП ЗАПУЩЕН!*\n\n"
    for group_name, group_data in data["groups"].items():
        team_names = [get_display_name(t['name']) for t in group_data["teams"]]
        text += f"📋 *Группа {group_name}:* {', '.join(team_names)}\n"

    text += "\n📝 Записывайте результаты: `/result @user1 @user2 3:1`"
    bot.reply_to(message, text, parse_mode="Markdown")

# ===== КОМАНДА /result =====
@bot.message_handler(commands=['result'])
def add_result(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data or data["status"] != "groups":
        bot.reply_to(message, "❌ Групповой этап не запущен.")
        return

    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(
            message,
            "❌ Используйте: `/result @user1 @user2 3:1`\n"
            "Например: `/result @ivan @petr 2:0`",
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

    # Ищем группу с этими игроками
    found_group = None
    for group_name, group_data in data["groups"].items():
        team_names = [t['name'] for t in group_data["teams"]]
        if p1 in team_names and p2 in team_names:
            found_group = group_name
            break

    if not found_group:
        bot.reply_to(message, "❌ Игроки не найдены в одной группе.")
        return

    # Проверяем, не играли ли уже
    group = data["groups"][found_group]
    for match in group["matches"]:
        if (match['p1'] == p1 and match['p2'] == p2) or (match['p1'] == p2 and match['p2'] == p1):
            bot.reply_to(message, "⚠️ Этот матч уже сыгран!")
            return

    # Обновляем статистику
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

# ===== КОМАНДА /groups =====
@bot.message_handler(commands=['groups'])
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
        sorted_teams = sort_teams(group_data["teams"])
        text += f"📋 *Группа {group_name}*\n"
        text += "```\n"
        text += f"{'Команда':<12} {'И':<3} {'О':<3} {'В':<3} {'Н':<3} {'П':<3} {'З':<3} {'П':<3} {'Р':<4}\n"
        text += "-" * 50 + "\n"
        for team in sorted_teams:
            name = get_display_name(team['name'])[:10]
            diff = team['goals_for'] - team['goals_against']
            text += f"{name:<12} {team['played']:<3} {team['points']:<3} {team['wins']:<3} {team['draws']:<3} {team['losses']:<3} {team['goals_for']:<3} {team['goals_against']:<3} {diff:<4}\n"
        text += "```\n\n"

    bot.reply_to(message, text, parse_mode="Markdown")

# ===== КОМАНДА /group =====
@bot.message_handler(commands=['group'])
def show_group(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/group A`\nНапример: `/group A`", parse_mode="Markdown")
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
    sorted_teams = sort_teams(group_data["teams"])

    text = f"🏆 *Группа {group_letter}*\n\n"
    text += "```\n"
    text += f"{'Команда':<12} {'И':<3} {'О':<3} {'В':<3} {'Н':<3} {'П':<3} {'З':<3} {'П':<3} {'Р':<4}\n"
    text += "-" * 50 + "\n"
    for team in sorted_teams:
        name = get_display_name(team['name'])[:10]
        diff = team['goals_for'] - team['goals_against']
        text += f"{name:<12} {team['played']:<3} {team['points']:<3} {team['wins']:<3} {team['draws']:<3} {team['losses']:<3} {team['goals_for']:<3} {team['goals_against']:<3} {diff:<4}\n"
    text += "```"

    # Показываем сыгранные матчи
    if group_data["matches"]:
        text += "\n📝 *Сыгранные матчи:*\n"
        for match in group_data["matches"]:
            p1 = get_display_name(match['p1'])
            p2 = get_display_name(match['p2'])
            text += f"{p1} {match['score1']} : {match['score2']} {p2}\n"

    bot.reply_to(message, text, parse_mode="Markdown")

# ===== КОМАНДА /reset_tournament =====
@bot.message_handler(commands=['reset_tournament'])
def reset_tournament(message):
    if not is_admin(message):
        return

    if os.path.exists(TOURNAMENT_FILE):
        os.remove(TOURNAMENT_FILE)
        bot.reply_to(message, "🗑️ Турнир полностью сброшен!")
    else:
        bot.reply_to(message, "ℹ️ Нет активного турнира для сброса.")

# ===== ОБРАБОТЧИК КНОПОК =====
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "🏆 Создать турнир":
        bot.reply_to(message, "📝 Напишите: `/create_tournament N`\nНапример: `/create_tournament 24`", parse_mode="Markdown")
    elif message.text == "➕ Добавить участника":
        bot.reply_to(message, "📝 Напишите: `/add_player @username`", parse_mode="Markdown")
    elif message.text == "📊 Группы":
        show_groups(message)
    elif message.text == "📝 Записать результат":
        bot.reply_to(message, "📝 Напишите: `/result @user1 @user2 3:1`", parse_mode="Markdown")
    elif message.text == "📈 Таблица":
        show_groups(message)
    elif message.text == "🔄 Сбросить турнир":
        reset_tournament(message)
    elif message.text == "🏆 Плей-офф":
        bot.reply_to(message, "⏳ Функция в разработке!")

# ---------- ЗАПУСК ----------
print("✅ Турнирный бот запущен!")
print("=" * 40)
bot.infinity_polling()