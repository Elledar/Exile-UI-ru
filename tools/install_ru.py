# Устанавливает русский пакет в Exile UI.
# Использование: python tools/install_ru.py <папка Exile UI>
#   - копирует файлы из ru/ в <Exile UI>\data\ru\
#   - создаёт копии картинок-подсказок акт-трекера под русскими именами (tools/hints_ru.json)
# Картинки автора не распространяются с пакетом — они копируются внутри вашей установки программы.
import json, os, shutil, sys

exile = sys.argv[1]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = os.path.join(exile, "data")
if not os.path.isfile(os.path.join(data, "english", "UI.txt")):
    sys.exit(f"не похоже на папку Exile UI: {exile}")

dst = os.path.join(data, "ru"); os.makedirs(dst, exist_ok=True)
for f in os.listdir(os.path.join(root, "ru")):
    shutil.copy2(os.path.join(root, "ru", f), os.path.join(dst, f))
print("скопировано в data\\ru:", len(os.listdir(os.path.join(root, "ru"))), "файлов")

hints = {k: v for k, v in json.load(open(os.path.join(root, "tools", "hints_ru.json"), encoding="utf-8")).items() if not k.startswith("_")}
hdir = os.path.join(exile, "img", "GUI", "leveling tracker", "hints")
done, missing = 0, []
for ru, en in hints.items():
    s = os.path.join(hdir, en)
    if os.path.isfile(s):
        shutil.copy2(s, os.path.join(hdir, ru.replace(" ", "_") + ".jpg")); done += 1
    else:
        missing.append(en)
print("подсказок создано:", done, "| не найдено картинок:", missing or "нет")
