import os
import json
import logging
import asyncio
from threading import Thread
from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatMemberUpdated, ChatJoinRequest
from pyrogram.errors import FloodWait

from vars import B_TOKEN, API, API_HASH, BOT_USERNAME, DB_URI, ownerid
from rishabh.users_db import get_served_users, add_served_user
from async_mongo import AsyncClient

# Constants
LOGO_URL = "https://envs.sh/lwo.jpg"
USER_DATA_FILE = "user_data.json"
GROUP_DATA_FILE = "group_data.json"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pyrogram bot client
thanos = Client(
    "bot_started",
    bot_token=B_TOKEN,
    api_id=API,
    api_hash=API_HASH
)

# MongoDB connect
try:
    mongo = AsyncClient(DB_URI)
    db = mongo["Assistant"]
    logger.info("Connected to Mongo Database.")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    exit(1)

usersdb = db["users"]

# Load/Save helpers
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_data(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

user_data = load_data(USER_DATA_FILE)
group_data = load_data(GROUP_DATA_FILE)

def add_to_data(data_list, new_entry, file_path):
    if new_entry not in data_list:
        data_list.append(new_entry)
        save_data(data_list, file_path)

# Handlers
@thanos.on_message(filters.private & filters.command(["start"]))
async def start(client: Client, message: Message):
    try:
        await add_served_user(message.from_user.id)
        logger.info(f"User {message.from_user.id} added.")

        button = [
            [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]
        ]

        await client.send_photo(
            chat_id=message.chat.id,
            photo=LOGO_URL,
            caption="**HELLO...⚡\n\ni am an advanced telegram auto request accept bot.**",
            reply_markup=InlineKeyboardMarkup(button)
        )
    except Exception as e:
        logger.error(f"Start handler error: {e}")
        await message.reply_text(f"Error occurred: {e}")

@thanos.on_chat_member_updated(filters.group)
async def welcome_goodbye(client: thanos, message: ChatMemberUpdated):
    try:
        new_chat_member = message.new_chat_member
        old_chat_member = message.old_chat_member
        chat = message.chat

        if new_chat_member and new_chat_member.status == "member":
            add_to_data(group_data, chat.id, GROUP_DATA_FILE)
            user = new_chat_member.user
            await client.send_message(
                chat_id=chat.id,
                text=f"Hello {user.mention}, welcome to {chat.title}!"
            )

        elif old_chat_member and old_chat_member.status == "left":
            user = old_chat_member.user
            await client.send_message(
                chat_id=chat.id,
                text=f"Goodbye {user.mention}, we will miss you!"
            )
            await client.send_photo(
                chat_id=user.id,
                photo=LOGO_URL,
                caption=(
                    "⚠️ Sorry for the inconvenience caused\n"
                    "🚨 You Can Request any Anime here\n"
                    "👉 https://t.me/saini_sahab19 \n"
                    "🛎️ Help? Msg above bot."
                )
            )
    except Exception as e:
        logger.error(f"welcome_goodbye error: {e}")

@thanos.on_chat_join_request()
async def autoapprove(client: thanos, message: ChatJoinRequest):
    try:
        await client.approve_chat_join_request(chat_id=message.chat.id, user_id=message.from_user.id)

        await client.send_photo(
            chat_id=message.from_user.id,
            photo=LOGO_URL,
            caption=(
                "💋Join for latest collection💋\n\n"
                "• https://discord.com/invite/5ACnAvC2et\n" * 4 +
                "\n🎬 How to use Discord: @HowToUse_Discord"
            )
        )
    except Exception as e:
        logger.error(f"autoapprove error: {e}")

@thanos.on_message(filters.command("stats") & filters.user(ownerid))
async def stats(client: thanos, message: Message):
    users = len(await get_served_users())
    await message.reply_text(f"ᴜsᴇʀs ᴄᴏᴜɴᴛ: {users}")

@thanos.on_message(filters.command("broadcast") & filters.user(ownerid))
async def broadcast(cli: thanos, message: Message):
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    elif len(message.command) < 2:
        return await message.reply_text("Reply to message or use: `/broadcast text`")
    else:
        query = message.text.split(None, 1)[1]

    susr = 0
    served_users = [int(u["user_id"]) for u in await get_served_users()]
    for i in served_users:
        try:
            if message.reply_to_message:
                await cli.copy_message(chat_id=i, from_chat_id=y, message_id=x)
            else:
                await cli.send_message(i, text=query)
            susr += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            await asyncio.sleep(min(e.value, 200))
        except:
            continue
    await message.reply_text(f"Broadcasted to {susr} users.")
    
@thanos.on_message(filters.command("help"))
async def help_command(client, message):
    text = (
        "**Available Commands:**\n\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help menu\n"
        "/stats - Show user stats (owner only)\n"
        "/broadcast - Send message to all users (owner only)\n"
        "/info - Get your user info\n"
        "/users - Show all user IDs (owner only)"
    )
    await message.reply_text(text)

@thanos.on_message(filters.command("info"))
async def info_command(client, message):
    user = message.from_user
    text = (
        f"**User Info:**\n\n"
        f"ID: `{user.id}`\n"
        f"Name: `{user.first_name}`\n"
        f"Username: @{user.username if user.username else 'N/A'}"
    )
    await message.reply_text(text)

@thanos.on_message(filters.command("users") & filters.user(ownerid))
async def list_users(client, message):
    users = await get_served_users()
    user_ids = [str(user["user_id"]) for user in users]
    user_list = "\n".join(user_ids)
    await message.reply_text(f"**Registered Users:**\n\n{user_list}")


# Flask server for Render
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start Flask in background
    Thread(target=run_flask).start()
    # Start bot
    thanos.run()
