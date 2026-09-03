import telebot
from telebot import types
import json
import os
import random
from datetime import datetime

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8658074950:AAHwVaOMhAW61ZIWeF7OU4ngaahDwSw48Co"
OWNER_ID = 7080227092

TOURNAMENT_FILE = "tournament_data.json"
# =====================

bot = telebot.TeleBot(BOT_TOKEN)

def load_tournament():
    if os.path.exists(TOURNAMENT_FILE):
        with open(TOURNAMENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_tournament(data):
    with open(TOURNAMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_owner(user_id):
    return user_id == OWNER_ID

def sort_teams(teams):
    return sorted(teams, key=lambda x: x['points'], reverse=True)

# ============================================================
# ВОССТАНОВЛЕНИЕ ТУРНИРА (ВСТРОЕННЫЕ ДАННЫЕ)
# ============================================================

def restore_tournament():
    data = {
        "status": "groups",
        "groups": {
            "A": {"teams": [{"name": "@ReoCopyed", "points": 7, "wins": 2, "draws": 1, "losses": 0, "goals_for": 5, "goals_against": 3, "played": 3}, {"name": "@Yary_270", "points": 6, "wins": 2, "draws": 0, "losses": 1, "goals_for": 4, "goals_against": 3, "played": 3}, {"name": "@ZERO_HZ", "points": 4, "wins": 1, "draws": 1, "losses": 1, "goals_for": 4, "goals_against": 4, "played": 3}, {"name": "@Limbibo", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 3, "played": 3}], "played": 6},
            "B": {"teams": [{"name": "@femfoy", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 3, "goals_against": 0, "played": 3}, {"name": "@noobtobias", "points": 2, "wins": 0, "draws": 2, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 3}, {"name": "@MAKAR_REVOLUTION", "points": 2, "wins": 0, "draws": 2, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 3}, {"name": "@ereneger13", "points": 2, "wins": 0, "draws": 2, "losses": 1, "goals_for": 2, "goals_against": 3, "played": 3}], "played": 6},
            "C": {"teams": [{"name": "@erofffa", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 9, "goals_against": 3, "played": 3}, {"name": "@Jimperqt", "points": 4, "wins": 1, "draws": 1, "losses": 1, "goals_for": 7, "goals_against": 5, "played": 3}, {"name": "@Sh4d0w_0x", "points": 4, "wins": 1, "draws": 1, "losses": 1, "goals_for": 6, "goals_against": 5, "played": 3}, {"name": "@ale7xey", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 9, "played": 3}], "played": 6},
            "D": {"teams": [{"name": "@egori_ii", "points": 7, "wins": 2, "draws": 1, "losses": 0, "goals_for": 8, "goals_against": 2, "played": 3}, {"name": "@jade_leech001", "points": 7, "wins": 2, "draws": 1, "losses": 0, "goals_for": 8, "goals_against": 4, "played": 3}, {"name": "@Vixzow", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 3, "goals_against": 6, "played": 3}, {"name": "@Krist_youtube", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 2, "goals_against": 9, "played": 3}], "played": 6},
            "E": {"teams": [{"name": "@A_r_t_0_0_7", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 9, "goals_against": 2, "played": 3}, {"name": "@ronin2033", "points": 6, "wins": 2, "draws": 0, "losses": 1, "goals_for": 8, "goals_against": 3, "played": 3}, {"name": "@stepanik123", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 3, "goals_against": 6, "played": 3}, {"name": "@Bad_Gyutaro", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 9, "played": 3}], "played": 6},
            "F": {"teams": [{"name": "@revolvrx", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 8, "goals_against": 0, "played": 3}, {"name": "@pasanbb", "points": 6, "wins": 2, "draws": 0, "losses": 1, "goals_for": 6, "goals_against": 2, "played": 3}, {"name": "@Red_Means_Love", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 3, "goals_against": 6, "played": 3}, {"name": "@gyutarosolo", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 9, "played": 3}], "played": 6},
            "G": {"teams": [{"name": "@NacamaML", "points": 7, "wins": 2, "draws": 1, "losses": 0, "goals_for": 6, "goals_against": 4, "played": 3}, {"name": "@velikiyarbuz", "points": 5, "wins": 1, "draws": 2, "losses": 0, "goals_for": 7, "goals_against": 6, "played": 3}, {"name": "@kapybaran7", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 6, "goals_against": 7, "played": 3}, {"name": "@Hamster_qw", "points": 1, "wins": 0, "draws": 1, "losses": 2, "goals_for": 5, "goals_against": 7, "played": 3}], "played": 6},
            "H": {"teams": [{"name": "@Dottoreji", "points": 9, "wins": 3, "draws": 0, "losses": 0, "goals_for": 9, "goals_against": 4, "played": 3}, {"name": "@panda20k", "points": 6, "wins": 2, "draws": 0, "losses": 1, "goals_for": 7, "goals_against": 4, "played": 3}, {"name": "@krer21001", "points": 3, "wins": 1, "draws": 0, "losses": 2, "goals_for": 6, "goals_against": 5, "played": 3}, {"name": "@beensuch", "points": 0, "wins": 0, "draws": 0, "losses": 3, "goals_for": 0, "goals_against": 9, "played": 3}], "played": 6}
        },
        "playoff": None
    }
    save_tournament(data)
    print("✅ Турнир восстановлен!")

if not os.path.exists(TOURNAMENT_FILE):
    restore_tournament()

# ============================================================
# ТАБЛИЦА
# ============================================================

def show_group_table(group_data, group_name):
    teams = sort_teams(group_data["teams"])
    text = f"🏆 *Группа {group_name}*\n\n"
    text += "```\n"
    text += f"{'Команда':<18} {'О':<3} {'ВР':<3} {'ПРР':<3} {'Р':<4}\n"
    text += "-" * 35 + "\n"
    for team in teams:
        name = team['name'][:18]
        diff = team['goals_for'] - team['goals_against']
        text += f"{name:<18} {team['points']:<3} {team['goals_for']:<3} {team['goals_against']:<3} {diff:>+3}\n"
    text += "```"
    return text

@bot.message_handler(commands=['fgroups'])
def show_groups(message):
    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Турнир не создан.")
        return

    text = "🏆 *ГРУППОВОЙ ЭТАП*\n\n"
    for group_name in sorted(data["groups"].keys()):
        text += show_group_table(data["groups"][group_name], group_name) + "\n\n"

    bot.reply_to(message, text, parse_mode="Markdown")

# ============================================================
# ПЛЕЙ-ОФФ
# ============================================================

@bot.message_handler(commands=['fplayoff'])
def start_playoff(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у владельца.")
        return

    data = load_tournament()
    if not data:
        bot.reply_to(message, "❌ Турнир не найден.")
        return

    # ТВОИ ТОЧНЫЕ ПАРЫ (с нижними подчёркиваниями)
    pairs = [
        {"p1": "@ReoCopyed", "p2": "@Sh4d0w_0x", "winner": None, "score1": None, "score2": None, "label": "A"},
        {"p1": "@erofffa", "p2": "@jade_leech001", "winner": None, "score1": None, "score2": None, "label": "B"},
        {"p1": "@femfoy", "p2": "@Yary_270", "winner": None, "score1": None, "score2": None, "label": "C"},
        {"p1": "@egori_ii", "p2": "@Jimperqt", "winner": None, "score1": None, "score2": None, "label": "D"},
        {"p1": "@A_r_t_0_0_7", "p2": "@pasanbb", "winner": None, "score1": None, "score2": None, "label": "E"},
        {"p1": "@NacamaML", "p2": "@panda20k", "winner": None, "score1": None, "score2": None, "label": "F"},
        {"p1": "@revolvrx", "p2": "@ronin2033", "winner": None, "score1": None, "score2": None, "label": "G"},
        {"p1": "@Dottoreji", "p2": "@velikiyarbuz", "winner": None, "score1": None, "score2": None, "label": "H"}
    ]

    data["playoff"] = {
        "round": "1/8",
        "pairs": pairs,
        "winners": {}
    }
    save_tournament(data)

    show_playoff(message, data)

def show_playoff(message, data):
    playoff = data.get("playoff")
    if not playoff:
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    text = f"🏆 *ПЛЕЙ-ОФФ: {playoff['round']}*\n\n"

    for i, pair in enumerate(playoff["pairs"], 1):
        p1 = pair["p1"]
        p2 = pair["p2"]
        if pair["winner"]:
            status = f"✅ {pair['score1']}:{pair['score2']} → {pair['winner']}"
        else:
            status = "⏳ Не сыгран"
        label = pair.get("label", "")
        label_text = f" [{label}]" if label else ""
        text += f"🔥 {i}. {p1} — {p2}{label_text} | {status}\n"

    text += "\n📝 Команды:\n"
    text += "`/fresult_playoff @user1 @user2 3:1`\n"
    text += "`/fnext_round` — следующий раунд"

    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['fresult_playoff'])
def result_playoff(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у владельца.")
        return

    data = load_tournament()
    if not data or not data.get("playoff"):
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
        bot.reply_to(message, "⚠️ В плей-офф ничья!")
        return

    found_pair["score1"] = score1
    found_pair["score2"] = score2

    if found_pair.get("label"):
        playoff["winners"][found_pair["label"]] = found_pair["winner"]

    save_tournament(data)

    bot.reply_to(
        message,
        f"✅ {found_pair['p1']} {score1} : {score2} {found_pair['p2']}\n🏆 Победитель: {found_pair['winner']}"
    )

@bot.message_handler(commands=['fnext_round'])
def next_round(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ только у владельца.")
        return

    data = load_tournament()
    if not data or not data.get("playoff"):
        bot.reply_to(message, "❌ Плей-офф не запущен.")
        return

    playoff = data["playoff"]

    for pair in playoff["pairs"]:
        if not pair["winner"]:
            bot.reply_to(message, "⚠️ Не все матчи сыграны!")
            return

    current_round = playoff["round"]
    winners = playoff["winners"]

    if current_round == "1/8":
        quarter = [
            {"p1": winners.get("A"), "p2": winners.get("B"), "winner": None, "score1": None, "score2": None, "label": "W"},
            {"p1": winners.get("E"), "p2": winners.get("F"), "winner": None, "score1": None, "score2": None, "label": "X"},
            {"p1": winners.get("G"), "p2": winners.get("H"), "winner": None, "score1": None, "score2": None, "label": "Y"},
            {"p1": winners.get("C"), "p2": winners.get("D"), "winner": None, "score1": None, "score2": None, "label": "Z"}
        ]
        playoff["round"] = "1/4"
        playoff["pairs"] = quarter
        playoff["winners"] = {}
        save_tournament(data)
        show_playoff(message, data)
        return

    if current_round == "1/4":
        qw = {}
        for pair in playoff["pairs"]:
            if pair.get("label") and pair["winner"]:
                qw[pair["label"]] = pair["winner"]

        semi = [
            {"p1": qw.get("W"), "p2": qw.get("X"), "winner": None, "score1": None, "score2": None},
            {"p1": qw.get("Y"), "p2": qw.get("Z"), "winner": None, "score1": None, "score2": None}
        ]
        playoff["round"] = "1/2"
        playoff["pairs"] = semi
        playoff["winners"] = {}
        save_tournament(data)
        show_playoff(message, data)
        return

    if current_round == "1/2":
        winners_list = []
        for pair in playoff["pairs"]:
            if pair["winner"]:
                winners_list.append(pair["winner"])

        if len(winners_list) < 2:
            bot.reply_to(message, "⚠️ Полуфиналы не сыграны!")
            return

        final = [
            {"p1": winners_list[0], "p2": winners_list[1], "winner": None, "score1": None, "score2": None}
        ]
        playoff["round"] = "Финал"
        playoff["pairs"] = final
        playoff["winners"] = {}
        save_tournament(data)
        show_playoff(message, data)
        return

    if current_round == "Финал":
        if not playoff["pairs"][0]["winner"]:
            bot.reply_to(message, "⚠️ Финал ещё не сыгран!")
            return

        champion = playoff["pairs"][0]["winner"]
        data["status"] = "finished"
        save_tournament(data)
        bot.reply_to(
            message,
            f"🏆 *ТУРНИР ЗАВЕРШЁН!*\n\n👑 *ЧЕМПИОН:* {champion}!",
            parse_mode="Markdown"
        )
        return

# ============================================================
# КНОПКИ
# ============================================================

@bot.message_handler(commands=['fstart'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_standings = types.KeyboardButton("📈 Таблица")
    btn_playoff = types.KeyboardButton("🏆 Плей-офф")
    markup.add(btn_standings, btn_playoff)

    bot.reply_to(
        message,
        "🏆 *ТУРНИРНЫЙ БОТ*\n\n"
        "📌 *Команды:*\n"
        "`/fgroups` — таблица групп\n"
        "`/fplayoff` — плей-офф\n"
        "`/fresult_playoff @u1 @u2 3:1`\n"
        "`/fnext_round` — следующий раунд",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "📈 Таблица":
        show_groups(message)
    elif message.text == "🏆 Плей-офф":
        start_playoff(message)

# ============================================================
# ЗАПУСК
# ============================================================

print("✅ Турнирный бот запущен!")
bot.infinity_polling()
