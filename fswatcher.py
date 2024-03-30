import os
import time
import logging
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import json
from datetime import datetime

def load_config():
    try:
        with open('config.json') as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return None

def send_telegram_message(bot_message, config, hostname):
    try:
        bot_token = config.get('botToken')
        bot_chat_id = config.get('botChatID')
        full_message = f'{hostname}: {bot_message}'
        send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={bot_chat_id}&parse_mode=Markdown&text={full_message}'
        response = requests.get(send_text)
        return response.json()
    except Exception as e:
        print(f"Error sending message via Telegram: {e}")

class MyHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.hostname = socket.gethostname()
        super().__init__()

    def is_warning_extension(self, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.config.get('warningExtensions', [])

    def on_created(self, event):
        if event.is_directory:
            if not self.is_skippable(event.src_path):
                logging.info(f'{self.hostname} > [Directory added] > {event.src_path}')
                print(f'{self.hostname} > [Directory added] > {event.src_path}')
                send_telegram_message(f'{event.src_path} > [Directory created > ', self.config, self.hostname)
        elif not event.is_directory:
            if not self.is_skippable(event.src_path):
                logging.info(f'{self.hostname} > [File added] > {event.src_path}')
                print(f'{self.hostname} > [File added] > {event.src_path}')
                if self.is_warning_extension(event.src_path):
                    print(f'{self.hostname} > [WARNING: This file may be malicious] > {event.src_path}')
                    send_telegram_message(f'{self.hostname} > [WARNING: This file may be malicious] >', self.config, self.hostname)

    def on_deleted(self, event):
        if event.is_directory:
            if not self.is_skippable(event.src_path):
                logging.info(f'{self.hostname} > [Directory removed] > {event.src_path}')
                print(f'{self.hostname} > [Directory removed] > {event.src_path}')
        elif not event.is_directory:
            if not self.is_skippable(event.src_path):
                logging.info(f'{self.hostname} > [File removed] > {event.src_path}')
                print(f'{self.hostname} > [File removed] > {event.src_path}')

    def on_modified(self, event):
        if not event.is_directory:
            if not self.is_skippable(event.src_path):
                logging.info(f'{self.hostname} > [File updated] > {event.src_path}')
                print(f'{self.hostname} > [File updated] > {event.src_path}')
                if self.is_warning_extension(event.src_path):
                    print(f'{self.hostname} > [WARNING: This file may be malicious] > {event.src_path}')
                    send_telegram_message(f'{self.hostname} > [WARNING: This file may be malicious] > {event.src_path}', self.config, self.hostname)

    def is_skippable(self, path):
        for item in self.config.get('toSkip', []):
            if item in path:
                return True
        return False

if __name__ == "__main__":
    path = 'hotfolder'
    config = load_config()

    if config:
        logging.basicConfig(filename=f'reports/{datetime.now().strftime("%Y-%m-%d")}.log', level=logging.INFO, format='%(asctime)s - %(message)s')
        event_handler = MyHandler(config)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()
    else:
        print("Invalid configuration. Please check config.json.")
