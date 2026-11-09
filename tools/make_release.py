# Собирает архив для игроков: распаковать в папку Exile UI — и всё на месте, Python не нужен.
# Использование: python tools/make_release.py "<папка Exile UI>"
#   (из неё берутся картинки-подсказки акт-трекера, чтобы положить их копии под русскими именами)
# Результат: .tmp/release/Exile-UI-ru-<версия>.zip
#   data/ru/...                                   — файлы перевода
#   img/GUI/leveling tracker/hints/<рус>.jpg      — копии картинок автора Exile UI (лицензия MIT)
#   ПРОЧТИ.txt, LICENSE-Exile-UI.md
import json, os, sys, zipfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
exile = sys.argv[1]
ver = json.load(open(os.path.join(ROOT, "base", "version.json"), encoding="utf-8"))["release"]
os.makedirs(os.path.join(ROOT, ".tmp", "release"), exist_ok=True)
dst = os.path.join(ROOT, ".tmp", "release", f"Exile-UI-ru-{ver}.zip")

hints = {k: v for k, v in json.load(open(os.path.join(HERE, "hints_ru.json"), encoding="utf-8")).items() if not k.startswith("_")}
hdir = os.path.join(exile, "img", "GUI", "leveling tracker", "hints")
missing = [v for v in hints.values() if not os.path.isfile(os.path.join(hdir, v))]
if missing:
    sys.exit(f"нет картинок-подсказок в {hdir}: {missing}")

readme = f"""Русский языковой пакет для Exile UI (версия программы {ver})
https://github.com/Elledar/Exile-UI-ru

Установка:
1. Закройте Exile UI. Распакуйте этот архив прямо в папку Exile UI (где лежит «Exile UI.ahk»),
   согласившись на объединение папок data и img.
2. Шрифт с русскими буквами: скачайте Fontin Sans CR Small Caps (файл FontinSansCR-SC.ttf),
   переименуйте в alt_font_FontinSansCR-SC.ttf и положите в папку data программы.
3. В игре включите русский язык. Запустите Exile UI, в настройках: General → Language → RU.
4. Если акт-трекер уже был запущен на английском, сбросьте его прогресс: зажмите кнопку «‹» на 1 секунду.

Подробности и что уже переведено — на странице проекта.
Картинки-подсказки акт-трекера — копии картинок Exile UI (автор Lailloken, лицензия MIT, см. LICENSE-Exile-UI.md).
"""
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(os.path.join(ROOT, "ru"))):
        z.write(os.path.join(ROOT, "ru", f), f"data/ru/{f}")
    for ru, en in hints.items():
        z.write(os.path.join(hdir, en), f"img/GUI/leveling tracker/hints/{ru.replace(' ', '_')}.jpg")
    z.writestr("ПРОЧТИ.txt", readme.replace("\n", "\r\n").encode("utf-8-sig"))
    z.write(os.path.join(ROOT, "base", "LICENSE.md"), "LICENSE-Exile-UI.md")
print(f"готово: {dst} ({os.path.getsize(dst) // 1024} КБ, {len(hints)} подсказок)")
