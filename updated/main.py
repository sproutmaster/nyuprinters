from os import environ
from datetime import datetime
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
}


async def get_status(session: aiohttp.ClientSession, db, url: str, printer_id: int, delay: int = 0) -> dict | None:
    """
    Gets printer status from sourced
    :param session: session
    :param db: database connection
    :param url: query url
    :param printer_id: printer id
    :param delay: delay to wait before sending request
    :return: response
    """
    await asyncio.sleep(delay)
    try:
        async with session.get(url, timeout=STATE['session_timeout']) as resp:
            res = json.loads(await resp.text())
            res.setdefault('meta', {})
            res['meta']['status'] = res['response']['status']

            # we move sensitive data from response and add to meta. Statusd can add/delete this data from meta
            del res['response']['status']
            del res['request']

            cur = db.cursor()

            # get current_state value from db
            cur.execute("SELECT current_state, last_online FROM printers WHERE id = %s", (printer_id,))
            current_state = cur.fetchone()[0]
            last_online = cur.fetchone()[1]

            if res['meta']['status'] == 'success':
                res['meta']['serial'] = res['response']['message']['serial']

                del res['response']['message']['host']
                del res['response']['message']['serial']

                last_online = datetime.now()

            cur.execute("INSERT INTO printers "
                        "(current_state, last_state, last_online, last_updated) VALUES (%s, %s) "
                        "WHERE id = (%s)",
                        (json.dumps(res), current_state, last_online, datetime.now(),
                         printer_id,))

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
        cur.execute("SELECT id, ip_address FROM printers WHERE display = TRUE")
        rows = cur.fetchall()
        cur.close()

        # rows -> [(id, ip), (id, ip), ...]

        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                t = 0
                for row in rows:
                    url = f'{sourced_uri}?ip={row[1]}'
                    tasks.append(asyncio.ensure_future(get_status(session, db, url, row[0], t)))
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
