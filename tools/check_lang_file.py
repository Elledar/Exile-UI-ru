# Проверяет файл перевода по тем же правилам, по которым его читает Exile UI (Lang_Load):
# у каждой не-комментарной строки должен быть знак "=" и чётное число кавычек.
# Использование: python tools/check_lang_file.py <файл> [<английский шаблон для сверки ключей>]
import sys, collections
def load(p):
    keys, errors = collections.Counter(), []
    for i, raw in enumerate(open(p, encoding="utf-8-sig").read().split("\n"), 1):
        line = raw.replace("\t", "").strip("\r").strip()
        if not line or line.startswith(";"): continue
        if "=" not in line or line.count('"') % 2:
            errors.append(f"строка {i}: нет '=' или нечётное число кавычек: {line[:80]}")
            continue
        keys[line.split("=", 1)[0].strip()] += 1
    return keys, errors
keys, errors = load(sys.argv[1])
for e in errors: print("ОШИБКА", e)
if len(sys.argv) > 2:
    ref, _ = load(sys.argv[2])
    for k in ref:
        if keys[k] < ref[k]: print(f"НЕ ХВАТАЕТ: {k} ({keys[k]} из {ref[k]})")
    for k in keys:
        if k not in ref: print(f"ЛИШНИЙ КЛЮЧ: {k}")
print("строк-значений:", sum(keys.values()), "| ошибок:", len(errors))
