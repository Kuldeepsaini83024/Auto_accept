import os
import json
import logging
from vars import *
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatMemberUpdated, ChatJoinRequest
import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from rishabh.users_db import get_served_users, add_served_user
from sys import exit
from async_mongo import AsyncClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot
thanos = Client(
    "bot_started",
    bot_token=B_TOKEN,
    api_id=API,
    api_hash=API_HASH
)

# File paths for storing data
USER_DATA_FILE = "user_data.json"
GROUP_DATA_FILE = "group_data.json"






try:
    mongo = AsyncClient(DB_URI)
    db = mongo["Assistant"]
    logger.info("Connected to your Mongo Database.")
except Exception as e:
    logger.error(f"Failed to connect to your Mongo Database.\ {e}")
    exit(1)

usersdb = db["users"]
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return []

def save_data(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

user_data = load_data(USER_DATA_FILE)
group_data = load_data(GROUP_DATA_FILE)

def add_to_data(data_list, new_entry, file_path):
    if new_entry not in data_list:
        data_list.append(new_entry)
        save_data(data_list, file_path)

@thanos.on_message(filters.private & filters.command(["start"]))
async def start(client: thanos, message: Message):
    try:
        await add_served_user(message.from_user.id)
        button = [
            [
                InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
            ]
        ]
        await message.reply_text(
            text="**HELLO...⚡\n\ni am an advanced telegram auto request accept bot.**",
            reply_markup=InlineKeyboardMarkup(button),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in start handler: {e}")

@thanos.on_chat_member_updated(filters.group)
async def welcome_goodbye(client: thanos, message: ChatMemberUpdated):
    try:
        new_chat_member = message.new_chat_member
        old_chat_member = message.old_chat_member
        chat = message.chat

        if new_chat_member:
            if new_chat_member.status == "member":
                add_to_data(group_data, chat.id, GROUP_DATA_FILE)
                user = new_chat_member.user
                logger.info(f"{user.first_name} joined {chat.title}")
                await client.send_message(
                    chat_id=chat.id,
                    text=f"Hello {user.mention}, welcome to {chat.title}!"
                )
        elif old_chat_member:
            if old_chat_member.status == "left":
                user = old_chat_member.user
                logger.info(f"{user.first_name} left {chat.title}")
                await client.send_message(
                    chat_id=chat.id,
                    text=f"Goodbye {user.mention}, we will miss you in {chat.title}!"
                )

                # Send a personal goodbye message to the user
                personal_goodbye_message = (
                    "⚠️ Sorry for the inconvenience caused\n"
                    "🚨 You Can Request 𝙎𝘼𝙄𝙉𝙄 𝙎𝘼𝙃𝘼𝘽\n"
                    "👉 https://t.me/saini_sahab_19 \n"
                    "🛎️ Koi bhi Help ke liye msg here ☝️"
                )

                await client.send_message(
                    chat_id=user.id,
                    text=personal_goodbye_message
                )
    except Exception as e:
        logger.error(f"Error in welcome_goodbye handler: {e}")

@thanos.on_chat_join_request()
async def autoapprove(client: thanos, message: ChatJoinRequest):
    try:
        await client.approve_chat_join_request(chat_id=message.chat.id, user_id=message.from_user.id)
        logger.info(f"Approved join request for {message.from_user.first_name} in {message.chat.title}")

        # Send a welcome message to the group or channel
        #await client.send_message(
          #  chat_id=message.chat.id,
          #  text=f"Hello {message.from_user.mention}, welcome to {message.chat.title}!"
     #   )

        # Send a personal welcome message to the user
        personal_message = (
    f"👋 𝗛𝗲𝗹𝗹𝗼 {message.from_user.mention}, Welcome to the Learning Zone! \n\n"
    "🔰 𝗪𝗵𝗮𝘁 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗚𝗲𝘁 𝗛𝗲𝗿𝗲?\n"
    "1⃣ Quality Notes for Your Exam Preparation\n"
    "2⃣ Free Live / Recorded Classes\n"
    "3⃣ Study Materials, PDFs, and Practice Sets\n\n"
    "✊ 𝗝𝗼𝗶𝗻 𝗼𝘂𝗿 𝗘𝗱𝘂𝗰𝗮𝘁𝗶𝗼𝗻 𝗖𝗼𝗺𝗺𝘂𝗻𝗶𝘁𝘆 — <b>𝙎𝘼𝙄𝙉𝙄 𝙎𝘼𝙃𝘼𝘽</b>\n"
    "1⃣ Doubts clear karo aur sawal puchho\n"
    "2⃣ Important updates aur tips har roz pao\n"
    "3⃣ Apne jaise students ke saath interact karo\n\n"
    "♥️ Join Now and Start Learning 👇\n"
    '<a href="https://t.me/saini_sahab19">𝙎𝘼𝙄𝙉𝙄 𝙎𝘼𝙃𝘼𝘽</a>\n'
    '<a href="https://t.me/saini_sahab19">𝙎𝘼𝙄𝙉𝙄 𝙎𝘼𝙃𝘼𝘽</a>\n'
    '<a href="https://t.me/saini_sahab19">𝙎𝘼𝙄𝙉𝙄 𝙎𝘼𝙃𝘼𝘽</a>\n\n'
    "📌 Type /start to explore more study tools and resources!"
)

        await client.send_message(
            chat_id=message.from_user.id,
            text=personal_message
        )
    except Exception as e:
        logger.error(f"Error in autoapprove handler: {e}")



@thanos.on_message(filters.command("stats") & filters.user(ownerid))
async def stats(client: thanos, message: Message):
    users = len(await get_served_users())
    await message.reply_text(
        f"<u><b>ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛs ᴏғ {client.me.mention} :</b></u>\n\n➻ <b>ᴜsᴇʀs :</b> {users}\n"
    )


@thanos.on_message(filters.command("broadcast") & filters.user(ownerid))
async def broadcast(cli: thanos, message: Message):
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(
                "<b>ᴇxᴀᴍᴘʟᴇ </b>:\n/broadcast [ᴍᴇssᴀɢᴇ] ᴏʀ [ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ]"
            )
        query = message.text.split(None, 1)[1]
    susr = 0
    served_users = []
    susers = await get_served_users()
    for user in susers:
        served_users.append(int(user["user_id"]))
    for i in served_users:
        try:
            m = (
                await cli.copy_message(chat_id=i, from_chat_id=y, message_id=x)
                if message.reply_to_message
                else await cli.send_message(i, text=query)
            )
            susr += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            flood_time = int(e.value)
            if flood_time > 200:
                continue
            await asyncio.sleep(flood_time)
        except:
            continue

    try:
        await message.reply_text(f"<b>ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ ᴛᴏ {susr} ᴜsᴇʀs.</b>")
    except:
        pass

if __name__ == "__main__":
    thanos.run()
    
