# Собирает весь русский пакет ru/ из эталона base/english (английские файлы, по которым сделан перевод).
# Использование:
#   python tools/build_all.py                      — собрать ru/
#   python tools/build_all.py "<папка Exile UI>"   — собрать и сразу установить
# Названия локаций и камней пересобираются, только если есть файлы RePoE в .tmp/repoe (см. build_names_ru.py);
# иначе остаются прежние ru/[leveltracker] areas.json и gems.json.
import os, shutil, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
E = os.path.join(ROOT, "base", "english")
RU = os.path.join(ROOT, "ru")
REPOE = os.path.join(ROOT, ".tmp", "repoe")

def run(script, *a):
    print(f"--- {script}", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, script), *a], env={**os.environ, "PYTHONUTF8": "1"})
    if r.returncode:
        sys.exit(f"СБОРКА ОСТАНОВЛЕНА на {script} — пакет не установлен")

run("build_client_ru.py", os.path.join(E, "client.txt"), os.path.join(RU, "client.txt"))
run("build_ui_ru.py", os.path.join(E, "UI.txt"), os.path.join(RU, "UI.txt"))
run("build_guide_ru.py", E, RU)
run("build_help_ru.py", os.path.join(E, "help tooltips.json"), RU)
if all(os.path.exists(os.path.join(REPOE, f)) for f in ("en_world_areas.json", "ru_world_areas.json", "en_gems.json", "ru_gems.json")):
    run("build_names_ru.py", E, REPOE, RU)
else:
    print("--- названия локаций и камней: нет файлов RePoE в .tmp/repoe, оставлены прежние")
# гайд PoE 2 пока не переведён: английская копия (без неё программа при языке RU не найдёт гайд)
shutil.copy2(os.path.join(E, "[leveltracker] default guide 2.json"), os.path.join(RU, "[leveltracker] default guide 2.json"))
run("check_lang_file.py", os.path.join(RU, "UI.txt"), os.path.join(E, "UI.txt"))
run("check_lang_file.py", os.path.join(RU, "client.txt"), os.path.join(E, "client.txt"))
if len(sys.argv) > 1:
    run("install_ru.py", sys.argv[1])
print("ГОТОВО")
