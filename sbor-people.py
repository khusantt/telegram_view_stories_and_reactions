import asyncio
import csv
from telethon import TelegramClient, errors, types
import logging

logging.basicConfig(filename='log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

api_id = 77777777 # Замените на ваш
api_hash = "gfdgw4554tw4" # Замените на ваш

client = TelegramClient("comment_user_scraper", api_id, api_hash)

async def get_commenters_from_channel(channel_username, posts_limit=5):
    commenters = {}

    try:
        channel = await client.get_entity(channel_username)
        await asyncio.sleep(2)
        #print(f"\n🔍 Канал: {channel.title}")
        logging.info(f"\n🔍 Канал: {channel.title}")

        count = 0
        async for post in client.iter_messages(channel, limit=posts_limit):
            if not post.replies or not post.replies.comments:
                continue  # нет комментариев
            count += 1
            #print(f"  └─ Пост ID {post.id} с комментариями")
            logging.info(f"  └─ Пост ID {post.id} с комментариями")

            # Получаем комментарии как реплаи
            async for comment in client.iter_messages(channel, reply_to=post.id):
                user = comment.sender
                if user and user.id not in commenters:
                    commenters[user.id] = user
                    await asyncio.sleep(2)
                elif user is None:
                    #print("    ⚠️ Комментарий от имени группы/канала — пропущен")
                    logging.info(f"  └─ Пост ID {post.id} с комментариями")

    except Exception as e:
        #print(f"[!] Ошибка при обработке {channel_username}: {e}")
        logging.error(f"[!] Ошибка при обработке {channel_username}: {e}")

    return commenters


def save_users_to_csv(users, filename="new_users.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "username", "first_name", "last_name", "access_hash"])
        for user in users.values():
            user_id = getattr(user, "id", "")
            username = getattr(user, "username", "")
            first_name = getattr(user, "first_name", "")
            last_name = getattr(user, "last_name", "")
            access_hash = getattr(user, "access_hash", "")

            # Игнорируем объекты без user_id или access_hash (например, каналы)
            if not user_id or not access_hash:
                continue

            writer.writerow([
                user_id,
                username,
                first_name,
                last_name,
                access_hash
            ])
    #print(f"\n💾 Сохранено в файл: {filename}")
    logging.info(f"\n💾 Сохранено в файл: {filename}")


async def main():
    await client.start()
    #print("[+] Авторизация успешна")
    logging.info("[+] Авторизация успешна")

    all_users = {}

    with open("groups.txt", "r") as f:
        links = [line.strip() for line in f if line.strip()]

    for link in links:
        if link.startswith("https://t.me/"):
            link = link.split("/")[-1]
        commenters = await get_commenters_from_channel(link, posts_limit=5)
        #print(f"  └─ Комментаторов найдено: {len(commenters)}")
        logging.info(f"  └─ Комментаторов найдено: {len(commenters)}")
        await asyncio.sleep(2)
        all_users.update(commenters)

    #print(f"\n✅ Всего уникальных пользователей: {len(all_users)}")
    logging.info(f"\n✅ Всего уникальных пользователей: {len(all_users)}")

    for uid, user in all_users.items():
        if not isinstance(user, types.User):
                logging.info(f"⛔ Пропущен объект не User: {type(user)}")
                #print(f"⛔ Пропущен объект не User: {type(user)}")
                continue
        name = user.username or f"{user.first_name or ''} {user.last_name or ''}".strip()
        #print(f"{uid} : {name}")

    save_users_to_csv(all_users)
    await client.disconnect()

asyncio.run(main())
