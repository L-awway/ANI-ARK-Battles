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
# ПЛЕЙ-ОФФ (ПЕРЕКРЁСТНАЯ СХЕМА)
# ============================================================

def get_qualified_teams(data):
    """Получает 1-е и 2-е места из каждой группы"""
    qualified = {}
    for group_name, group_data in data["groups"].items():
        sorted_teams = sort_teams(group_data["teams"])
        if len(sorted_teams) >= 2:
            qualified[group_name] = {
                "first": sorted_teams[0]["name"],
                "second": sorted_teams[1]["name"]
            }
    return qualified

def generate_playoff_pairs(qualified):
    """Генерирует пары по перекрёстной схеме"""
    groups = sorted(qualified.keys())
    
    # 1/8 финала по схеме
    pairs = [
        # 1 место A — 2 место B
        {"p1": qualified["A"]["first"], "p2": qualified["B"]["second"], "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "A"},
        # 1 место C — 2 место D
        {"p1": qualified["C"]["first"], "p2": qualified["D"]["second"], "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "B"},
        # 1 место B — 2 место A
        {"p1": qualified["B"]["first"], "p2": qualified["A"]["second"], "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "C"},
        # 1 место D — 2 место C
        {"p1": qualified["D"]["first"], "p2": qualified["C"]["second"], "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "D"},
        # 1 место E — 2 место F
        {"p1": qualified["E"]["first"], "p2": qualified["F"]["second"], "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "E"},
        # 1 место G — 2 место H
        {"p1": qualified["G"]["first"], "p2": qualified["H"]["second"], "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "F"},
        # 1 место F — 2 место E
        {"p1": qualified["F"]["first"], "p2": qualified["E"]["second"], "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "G"},
        # 1 место H — 2 место G
        {"p1": qualified["H"]["first"], "p2": qualified["G"]["second"], "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "H"}
    ]
    
    return pairs

def get_playoff_quarterfinals(winners):
    """Формирует 1/4 финала по схеме A-B, E-F, G-H, C-D"""
    # winners — словарь {label: team_name}
    return [
        {"p1": winners.get("A"), "p2": winners.get("B"), "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "W"},
        {"p1": winners.get("E"), "p2": winners.get("F"), "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "X"},
        {"p1": winners.get("G"), "p2": winners.get("H"), "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "Y"},
        {"p1": winners.get("C"), "p2": winners.get("D"), "winner": None, "score1": None, "score2": None, "is_draw": False, "label": "Z"}
    ]

def get_playoff_semifinals(quarter_winners):
    """Формирует 1/2 финала: W-X, Y-Z"""
    return [
        {"p1": quarter_winners.get("W"), "p2": quarter_winners.get("X"), "winner": None, "score1": None, "score2": None, "is_draw": False},
        {"p1": quarter_winners.get("Y"), "p2": quarter_winners.get("Z"), "winner": None, "score1": None, "score2": None, "is_draw": False}
    ]

# ============================================================
# КОМАНДЫ ПЛЕЙ-ОФФ
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

    # Если плей-офф уже есть — показываем его
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

    # Получаем квалифицированные команды
    qualified = get_qualified_teams(data)
    if len(qualified) < 8:
        bot.reply_to(message, f"❌ Недостаточно групп для плей-офф. Нужно 8, есть {len(qualified)}.")
        return

    # Генерируем пары 1/8
    pairs = generate_playoff_pairs(qualified)

    data["status"] = "playoff"
    data["playoff"] = {
        "round": "1/8",
        "pairs": pairs,
        "winners": {},
        "quarter_winners": {},
        "semifinal_winners": [],
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
            if pair.get("is_draw", False):
                status = f"🎲 {pair['score1']}:{pair['score2']} → {winner} (по буллитам)"
            else:
                status = f"✅ {pair['score1']}:{pair['score2']} → {winner}"
        else:
            status = "⏳ Не сыгран"
        label = pair.get("label", "")
        label_text = f" [{label}]" if label else ""
        text += f"🔥 {i}. {p1} — {p2}{label_text} | {status}\n"

    if playoff.get("history"):
        text += "\n📜 *ИСТОРИЯ:*\n"
        for round_name, matches in playoff["history"].items():
            if matches:
                text += f"\n📋 *{round_name}*\n"
                for match in matches:
                    text += f"  ✅ {match['p1']} {match['score1']}:{match['score2']} {match['p2']} → {match['winner']}\n"

    text += "\n📝 Команды:\n"
    text += "`/fresult_playoff @user1 @user2 3:1` — записать результат\n"
    text += "`/fresult_playoff_draw @user1 @user2 1:1 @winner` — ничья\n"
    text += "`/fnext_round` — следующий раунд"

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
        found_pair["winner"] = found_pair["p1"]
    elif score2 > score1:
        found_pair["winner"] = found_pair["p2"]
    else:
        bot.reply_to(message, "⚠️ В плей-офф ничья! Используйте `/fresult_playoff_draw`", parse_mode="Markdown")
        return

    found_pair["score1"] = score1
    found_pair["score2"] = score2
    found_pair["is_draw"] = False

    # Запоминаем победителя по метке
    if found_pair.get("label"):
        playoff["winners"][found_pair["label"]] = found_pair["winner"]

    # Сохраняем историю
    if playoff["round"] not in playoff["history"]:
        playoff["history"][playoff["round"]] = []
    playoff["history"][playoff["round"]].append({
        "p1": found_pair["p1"],
        "p2": found_pair["p2"],
        "score1": score1,
        "score2": score2,
        "winner": found_pair["winner"]
    })

    save_tournament(data)

    bot.reply_to(
        message,
        f"✅ {found_pair['p1']} {score1} : {score2} {found_pair['p2']}\n🏆 Победитель: {found_pair['winner']}"
    )

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

    p1 = parts[1]
    p2 = parts[2]

    try:
        score1, score2 = map(int, parts[3].split(':'))
        if score1 < 0 or score2 < 0:
            bot.reply_to(message, "❌ Счёт не может быть отрицательным")
            return
    except ValueError:
        bot.reply_to(message, "❌ Формат счёта: 1:1")
        return

    winner = parts[4]
    if not winner.startswith('@'):
        bot.reply_to(message, "❌ Укажите победителя: @username")
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

    if winner != p1 and winner != p2:
        bot.reply_to(message, "❌ Победитель должен быть одним из участников.")
        return

    found_pair["winner"] = winner
    found_pair["score1"] = score1
    found_pair["score2"] = score2
    found_pair["is_draw"] = True

    if found_pair.get("label"):
        playoff["winners"][found_pair["label"]] = winner

    if playoff["round"] not in playoff["history"]:
        playoff["history"][playoff["round"]] = []
    playoff["history"][playoff["round"]].append({
        "p1": found_pair["p1"],
        "p2": found_pair["p2"],
        "score1": score1,
        "score2": score2,
        "winner": winner
    })

    save_tournament(data)

    bot.reply_to(
        message,
        f"✅ Ничья: {found_pair['p1']} {score1} : {score2} {found_pair['p2']}\n🎲 Победитель: {winner}"
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

    # Проверяем, все ли матчи сыграны
    for pair in playoff["pairs"]:
        if not pair["winner"]:
            bot.reply_to(message, "⚠️ Не все матчи сыграны! Запишите результаты.")
            return

    current_round = playoff["round"]
    winners = playoff["winners"]

    # Переход к 1/4 финала
    if current_round == "1/8":
        quarter_pairs = get_playoff_quarterfinals(winners)
        playoff["round"] = "1/4"
        playoff["pairs"] = quarter_pairs
        playoff["winners"] = {}
        save_tournament(data)
        show_playoff(message, data)
        return

    # Переход к 1/2 финала
    if current_round == "1/4":
        quarter_winners = {}
        for pair in playoff["pairs"]:
            if pair.get("label") and pair["winner"]:
                quarter_winners[pair["label"]] = pair["winner"]

        semifinal_pairs = get_playoff_semifinals(quarter_winners)
        playoff["round"] = "1/2"
        playoff["pairs"] = semifinal_pairs
        playoff["winners"] = {}
        playoff["quarter_winners"] = quarter_winners
        save_tournament(data)
        show_playoff(message, data)
        return

    # Переход к финалу и матчу за 3-е место
    if current_round == "1/2":
        # Победители полуфиналов
        semi_winners = []
        semi_losers = []
        for pair in playoff["pairs"]:
            if pair["winner"]:
                semi_winners.append(pair["winner"])
                # Определяем проигравшего
                if pair["winner"] == pair["p1"]:
                    semi_losers.append(pair["p2"])
                else:
                    semi_losers.append(pair["p1"])

        if len(semi_winners) < 2:
            bot.reply_to(message, "⚠️ Не все полуфиналы сыграны!")
            return

        # Матч за 3-е место
        playoff["third_place"] = {
            "p1": semi_losers[0],
            "p2": semi_losers[1],
            "winner": None,
            "score1": None,
            "score2": None
        }

        # Финал
        playoff["round"] = "Финал"
        playoff["pairs"] = [
            {"p1": semi_winners[0], "p2": semi_winners[1], "winner": None, "score1": None, "score2": None, "is_draw": False}
        ]
        playoff["winners"] = {}
        save_tournament(data)

        text = "🏆 *ФИНАЛ*\n\n"
        text += f"🔥 {semi_winners[0]} — {semi_winners[1]} | ⏳ Не сыгран\n\n"
        text += "🥉 *Матч за 3-е место*\n"
        text += f"🔥 {semi_losers[0]} — {semi_losers[1]} | ⏳ Не сыгран\n\n"
        text += "📝 Запишите финал: `/fresult_playoff @user1 @user2 3:1`\n"
        text += "📝 Запишите матч за 3-е место: `/fresult_third_place @user1 @user2 3:1`"
        bot.reply_to(message, text, parse_mode="Markdown")
        return

    # Завершение турнира (финал)
    if current_round == "Финал":
        if not playoff["pairs"][0]["winner"]:
            bot.reply_to(message, "⚠️ Финал ещё не сыгран!")
            return

        champion = playoff["pairs"][0]["winner"]
        data["status"] = "finished"
        save_tournament(data)

        text = f"🏆 *ТУРНИР ЗАВЕРШЁН!*\n\n"
        text += f"👑 *ЧЕМПИОН:* {champion}!\n"
        if playoff.get("third_place") and playoff["third_place"]["winner"]:
            text += f"🥉 *3-е место:* {playoff['third_place']['winner']}\n"
        bot.reply_to(message, text, parse_mode="Markdown")
        return

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
# ЗАПУСК
# ============================================================

print("✅ Турнирный бот запущен!")
print("=" * 40)
bot.infinity_polling()
