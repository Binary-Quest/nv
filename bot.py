import requests
from random import randint
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ================== CONFIG ==================
url = "https://leakosintapi.com/"
bot_token = "6230237564:AAE7x7FhoTe8LCOzXzTXc84rxGYV0PjcNVs"  # Bot token from @BotFather
api_token = "7771703268:SghPFtBt"  # Insert LeakOSINT API token here (string)
lang = "en"
limit = 1000
# ============================================

# Access control (currently allows everyone)
def user_access_test(user_id):
    return True

# Cache for storing reports
cash_reports = {}

# Function for generating reports
def generate_report(query, query_id):
    global cash_reports
    data = {"token": api_token, "request": query.split("\n")[0], "limit": limit, "lang": lang}
    try:
        response = requests.post(url, json=data).json()
    except Exception as e:
        print("Request error:", e)
        return None

    print(response)
    if "Error code" in response:
        print("Error:" + response["Error code"])
        return None

    cash_reports[str(query_id)] = []

    for database_name in response.get("List", {}).keys():
        text = [f"<b>{database_name}</b>", ""]
        text.append(response["List"][database_name].get("InfoLeak", "") + "\n")

        if database_name != "No results found":
            for report_data in response["List"][database_name].get("Data", []):
                for column_name, value in report_data.items():
                    text.append(f"<b>{column_name}</b>: {value}")
                text.append("")

        text = "\n".join(text)
        if len(text) > 3500:
            text = text[:3500] + "\n\nSome data did not fit this message"

        cash_reports[str(query_id)].append(text)

    return cash_reports[str(query_id)]

# Function for creating inline keyboard
def create_inline_keyboard(query_id, page_id, count_page):
    markup = InlineKeyboardMarkup()

    if page_id < 0:
        page_id = count_page - 1
    elif page_id > count_page - 1:
        page_id = page_id % count_page

    if count_page == 1:
        return markup

    markup.row_width = 3
    markup.add(
        InlineKeyboardButton(text="<<", callback_data=f"/page {query_id} {page_id-1}"),
        InlineKeyboardButton(text=f"{page_id+1}/{count_page}", callback_data="page_list"),
        InlineKeyboardButton(text=">>", callback_data=f"/page {query_id} {page_id+1}")
    )
    return markup


bot = telebot.TeleBot(bot_token)

# Start command
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am a telegram-bot that can search for databases.", parse_mode="Markdown")

# Handle text queries
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id
    if not user_access_test(user_id):
        bot.send_message(message.chat.id, "You have no access to the bot")
        return

    if message.content_type == "text":
        query_id = randint(0, 9999999)
        report = generate_report(message.text, query_id)

        if report is None:
            bot.reply_to(message, "The bot does not work at the moment.", parse_mode="Markdown")
            return

        markup = create_inline_keyboard(query_id, 0, len(report))
        try:
            bot.send_message(message.chat.id, report[0], parse_mode="html", reply_markup=markup)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(
                message.chat.id,
                text=report[0].replace("<b>", "").replace("</b>", ""),
                reply_markup=markup
            )

# Handle button presses
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    global cash_reports
    if call.data.startswith("/page "):
        query_id, page_id = call.data.split(" ")[1:]
        if query_id not in cash_reports:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="The results of the request have already been deleted"
            )
        else:
            report = cash_reports[query_id]
            markup = create_inline_keyboard(query_id, int(page_id), len(report))
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=report[int(page_id)],
                    parse_mode="html",
                    reply_markup=markup
                )
            except telebot.apihelper.ApiTelegramException:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=report[int(page_id)].replace("<b>", "").replace("</b>", ""),
                    reply_markup=markup
                )

# Keep the bot running
while True:
    try:
        bot.polling()
    except Exception as e:
        print("Polling error:", e)
        continue
