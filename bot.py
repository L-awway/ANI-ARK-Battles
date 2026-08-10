import telebot
from telebot import types
import json
import os
import random
from datetime import datetime

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8658074950:AAHwVaOMhAW61ZIWeF7OU4ngaahDwSw48Co"

# ТВОЙ ID (главный админ)
OWNER_ID = 7080227092

TOURNAMENT_FILE = "tournament_data.json"
SAVE_FILE = "tournament_save.json"
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

def safe_save(data):
    # Сохраняем основной файл
    save_tournament(data)
    # И сразу делаем резервную копию
    with open("tournament_backup.json", "w") as f:
        json.dump(data, f, indent=2)

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
    text += f"{'Команда':<12} {'И':<3} {'О':<3} {'В':<3} {'Н':<3} {'П':<3} {'З':<3} {'ПР':<3} {'Р':<4}\n"
    text += "-" * 55 + "\n"
    for team in sorted_teams:
        name = get_display_name(team['name'])[:10]
        win_rounds = team['goals_for']
        lose_rounds = team['goals_against']
        diff = win_rounds - lose_rounds
        text += f"{name:<12} {team['played']:<3} {team['points']:<3} {win_rounds:<3} {team['draws']:<3} {lose_rounds:<3} {win_rounds:<3} {lose_rounds:<3} {diff:>+3}\n"
    text += "```"
    return text

