# FileSystem Watcher (FSWatcher)

## Overview
FSWatcher is a Python script that monitors file system events in a specified directory and sends notifications via Telegram when certain events occur.

## Features
- Monitors file creation, deletion, and modification events.
- Sends notifications to Telegram when warning conditions are met.
- Excludes specified directories from monitoring based on configuration.

## Prerequisites
Before running the script, ensure you have the following installed:
- Python 3.x
- Required Python packages: `watchdog`, `requests`

## Configuration
1. Create a `config.json` file with the following structure:
```json
{
  "botToken": "YOUR_TELEGRAM_BOT_TOKEN",
  "botChatID": "YOUR_TELEGRAM_CHAT_ID",
  "warningExtensions": [".exe", ".bat", ".com"],
  "toSkip": ["node_modules", "temp"]
}
