import csv
import asyncio
from telethon import TelegramClient, types
import os

api_id = 77777777  # Замените на ваш
api_hash = "5enb544ecbb4e1" # Замените на ваш

client = TelegramClient("comment_user_scraper", api_id, api_hash)

async def filter_premium_users(input_file="new_users.csv", output_file="new_premium_users.csv"):
    premium_users = []

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                user_id = int(row["user_id"])
                access_hash = int(row["access_hash"])
                user = await client.get_entity(types.InputPeerUser(user_id, access_hash))
                await asyncio.sleep(2)

                if getattr(user, "premium", False):
                    print(f"✅ Premium: {user.username or user.first_name or user.id}")
                    premium_users.append(row)
                else:
                    print(f"⛔️ Не Premium: {user.username or user.first_name or user.id}")

            except Exception as e:
                print(f"[!] Ошибка при проверке {row.get('user_id')}: {e}")
                await asyncio.sleep(2)

    # Сохраняем отфильтрованных
    if premium_users:
        with open(output_file, mode="w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(premium_users)

        print(f"\n💾 Сохранено {len(premium_users)} Premium-пользователей в '{output_file}'")
    else:
        print("\n⚠️ Premium-пользователи не найдены.")

async def main():
    await client.start()
    print("[+] Авторизация успешна")
    await filter_premium_users()
    await client.disconnect()

asyncio.run(main())
