from os import environ
from datetime import datetime
from pytz import timezone
import psycopg2
import aiohttp
import asyncio
import json
import sys

STATE = {
    "running": False,  # updated_run
    "refresh_interval": 0,  # updated_update_interval
    "session_timeout": 0,  # updated_try_timout
    "delay": 0,  # updated_try_delay_factor
    "constant_field_updates": False,  # updated_constant_field_updates
}


async def get_status(session: aiohttp.ClientSession, db, sourced_uri: str, ip: str, delay: int = 0) -> dict | None:
    """
    Gets printer status from sourced
    :param session: session
    :param db: database connection
    :param sourced_uri: sourced uri
    :param ip: printer ip
    :param delay: delay to wait before sending request
    :return: response
    """
    url = f'{sourced_uri}?ip={ip}'
    await asyncio.sleep(delay)
    try:
        async with session.get(url, timeout=STATE['session_timeout']) as resp:
            raw_resp = json.loads(await resp.text())
            resp = raw_resp['response']

            cur = db.cursor()
            cur.execute("SELECT current_state, last_state, last_online FROM printers WHERE ip_address = %s", (ip,))

            current_state = cur.fetchone()[0]
            last_state = cur.fetchone()[1]
            last_online = cur.fetchone()[2]

            if resp['status'] == 'success':
                if STATE['constant_field_updates']:
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

            cur.close()
            db.commit()

    except asyncio.TimeoutError:
        return None


async def main():
    """
    Read printer IPs from database and use printer info snatcher to get the data. After getting the data push it
    into db
    """
    sourced_uri = environ.get("SOURCED_URI", default="http://localhost:8000")
    postgres_uri = environ.get("POSTGRES_URI", default="postgresql://admin:admin@localhost:5432/nyup")

    db = psycopg2.connect(postgres_uri)

    # check if services are online, else throw an error
    async def update_data() -> None:
        """
        Get all IP addresses from database and add data fetch task to queue. After getting the data, push it into db
        """
        cur = db.cursor()
        cur.execute("SELECT ip_address FROM printers WHERE display = TRUE")
        rows = cur.fetchall()
        cur.close()

        # rows -> [(ip), (ip), ...]

        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                t = 0
                for row in rows:
                    tasks.append(asyncio.ensure_future(get_status(session, db, sourced_uri, row[0], t)))
                    t += STATE['delay']
                await asyncio.gather(*tasks)

        except aiohttp.ServerDisconnectedError:
            return None

    def update_state():
        """
        Update state settings from database
        """
        cur = db.cursor()
        cur.execute("SELECT key, value FROM settings WHERE key like 'updated_%'")
        settings = dict(cur.fetchall())
        cur.close()

        global STATE
        STATE = {
            "running": bool(settings['updated_run']),
            "refresh_interval": int(settings['updated_update_interval']),
            "session_timeout": int(settings['updated_try_timout']),
            "delay": int(settings['updated_try_delay_factor']),
            "constant_field_updates": bool(settings['updated_constant_field_updates']),
        }

        print(f"Running: {STATE['running']}, Sleeping for: {STATE['refresh_interval']} sec")

    # XXX: execution starts from here
    """
    Update state settings from database. If running state is true, update data and sleep for refresh interval
    """
    while True:
        update_state()
        global STATE
        if STATE['running']:
            await update_data()
        await asyncio.sleep(STATE['refresh_interval'])


if __name__ == '__main__':
    if sys.platform == 'linux':
        asyncio.run(main())
    elif sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
