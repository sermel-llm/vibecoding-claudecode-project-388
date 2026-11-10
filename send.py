"""Отправка сообщения в Telegram.

Запуск: python3 send.py "текст сообщения"

Токен и chat id берутся из переменных окружения TELEGRAM_BOT_TOKEN
и TELEGRAM_CHAT_ID, а если их нет — из файла .env рядом со скриптом.
Использует только стандартную библиотеку Python.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Telegram не принимает сообщения длиннее 4096 символов.
MAX_LENGTH = 4096


def load_env_file(path):
    """Читает строки вида KEY=VALUE из .env, не перекрывая уже заданные переменные."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def split_text(text):
    """Делит длинный текст на части по строкам, чтобы каждая влезла в одно сообщение."""
    parts, current = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > MAX_LENGTH:
            if current:
                parts.append(current)
                current = ""
            parts.append(line[:MAX_LENGTH])
            line = line[MAX_LENGTH:]
        if len(current) + len(line) > MAX_LENGTH:
            parts.append(current)
            current = ""
        current += line
    if current:
        parts.append(current)
    return parts


def send(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    with urllib.request.urlopen(url, data=data, timeout=20) as response:
        return json.load(response)


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print('Использование: python3 send.py "текст сообщения"', file=sys.stderr)
        return 2

    load_env_file(Path(__file__).resolve().parent / ".env")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    missing = [name for name, value in
               (("TELEGRAM_BOT_TOKEN", token), ("TELEGRAM_CHAT_ID", chat_id)) if not value]
    if missing:
        print(f"Ошибка: не заданы {', '.join(missing)} (в окружении или в .env).", file=sys.stderr)
        return 1

    try:
        for part in split_text(sys.argv[1]):
            send(token, chat_id, part)
    except urllib.error.HTTPError as error:
        # Ответ Telegram содержит понятное описание ошибки; токен в него не попадает.
        try:
            description = json.load(error).get("description", "")
        except (ValueError, AttributeError):
            description = ""
        print(f"Ошибка Telegram {error.code}: {description or error.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(f"Ошибка сети: не удалось связаться с api.telegram.org ({error.reason}).", file=sys.stderr)
        return 1

    print("Отправлено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

