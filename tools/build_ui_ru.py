# Собирает ru/UI.txt из английского шаблона Exile UI по таблице tools/ui_ru.json.
# Использование: python tools/build_ui_ru.py <data/english/UI.txt> <ru/UI.txt>
# Значения подставляются по порядку для повторяющихся ключей; проверяется число '#', ';' и кавычек.
import json, os, re, sys, collections

src, dst = sys.argv[1], sys.argv[2]
tr = {k: v for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_ru.json"), encoding="utf-8")).items() if not k.startswith("_")}
FORBIDDEN = {"lvltracker_format_optional", "lvltracker_format_league", "lvltracker_format_twink", "global_colon"}
bad = FORBIDDEN & set(tr)
if bad:
    sys.exit(f"эти ключи переводить нельзя (служебные метки): {bad}")

line_rx = re.compile(r'^(\s*)([^;=\s][^=]*?)(\s*=\s*)(".*)$')
seen, out, errors, done = collections.Counter(), [], [], 0
for line in open(src, encoding="utf-8-sig").read().splitlines():
    m = line_rx.match(line)
    if not m or line.lstrip().startswith(";"):
        out.append(line); continue
    indent, key, eq, full = m.groups(); k = key.strip()
    cut = full.find(";##"); body = full if cut < 0 else full[:cut]
    q = body.rfind('"'); val, rest = full[1:q], full[q + 1:]
    i = seen[k]; seen[k] += 1
    vals = tr.get(k)
    if vals is not None and i < len(vals) and vals[i] is not None:
        ru = vals[i]
        for ch in ("#", ";"):
            if val.count(ch) != ru.count(ch):
                errors.append(f"{k}[{i}]: число '{ch}' не совпадает: '{val}' -> '{ru}'")
        if ru.count('"') % 2:
            errors.append(f"{k}[{i}]: нечётное число кавычек: {ru}")
        line = f'{indent}{key}{eq}"{ru}"{rest}'; done += 1
    out.append(line)
for k, vals in tr.items():
    if seen[k] == 0:
        errors.append(f"ключа {k} нет в шаблоне (автор переименовал?)")
    elif len(vals) > seen[k]:
        errors.append(f"{k}: в переводе {len(vals)} значений, в шаблоне {seen[k]}")
if errors:
    sys.exit("ОШИБКИ:\n" + "\n".join(errors))
header = [";## Русский перевод интерфейса Exile UI. Собран tools/build_ui_ru.py из английского шаблона по tools/ui_ru.json.",
          ";## Шрифт: Fontin Sans CR SC (файл data\\alt_font_FontinSansCR-SC.ttf, см. README). Непереведённые строки — на английском.", ""]
# без BOM, как английский шаблон
open(dst, "w", encoding="utf-8", newline="\r\n").write("\n".join(header + out) + "\n")
print("переведено значений:", done)
