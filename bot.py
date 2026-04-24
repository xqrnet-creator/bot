import asyncio
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ADMIN_ID = None
running = False

topics = []
ads = []
last_channel_post = None

# ===== START =====
@dp.message(Command("start"))
async def start(msg: types.Message):
    global ADMIN_ID
    ADMIN_ID = msg.from_user.id
    await msg.answer("🔥 PRO ADS BOT READY\n/addgroup\n/addad\n/autochannel\n/startads")

# ===== ADD GROUP =====
@dp.message(Command("addgroup"))
async def add_group(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    try:
        _, chat_id, thread_id = msg.text.split()
        topics.append({"chat_id": int(chat_id), "thread_id": int(thread_id)})
        await msg.answer("✅ Group added")
    except:
        await msg.answer("Usage: /addgroup chat_id thread_id")

# ===== ADD AD =====
@dp.message(Command("addad"))
async def add_ad(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("Send your ad now")

    @dp.message()
    async def save_ad(m: types.Message):
        ads.append(m)
        await m.answer("✅ Ad saved")

# ===== AUTO CHANNEL POST =====
@dp.channel_post()
async def get_channel_post(message: types.Message):
    global last_channel_post
    last_channel_post = message

# ===== ADS LOOP =====
async def ads_loop():
    global running

    sent_count = 0

    while running:
        if not topics:
            await asyncio.sleep(10)
            continue

        for t in topics:
            if not running:
                break

            try:
                # choose source
                if ads:
                    ad = random.choice(ads)
                    await bot.copy_message(
                        chat_id=t["chat_id"],
                        from_chat_id=ad.chat.id,
                        message_id=ad.message_id,
                        message_thread_id=t["thread_id"]
                    )
                elif last_channel_post:
                    await bot.forward_message(
                        chat_id=t["chat_id"],
                        from_chat_id=last_channel_post.chat.id,
                        message_id=last_channel_post.message_id,
                        message_thread_id=t["thread_id"]
                    )

                sent_count += 1
                print(f"Sent {sent_count}")

                # smart delay
                await asyncio.sleep(random.randint(60, 120))

            except Exception as e:
                print("Error:", e)
                await asyncio.sleep(180)

        print("Cycle complete")

        # long break
        await asyncio.sleep(random.randint(300, 600))

# ===== START ADS =====
@dp.message(Command("startads"))
async def start_ads(msg: types.Message):
    global running
    if msg.from_user.id == ADMIN_ID:
        running = True
        asyncio.create_task(ads_loop())
        await msg.answer("🚀 Ads Started")

# ===== STOP ADS =====
@dp.message(Command("stopads"))
async def stop_ads(msg: types.Message):
    global running
    running = False
    await msg.answer("⛔ Ads Stopped")

# ===== RUN =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
