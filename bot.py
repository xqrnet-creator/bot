import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

topics = []
post_link = None
running = False
ADMIN_ID = None


# ===== GET POST DETAILS =====
def parse_link(link):
    parts = link.split("/")
    chat = parts[-2]
    msg_id = int(parts[-1])
    return chat, msg_id


# ===== START COMMAND =====
@dp.message(Command("start"))
async def start(msg: types.Message):
    global ADMIN_ID
    ADMIN_ID = msg.from_user.id
    await msg.answer("✅ Bot is ready!\n\nUse:\n/add chat_id thread_id\n/setpost link\n/startads")


# ===== ADD TOPIC =====
@dp.message(Command("add"))
async def add(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    try:
        _, chat_id, thread_id = msg.text.split()
        topics.append({"chat_id": int(chat_id), "thread_id": int(thread_id)})
        await msg.answer("✅ Topic added")
    except:
        await msg.answer("❌ Usage: /add chat_id thread_id")


# ===== SET POST LINK =====
@dp.message(Command("setpost"))
async def setpost(msg: types.Message):
    global post_link
    if msg.from_user.id != ADMIN_ID:
        return

    try:
        _, link = msg.text.split()
        post_link = link
        await msg.answer("✅ Post link set")
    except:
        await msg.answer("❌ Usage: /setpost https://t.me/yourchannel/123")


# ===== ADS LOOP =====
async def ads_loop():
    global running

    while running:
        if not post_link or not topics:
            await asyncio.sleep(10)
            continue

        chat, msg_id = parse_link(post_link)

        for t in topics:
            if not running:
                break

            try:
                await bot.forward_message(
                    chat_id=t["chat_id"],
                    from_chat_id=f"@{chat}",
                    message_id=msg_id,
                    message_thread_id=t["thread_id"]
                )

                print(f"Sent to {t['chat_id']}")

                # 1 minute delay
                await asyncio.sleep(60)

            except Exception as e:
                print("Error:", e)

                # wait more if error
                await asyncio.sleep(120)

        print("Cycle done, waiting 5 minutes...")

        # 5 minute break
        await asyncio.sleep(300)


# ===== START ADS =====
@dp.message(Command("startads"))
async def startads(msg: types.Message):
    global running
    if msg.from_user.id == ADMIN_ID:
        running = True
        asyncio.create_task(ads_loop())
        await msg.answer("🚀 Ads started")


# ===== STOP ADS =====
@dp.message(Command("stopads"))
async def stopads(msg: types.Message):
    global running
    if msg.from_user.id == ADMIN_ID:
        running = False
        await msg.answer("⛔ Ads stopped")


# ===== RUN BOT =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
