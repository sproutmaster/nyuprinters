from time import sleep
from dataclasses import dataclass
from os import environ
from sys import stderr

import psycopg2
import threading


@dataclass
class Env:
    sourced_url = environ.get("SOURCED_URL", default="http://localhost:8000")
    postgres_url = environ.get("POSTGRES_URL", default="postgresql://admin:admin@localhost:5432/nyup")
    db = None

    def __post_init__(self):
        try:
            self.db = psycopg2.connect(self.postgres_url)
        except Exception as e:
            print(f"Error connecting to database: {e}", file=stderr)
            exit(1)


env = Env()


@dataclass
class Setting:
    running: bool = False  # updated_run
    refresh_interval: int = 0  # updated_update_interval
    session_timeout: int = 0  # updated_try_timout
    delay: int = 0  # updated_try_delay_factor
    constant_field_updates: bool = False  # updated_constant_field_updates


setting = Setting()


class ConfigUpdater:
    def __init__(self, _setting):
        self.setting = _setting
        self.stop_event = threading.Event()

    def update(self):
        while not self.stop_event.is_set():
            try:
                cur = env.db.cursor()
                cur.execute("SELECT key, value FROM settings WHERE key like 'updated_%'")
                settings = dict(cur.fetchall())
                cur.close()

                run = settings['updated_run'] == 'true'

                if run != self.setting.running:
                    print("-- Starting --" if not self.setting.running else "-- Stop --")

                self.setting.running = run
                self.setting.refresh_interval = int(settings['updated_update_interval'])
                self.setting.session_timeout = int(settings['updated_try_timout'])
                self.setting.delay = int(settings['updated_try_delay_factor'])
                self.setting.constant_field_updates = settings['updated_constant_field_updates'] == 'true'

                sleep(3)

            except Exception as e:
                config_updater.stop()
                print("-- Exit(1) --", e)
                exit(1)

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()

    def stop(self):
        self.stop_event.set()


config_updater = ConfigUpdater(setting)
config_updater.start()
