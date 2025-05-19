import asyncio
import csv
from datetime import datetime
from telethon import TelegramClient, functions, types
import time

api_id = 77777777  # Замените на ваш
api_hash = "452g42fa3f56h" # Замените на ваш

client = TelegramClient("comment_user_scraper", api_id, api_hash)

def load_users_from_csv(filename="etalon_premium_users.csv"):
    users = []
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            time.sleep(2)
            try:
                user_id = int(row["user_id"])
                access_hash = int(row["access_hash"])
                users.append(types.InputPeerUser(user_id=user_id, access_hash=access_hash))
            except Exception as e:
                print(f"[!] Ошибка в CSV: {e}")
    return users

async def view_stories(peers):
    viewed = 0
    for peer in peers:
        try:
            user = await client.get_entity(peer)

            # Проверяем наличие сторис
            if (
                not getattr(user, "stories_unavailable", True)
                and not getattr(user, "stories_hidden", True)
                and getattr(user, "stories_max_id", None)
            ):
                await client(
                    functions.stories.ReadStoriesRequest(
                        peer=await client.get_input_entity(user), #user_id=user.id,
                        max_id=user.stories_max_id
                    )
                )
                viewed += 1
                print(f"👁️ Просмотрены сторис: {user.username or user.id}")
                await asyncio.sleep(1.2)

                story_id = user.stories_max_id
                 # Пробуем оставить реакцию (например, ❤️)
                try:
                    await client(functions.stories.SendReactionRequest(
                        await client.get_input_entity(user), #peer=user.id,
                        story_id=story_id,
                        reaction=types.ReactionEmoji(emoticon="❤️")
                    ))
                    print(f"💬 Реакция отправлена: ❤️ пользователю {user.username or user.id}")
                except Exception as e:
                    print(f"⚠️ Реакция не отправлена: {e}")

                await asyncio.sleep(5)  # 5 секунд
            else:
                print(f"⛔ Нет актуальных сторис: {user.username or user.id}")
                await asyncio.sleep(5)  # 5 секунд
        except Exception as e:
            print(f"[!] Ошибка у {peer.user_id}: {e}")
            await asyncio.sleep(5)  # 5 секунд
    return viewed

async def main_loop():
    await client.start()
    print("[+] Авторизация успешна")

    peers = load_users_from_csv()
    print(f"📋 Загружено пользователей: {len(peers)}")

    while True:
        print(f"\n🕓 Цикл запущен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        count = await view_stories(peers)
        print(f"✅ Всего просмотрено: {count} сторис")

        print("⏳ Жду 2 часа...\n")
        time.sleep(2 * 60 * 60)  # 2 часа

# Запуск
asyncio.run(main_loop())
