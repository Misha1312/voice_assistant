import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import urllib.parse
import pyautogui
import pystray
from PIL import Image
import threading
import sys
import re
import getpass
import time

# Инициализация синтеза речи
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # Базовая скорость речи
engine.setProperty('volume', 0.9)  # Громкость
voices = engine.getProperty('voices')
for voice in voices:
    if "russian" in voice.name.lower() or "ru" in voice.id.lower():
        engine.setProperty('voice', voice.id)  # Русский голос
        break

# Инициализация распознавания речи
recognizer = sr.Recognizer()
mic = sr.Microphone()
recognizer.energy_threshold = 300  # Базовый порог энергии
recognizer.dynamic_energy_threshold = True  # Динамическая адаптация

# Имя ассистента (wake word) и тайный режим
WAKE_WORD = "ассистент"
secret = True

# Флаг для управления прослушкой
listening_enabled = True

# Пути к приложениям (Telegram и Spotify)
USERNAME = getpass.getuser()
TELEGRAM_PATH = f"C:\\Users\\{USERNAME}\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe"
SPOTIFY_PATH = f"C:\\Users\\{USERNAME}\\AppData\\Roaming\\Spotify\\Spotify.exe"

# Функция для выполнения команд
def execute_command(command):
    global WAKE_WORD, listening_enabled, secret
    command = command.lower().replace(WAKE_WORD.lower(), "").strip()
    print(f"Обработка команды: {command}")
    if "открой браузер" in command:
        os.system("start chrome")
        speak("Открываю")
    elif "открой блокнот" in command:
        os.system("start notepad")
        speak("Открываю")
    elif "сосал" in command and secret:
        speak("Да")
    elif "что делает кфг флюгера" in command and secret:
        speak("Бустит")
    elif "открой дота" in command or "открой dota" in command:
        os.system("start steam://run/570")
        speak("Дота два запускается")
    elif "стоп" in command:
        speak("Прослушка остановлена")
        return False
    elif "спасибо" in command:
        speak("Незачто, что еще сделать?")
    elif "открой youtube" in command:
        speak("Открываю")
        webbrowser.open("https://www.youtube.com")
    elif "найди в интернете" in command:
        speak("Назови запрос")
        query = listen_for_query()
        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            speak(f"Поиск {query} выполнен")
        else:
            speak("Запрос не распознан")
    elif "найди видео" in command:
        speak("Назови тему видео")
        query = listen_for_query()
        if query:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(url)
            speak(f"Поиск видео {query} выполнен")
        else:
            speak("Запрос не распознан")
    elif "чей крым" in command:
        speak("Украины")
    elif "тайный режим" in command:
        if not secret:
            speak("Тайный режим включен")
            secret = True
        else:
            speak("Тайный режим выключен")
            secret = False
    elif "на рабочий стол" in command:
        pyautogui.hotkey('win', 'd')
        speak("Рабочий стол открыт")
    elif "измени имя" in command:
        speak("Назови новое имя")
        new_name = listen_for_query()
        if new_name and len(new_name.strip()) >= 2 and re.match(r'^[a-zа-яё\s]+$', new_name.lower()):
            WAKE_WORD = new_name.strip().lower()
            speak(f"Теперь моё имя {WAKE_WORD}")
        else:
            speak("Имя не распознано, слишком короткое или содержит недопустимые символы")
    elif "открой ворд" in command or "открой word" in command:
        try:
            os.system("start winword")
            speak("Открываю Word")
        except OSError:
            speak("Приложение не найдено")
    elif "открой телеграм" in command or "открой telegram" in command:
        if os.path.exists(TELEGRAM_PATH):
            try:
                os.startfile(TELEGRAM_PATH)
                speak("Открываю Telegram")
            except OSError:
                speak("Не удалось открыть Telegram")
        else:
            speak("Приложение не найдено")
    elif "открой спотифай" in command or "открой spotify" in command:
        if os.path.exists(SPOTIFY_PATH):
            try:
                os.startfile(SPOTIFY_PATH)
                speak("Открываю Spotify")
                print(f"Открывается Spotify: {SPOTIFY_PATH}")
            except OSError:
                speak("Не удалось открыть Spotify")
                print(f"Ошибка открытия Spotify: {SPOTIFY_PATH}")
        else:
            speak("Приложение не найдено")
            print(f"Spotify не найден: {SPOTIFY_PATH}")
    else:
        speak("Команда не распознана")
    return True

# Функция для синтеза речи
def speak(text):
    try:
        print(f"Синтез речи: {text}")
        engine.say(text)
        engine.runAndWait()
    except RuntimeError as e:
        print(f"Ошибка синтеза речи: {e}")

# Функция для прослушивания wake word и команд
def listen(is_command=False):
    with mic as source:
        print("Прослушка wake word" if not is_command else "Прослушка команды")
        try:
            audio = recognizer.listen(source, timeout=0, phrase_time_limit=2)
            text = recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"Распознан текст: {text}")
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            print("Ничего не распознано")
            return ""
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            speak("Ошибка сервиса распознавания")
            return ""
        except Exception as e:
            print(f"Ошибка прослушивания: {e}")
            return ""

# Функция для 8-секундной записи запроса или имени
def listen_for_query():
    with mic as source:
        print("Прослушка запроса (8 сек)")
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=8)
            text = recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"Распознан запрос: {text}")
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            print("Запрос не распознан")
            return ""
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            speak("Ошибка сервиса распознавания")
            return ""
        except Exception as e:
            print(f"Ошибка прослушивания запроса: {e}")
            return ""

# Основной цикл ассистента
def assistant_loop():
    global listening_enabled, WAKE_WORD
    while True:
        try:
            if listening_enabled:
                text = listen()
                if not text:
                    time.sleep(0.01)
                    continue
                if WAKE_WORD.lower() in text.lower():
                    speak("Я слушаю")
                    while listening_enabled:
                        command = listen(is_command=True)
                        if command and not execute_command(command):
                            listening_enabled = True
                            break
                        time.sleep(0.01)
        except Exception as e:
            print(f"Ошибка в цикле ассистента: {e}")

# Функция для создания иконки трея
def create_tray_icon():
    try:
        image = Image.open("icon.ico")
    except FileNotFoundError:
        print("Иконка icon.ico не найдена, используется заглушка")
        image = Image.new('RGB', (64, 64), color='blue')
    icon = pystray.Icon("Voice Assistant", image, "Голосовой ассистент")
    menu = (
        pystray.MenuItem("Включить прослушку", lambda: enable_listening(icon)),
        pystray.MenuItem("Остановить прослушку", lambda: disable_listening(icon)),
        pystray.MenuItem("Выход", lambda: exit_program(icon))
    )
    icon.menu = menu
    icon.run()

# Включить прослушку
def enable_listening(icon):
    global listening_enabled
    listening_enabled = True
    icon.notify("Прослушка включена", "Голосовой ассистент")
    print("Прослушка включена")

# Отключить прослушку
def disable_listening(icon):
    global listening_enabled
    listening_enabled = False
    icon.notify("Прослушка остановлена", "Голосовой ассистент")
    print("Прослушка остановлена")

# Выход из программы
def exit_program(icon):
    print("Выход из программы")
    icon.stop()
    sys.exit()

# Главная функция
def main():
    print("Запуск ассистента")
    with mic as source:
        print("Адаптация шума микрофона")
        recognizer.adjust_for_ambient_noise(source, duration=0.1)
    assistant_thread = threading.Thread(target=assistant_loop, daemon=True)
    assistant_thread.start()
    create_tray_icon()

if __name__ == "__main__":
    main()