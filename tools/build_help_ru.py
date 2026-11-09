# Собирает ru/help tooltips.json (всплывающие подсказки) из tools/help_tooltips_ru.json.
# Использование: python tools/build_help_ru.py <data/english/help tooltips.json> <выходная папка ru>
# В файл попадает весь английский шаблон, переведённые подсказки заменяются русскими.
# Проверка: та же вложенность списков, то же число строк и та же разметка, что у английских подсказок.
import json, os, re, sys, collections

en = json.load(open(sys.argv[1], encoding="utf-8-sig"))
here = os.path.dirname(os.path.abspath(__file__))
ru = {k: v for k, v in json.load(open(os.path.join(here, "help_tooltips_ru.json"), encoding="utf-8")).items() if not k.startswith("_")}

GUIDE_STYLE = False  # подсказки с (hint) программа рисует как гайд: там "optional:" — служебная метка
def marks(s):
    pat = r"\(/highlight\)|\(hint\)_+|\((?:img|color):[^)]*\)|\(quest:|\n" + (r"|optional:" if GUIDE_STYLE else "")
    c = collections.Counter(re.findall(pat, s))
    c["<>"] = s.count("<")
    return c

errors = []
def compare(a, b, path):
    if isinstance(a, list) != isinstance(b, list):
        errors.append(f"{path}: разная вложенность"); return
    if isinstance(a, list):
        if len(a) != len(b):
            errors.append(f"{path}: в английском {len(a)} элементов, в переводе {len(b)}"); return
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, f"{path}[{i}]")
    elif marks(a) != marks(b):
        errors.append(f"{path}: разметка не совпала\n  en: {a!r}\n  ru: {b!r}")

for sec, items in ru.items():
    for key, val in items.items():
        if key not in en.get(sec, {}):
            errors.append(f"{sec}/{key}: нет в английском файле (автор переименовал?)"); continue
        GUIDE_STYLE = "(hint)" in json.dumps(en[sec][key])
        compare(en[sec][key], val, f"{sec}/{key}")
if errors:
    sys.exit("ОШИБКИ:\n" + "\n".join(errors))
# полный файл: английский шаблон + русские переводы поверх (часть кода не умеет брать английский запасной вариант,
# например пояснения к проверкам экрана, поэтому все разделы должны быть на месте)
full = json.loads(json.dumps(en))
for sec, items in ru.items():
    full[sec].update(items)
json.dump(full, open(os.path.join(sys.argv[2], "help tooltips.json"), "w", encoding="utf-8", newline="\r\n"), ensure_ascii=False, indent=2)
print("подсказок:", sum(len(v) for v in ru.values()))