# ===== КОМАНДА /start =====
@bot.message_handler(commands=['start'])
def start(message):
    if not is_admin(message):
        bot.reply_to(message, "⛔ Доступ только у администратора.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_create = types.KeyboardButton("🏆 Создать турнир")
    btn_add = types.KeyboardButton("➕ Добавить участника")
    btn_register = types.KeyboardButton("📋 Регистрация всех")
    btn_groups = types.KeyboardButton("📊 Группы")
    btn_result = types.KeyboardButton("📝 Записать результат")
    btn_generate = types.KeyboardButton("🎲 Сгенерировать результаты")
    btn_standings = types.KeyboardButton("📈 Таблица")
    btn_playoff = types.KeyboardButton("🏆 Плей-офф")
    btn_reset = types.KeyboardButton("🔄 Сбросить турнир")
    markup.add(btn_create, btn_add, btn_register, btn_groups, btn_result, btn_generate, btn_standings, btn_playoff, btn_reset)

    bot.reply_to(
        message,
        "🏆 *ТУРНИРНЫЙ БОТ*\n\n"
        "📌 *Команды:*\n"
        "`/create_tournament 24` — создать турнир\n"
        "`/register_players @user1 @user2 ...` — массовая регистрация\n"
        "`/add_player @user` — добавить участника\n"
        "`/start_groups` — запустить групповой этап\n"
        "`/result @u1 @u2 3:1` — записать результат\n"
        "`/generate_results` — сгенерировать случайные результаты\n"
        "`/clear_results` — очистить все результаты\n"
        "`/groups` — все группы\n"
        "`/group A` — конкретная группа\n"
        "`/playoff` — плей-офф\n"
        "`/save_tournament` — сохранить турнир\n"
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

    # Проверяем, есть ли уже турнир
    existing = load_tournament()
    if existing:
        if existing["status"] == "waiting" and existing["players"]:
            bot.reply_to(
                message,
                "⚠️ *Турнир уже создан и в нём есть участники!*\n\n"
                f"📊 Участников: {len(existing['players'])}/{existing['total_players']}\n"
                f"📌 Статус: {existing['status']}\n\n"
                "Чтобы создать новый турнир, сначала сбросьте старый:\n"
                "`/reset_tournament`",
                parse_mode="Markdown"
            )
            return
        elif existing["status"] != "waiting":
            bot.reply_to(
                message,
                "⚠️ *Турнир уже запущен!*\n\n"
                f"📌 Статус: {existing['status']}\n"
                "Нельзя создать новый турнир, пока текущий не завершён.\n\n"
                "Чтобы сбросить: `/reset_tournament`",
                parse_mode="Markdown"
            )
            return

    # Дальше идёт обычный код создания турнира...
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/create_tournament N`\nНапример: `/create_tournament 24`", parse_mode="Markdown")
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
        f"➕ Добавьте участников: `/register_players @user1 @user2 ...`\n"
        f"📖 Инструкция: `/help`",
        parse_mode="Markdown"
    )

# ===== КОМАНДА /help ====
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "📖 *ИНСТРУКЦИЯ ПО ТУРНИРНОМУ БОТУ*\n\n"
        "🏆 *Формат турнира:*\n"
        "• Групповой этап (каждый с каждым в группе)\n"
        "• 3 тура в группе (для 4 участников)\n"
        "• Далее плей-офф (1/8, 1/4, 1/2, финал)\n\n"
        "📊 *Как читать таблицу:*\n"
        "`И` — сыграно матчей\n"
        "`О` — очки (3 — победа, 1 — ничья, 0 — поражение)\n"
        "`В` — выигранные раунды (сумма за все матчи)\n"
        "`Н` — ничьи по матчам\n"
        "`П` — проигранные раунды (сумма)\n"
        "`З` — раунды за игроком (выиграно)\n"
        "`ПР` — раунды проигранные игроком (проиграно)\n"
        "`Р` — разница (З − ПР)\n\n"
        "📝 *Как записать результат:*\n"
        "`/result @игрок1 @игрок2 3:1`\n\n"
        "📋 *Команды:*\n"
        "`/create_tournament N` — создать турнир (16, 24, 32, 48, 64)\n"
        "`/register_players @u1 @u2 ...` — массовая регистрация\n"
        "`/add_player @user` — добавить одного участника\n"
        "`/start_groups` — запустить групповой этап\n"
        "`/result @u1 @u2 3:1` — записать результат\n"
        "`/generate_results` — сгенерировать случайные результаты\n"
        "`/clear_results` — очистить все результаты\n"
        "`/groups` — показать все группы\n"
        "`/group A` — показать конкретную группу\n"
        "`/playoff` — начать плей-офф\n"
        "`/save_tournament` — сохранить турнир\n"
        "`/reset_tournament` — сбросить турнир\n\n"
        "💡 *Важно:*\n"
        "• Все команды доступны только администратору\n"
        "• Перед созданием нового турнира — сбросьте старый\n"
        "• Результаты сохраняются автоматически"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ===== КОМАНДА /rules ====
@bot.message_handler(commands=['rules'])
def show_rules(message):
    rules_text = (
        "📋 *ПРАВИЛА ТУРНИРА*\n\n"
        "1️⃣ Каждый играет с каждым в своей группе (3 тура).\n"
        "2️⃣ За победу — 3 очка, ничья — 1, поражение — 0.\n"
        "3️⃣ В плей-офф выходят:\n"
        "   • 1-е и 2-е места из каждой группы\n"
        "   • Лучшие команды с 3-х мест (если нужно)\n"
        "4️⃣ В плей-оффе — один матч на вылет.\n"
        "5️⃣ При равенстве очков — смотрим разницу раундов.\n\n"
        "📊 *Колонки в таблице:*\n"
        "`И` — игры, `О` — очки, `В` — выигранные раунды,\n"
        "`Н` — ничьи, `П` — проигранные раунды,\n"
        "`З` — забито, `ПР` — пропущено, `Р` — разница."
    )
    bot.reply_to(message, rules_text, parse_mode="Markdown")

# ===== КОМАНДА /register_players =====
@bot.message_handler(commands=['register_players'])
def register_players(message):
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
    if len(parts) < 2:
        bot.reply_to(message, "❌ Используйте: `/register_players @user1 @user2 @user3 ...`", parse_mode="Markdown")
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

# ===== КОМАНДА /generate_results =====
@bot.message_handler(commands=['generate_results'])
def generate_results(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data or data["status"] != "groups":
        bot.reply_to(message, "❌ Сначала создайте турнир и запустите группы: /start_groups")
        return

    total_matches = 0
    for group_name, group_data in data["groups"].items():
        teams = [t['name'] for t in group_data["teams"]]
        if len(teams) < 2:
            continue

        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                p1 = teams[i]
                p2 = teams[j]

                already_played = False
                for match in group_data["matches"]:
                    if (match['p1'] == p1 and match['p2'] == p2) or (match['p1'] == p2 and match['p2'] == p1):
                        already_played = True
                        break
                if already_played:
                    continue

                score1 = random.randint(0, 3)
                score2 = random.randint(0, 2)

                for team in group_data["teams"]:
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

                group_data["matches"].append({
                    "p1": p1,
                    "p2": p2,
                    "score1": score1,
                    "score2": score2
                })
                group_data["played"] += 1
                total_matches += 1

    save_tournament(data)
    bot.reply_to(message, f"✅ Сгенерировано {total_matches} матчей! Используйте /groups, чтобы посмотреть таблицу.")

# ===== КОМАНДА /clear_results =====
@bot.message_handler(commands=['clear_results'])
def clear_results(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data or data["status"] != "groups":
        bot.reply_to(message, "❌ Турнир не в статусе groups.")
        return

    for group_name, group_data in data["groups"].items():
        for team in group_data["teams"]:
            team["points"] = 0
            team["wins"] = 0
            team["draws"] = 0
            team["losses"] = 0
            team["goals_for"] = 0
            team["goals_against"] = 0
            team["played"] = 0
        group_data["matches"] = []
        group_data["played"] = 0

    save_tournament(data)
    bot.reply_to(message, "🗑️ Все результаты очищены!")

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
        text += show_group_table(group_data, group_name) + "\n\n"

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
    text = show_group_table(group_data, group_letter)

    if group_data["matches"]:
        text += "\n📝 *Сыгранные матчи:*\n"
        for match in group_data["matches"]:
            p1 = get_display_name(match['p1'])
            p2 = get_display_name(match['p2'])
            text += f"{p1} {match['score1']} : {match['score2']} {p2}\n"

    bot.reply_to(message, text, parse_mode="Markdown")

# ===== ПЛЕЙ-ОФФ =====

ROUND_NAMES = ["1/16", "1/8", "1/4", "1/2", "Финал"]

def get_qualified_teams(data):
    """Определяет, кто вышел из групп (с учётом лучших 3-х мест)"""
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

    # Сортируем 3-и места
    third_placed.sort(key=lambda x: (x["points"], x["diff"], x["goals_for"]), reverse=True)

    # Определяем, сколько 3-х мест нужно добрать до степени двойки
    total_qualified = len(qualified)
    powers = [8, 16, 32, 64]
    target = next((p for p in powers if p >= total_qualified), 16)
    third_needed = target - total_qualified

    # Добавляем лучшие 3-и места
    for i in range(min(third_needed, len(third_placed))):
        qualified.append(third_placed[i])

    return qualified


def generate_playoff_pairs(qualified, groups_count):
    """Генерирует пары для плей-офф"""
    if len(qualified) < 2:
        return [], ""

    total = len(qualified)
    
    # Определяем раунд
    if total == 32:
        first_round = "1/16"
    elif total == 16:
        first_round = "1/8"
    elif total == 8:
        first_round = "1/4"
    else:
        first_round = "1/8"

    # Разделяем по местам
    first_place = [t for t in qualified if t["place"] == 1]
    second_place = [t for t in qualified if t["place"] == 2]
    third_place = [t for t in qualified if t["place"] == 3]

    first_place.sort(key=lambda x: x["group"])
    second_place.sort(key=lambda x: x["group"])
    third_place.sort(key=lambda x: x["group"])

    pairs = []

    # Если есть третьи места (24, 48 участников)
    if third_place:
        # Сначала 1-е места против 3-х мест (перекрёст)
        for i in range(min(len(first_place), len(third_place))):
            pairs.append({
                "p1": first_place[i]["name"],
                "p2": third_place[i]["name"],
                "winner": None,
                "score1": None,
                "score2": None,
                "is_draw": False
            })
        
        # Затем оставшиеся 1-е места против 2-х мест
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
        
        # Если пар всё ещё мало — добавляем оставшиеся 2-е места
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
        # Классическая схема: 1-е места против 2-х мест
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

@bot.message_handler(commands=['playoff'])
def start_playoff(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Турнир не найден.")
        return

    # Если плей-офф уже запущен — просто показываем текущую сетку
    if data["status"] == "playoff":
        show_playoff_grid(message, data)
        return

    if data["status"] != "groups":
        bot.reply_to(message, "❌ Групповой этап ещё не завершён.")
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
        "winners": []
    }
    save_tournament(data)

    show_playoff_grid(message, data)

def show_playoff_grid(message, data):
    """Показывает текущую сетку плей-офф"""
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

    text += "\n📝 Команды:\n"
    text += "`/result_playoff @user1 @user2 3:1` — записать результат\n"
    text += "`/result_playoff_draw @user1 @user2 1:1 @winner` — ничья с победителем\n"
    text += "`/generate_playoff` — автоматически заполнить все матчи\n"
    text += "`/next_round` — перейти к следующему раунду"

    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['result_playoff'])
def result_playoff(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, "❌ Используйте: `/result_playoff @user1 @user2 3:1`", parse_mode="Markdown")
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
        bot.reply_to(message, "⚠️ В плей-офф ничья! Используйте команду для ничьи с указанием победителя:\n`/result_playoff_draw @user1 @user2 1:1 @winner`", parse_mode="Markdown")
        return

    found_pair["score1"] = score1
    found_pair["score2"] = score2
    found_pair["is_draw"] = False

    playoff["winners"].append(found_pair["winner"])
    save_tournament(data)

    all_played = all(p["winner"] for p in playoff["pairs"])
    display_p1 = get_display_name(p1)
    display_p2 = get_display_name(p2)
    winner = get_display_name(found_pair["winner"])

    if all_played:
        bot.reply_to(
            message,
            f"✅ Результат записан!\n{display_p1} {score1} : {score2} {display_p2}\n🏆 Победитель: {winner}\n\n📌 Все матчи сыграны! Напишите `/next_round` для перехода."
        )
    else:
        bot.reply_to(message, f"✅ {display_p1} {score1} : {score2} {display_p2}\n🏆 Победитель: {winner}")

@bot.message_handler(commands=['result_playoff_draw'])
def result_playoff_draw(message):
    """Ничья в плей-офф с указанием победителя"""
    if not is_admin(message):
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    parts = message.text.split()
    if len(parts) < 5:
        bot.reply_to(message, "❌ Используйте: `/result_playoff_draw @user1 @user2 1:1 @winner`", parse_mode="Markdown")
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

    playoff["winners"].append(winner)
    save_tournament(data)

    all_played = all(p["winner"] for p in playoff["pairs"])
    display_p1 = get_display_name(p1)
    display_p2 = get_display_name(p2)
    winner_display = get_display_name(winner)

    if all_played:
        bot.reply_to(
            message,
            f"✅ Ничья записана!\n{display_p1} {score1} : {score2} {display_p2}\n🎲 Победитель по буллитам/кубам: {winner_display}\n\n📌 Все матчи сыграны! Напишите `/next_round` для перехода."
        )
    else:
        bot.reply_to(message, f"✅ Ничья: {display_p1} {score1} : {score2} {display_p2}\n🎲 Победитель: {winner_display}")

@bot.message_handler(commands=['generate_playoff'])
def generate_playoff_results(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    playoff = data["playoff"]
    generated = 0

    for pair in playoff["pairs"]:
        if pair["winner"]:
            continue

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
        playoff["winners"].append(pair["winner"])
        generated += 1

    save_tournament(data)

    all_played = all(p["winner"] for p in playoff["pairs"])
    reply = f"✅ Сгенерировано {generated} матчей!"

    if all_played:
        reply += "\n📌 Все матчи сыграны! Напишите `/next_round` для перехода."

    bot.reply_to(message, reply)

@bot.message_handler(commands=['next_round'])
def next_round(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data or data["status"] != "playoff":
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    playoff = data["playoff"]
    
    for pair in playoff["pairs"]:
        if not pair["winner"]:
            bot.reply_to(message, "⚠️ Не все матчи сыграны! Запишите результаты или используйте `/generate_playoff`.")
            return

    winners = [p["winner"] for p in playoff["pairs"]]
    
    round_names = ROUND_NAMES
    current_idx = round_names.index(playoff["round"])
    next_idx = current_idx + 1

    if next_idx >= len(round_names):
        champion = winners[0] if winners else "неизвестен"
        data["status"] = "finished"
        save_tournament(data)
        bot.reply_to(
            message,
            f"🏆 *ТУРНИР ЗАВЕРШЁН!*\n\n"
            f"👑 *ЧЕМПИОН:* {get_display_name(champion)}!\n\n"
            f"Поздравляем победителя! 🎉"
        )
        return

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

    text = f"🏆 *ПЛЕЙ-ОФФ: {round_names[next_idx].upper()}*\n\n"
    for i, pair in enumerate(new_pairs, 1):
        p1 = get_display_name(pair["p1"])
        p2 = get_display_name(pair["p2"])
        text += f"🔥 {i}. {p1} — {p2} | ⏳ Не сыгран\n"
    text += "\n📝 Записывайте результаты:\n`/result_playoff @user1 @user2 3:1`\n`/result_playoff_draw @user1 @user2 1:1 @winner`"

    bot.reply_to(message, text, parse_mode="Markdown")

# ===== КОМАНДА /save_tournament =====
@bot.message_handler(commands=['save_tournament'])
def save_tournament_to_file(message):
    if not is_admin(message):
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Нет активного турнира.")
        return

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    bot.reply_to(message, "✅ Турнир сохранён в файл `tournament_save.json`", parse_mode="Markdown")

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
    elif message.text == "📋 Регистрация всех":
        bot.reply_to(message, "📝 Напишите: `/register_players @user1 @user2 @user3 ...`", parse_mode="Markdown")
    elif message.text == "📊 Группы":
        show_groups(message)
    elif message.text == "📝 Записать результат":
        bot.reply_to(message, "📝 Напишите: `/result @user1 @user2 3:1`", parse_mode="Markdown")
    elif message.text == "🎲 Сгенерировать результаты":
        generate_results(message)
    elif message.text == "📈 Таблица":
        show_groups(message)
    elif message.text == "🔄 Сбросить турнир":
        reset_tournament(message)
    elif message.text == "🏆 Плей-офф":
        start_playoff(message)

# ---------- ЗАПУСК ----------
print("✅ Турнирный бот запущен!")
print("=" * 40)
bot.infinity_polling()
