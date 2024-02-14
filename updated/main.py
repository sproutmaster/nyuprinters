from datetime import datetime
from time import sleep

from pytz import timezone
import aiohttp
import asyncio
import json
import sys

from app import env, setting


async def get_status(session: aiohttp.ClientSession, db, ip: str, delay: int = 0) -> dict | None:
    """
    Gets printer status from sourced
    :param session: session
    :param db: database connection
    :param ip: printer ip
    :param delay: delay to wait before sending request
    :return: response
    """
    url = f'{env.sourced_url}?ip={ip}'
    await asyncio.sleep(delay)
    print(f"update queue: {ip}")
    try:
        async with session.get(url, timeout=setting.session_timeout) as resp:
            raw_resp = json.loads(await resp.text())
            resp = raw_resp['response']

            cur = db.cursor()
            cur.execute("SELECT current_state, last_state, last_online FROM printers WHERE ip_address = %s", (ip,))

            db_result = cur.fetchone()

            current_state = db_result[0]
            last_state = db_result[1]
            last_online = db_result[2]

            if resp['status'] == 'success':
                if setting.constant_field_updates:
                    serial = resp['message']['serial']
                    type_ = resp['message']['type']
                    model = resp['message']['model']

                    cur.execute("UPDATE printers SET "
                                "serial = %s, type = %s, model = %s "
                                "WHERE ip_address = %s",
                                (serial, type_, model,
                                 ip,))

                last_state = current_state
                current_state = json.dumps(resp)
                last_online = datetime.now(timezone('UTC'))

                del resp['message']['host']
                del resp['message']['serial']
                del resp['message']['model']
                del resp['message']['type']

            cur.execute("UPDATE printers SET "
                        "current_state = %s, last_state =%s, last_online = %s "
                        "WHERE ip_address = %s",
                        (current_state, last_state, last_online,
                         ip,))

            print(f"updated: {ip}")

            cur.close()
            db.commit()

    except asyncio.TimeoutError:
        return None


async def main():
    """
    Read printer IPs from database and use printer info snatcher to get the data. After getting the data push it
    into db
    """
    db = env.db

    # check if services are online, else throw an error
    async def update_data() -> None:
        """
        Get all IP addresses from database and add data fetch task to queue. After getting the data, push it into db
        """
        cur = db.cursor()
        cur.execute("SELECT ip_address FROM printers WHERE visible = TRUE")
        rows = cur.fetchall()
        cur.close()

        # rows -> [(ip), (ip), ...]

        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                t = 0
                for row in rows:
                    tasks.append(asyncio.ensure_future(get_status(session, db, row[0], t)))
                    t += setting.delay
                await asyncio.gather(*tasks)

        except aiohttp.ServerDisconnectedError:
            return None

    # XXX: execution starts from here
    """
    Update state settings from database. If running state is true, update data and sleep for refresh interval
    """
    while True:
        if setting.running:
            await update_data()
        await asyncio.sleep(setting.refresh_interval)


if __name__ == '__main__':
    sleep(5)
    if sys.platform == 'linux':
        asyncio.run(main())
    elif sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
