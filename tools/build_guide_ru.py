# Собирает русский гайд акт-трекера PoE 1: ru/[leveltracker] default guide.json
# Использование: python tools/build_guide_ru.py <data/english Exile UI> <выходная папка ru>
#
# 1) строки из tools/guide_poe1_ru.json заменяются переводом;
# 2) в непереведённых строках переименовываются квесты, NPC и служебные слова (kill, buy_gems),
#    чтобы связи с gems.json/client.txt/UI.txt не рвались;
# 3) каждая переведённая строка проверяется: служебные метки, иконки, коды локаций, цвета,
#    уровни и разделители должны совпадать с английской строкой.
import json, os, re, sys, collections

src, out = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
load = lambda p: json.load(open(p, encoding="utf-8-sig"))
import glob
tr = {}
for f in sorted(glob.glob(os.path.join(here, "guide_poe1_ru*.json"))):  # акты 1–3 и 4–10
    for k, v in load(f).items():
        if k.startswith("_"): continue
        if k in tr and tr[k] != v:
            sys.exit(f"строка переведена по-разному в разных файлах: {k}")
        tr[k] = v
        bad = re.findall(r"\((?:quest|img|color|hint)[^)]*\s[^)]*\)", v)
        if bad:  # программа не распознаёт метку с пробелом и показывает её как текст
            sys.exit(f"пробел внутри метки (нужен _): {bad} в строке: {v}")
names =load(os.path.join(here, "quest_names_ru.json"))
qmap = {k.replace(" ", "_"): v.replace(" ", "_") for k, v in names["quests"].items()}
npcs = names["npcs"]
guide = load(os.path.join(src, "[leveltracker] default guide.json"))

def tokens(line):
    """то, что программа читает как разметку и что обязано сохраниться при переводе"""
    t = collections.Counter()
    t.update(re.findall(r"\(img:[^)]*\)", line))
    t.update(re.findall(r"areaid\S+", line))
    t.update(re.findall(r"\(lvl:[^)]*\)", line))
    # цвет 569777 добавляется в переводе вручную: программа сама красит только английские "trial" и "_lab"
    t.update(c for c in re.findall(r"\(color:[^)]*\)", line) if c != "(color:569777)")
    t.update(re.findall(r"\(hint\)_+", line))
    t.update(m for m in ("leaguestart:", "optional:", "twinkrun:", "quest-check:", "||", ";;") for _ in range(line.count(m)))
    # "lilly" — служебная метка только перед квестом ("lilly: <") или после "||"; в остальных строках это имя
    t["lilly-метка"] = len(re.findall(r"\|\| lilly:|lilly: <", line))
    t["<quest>"] = line.count("<"); t["(quest:"] = line.count("(quest:"); t["arena:"] = len(re.findall(r"arena:(?=\S)", line))  # "arena: " с пробелом — обычное слово
    return t

def rename(line):
    """для непереведённых строк: квесты, NPC и служебные слова — как в русских данных"""
    line = re.sub(r"<([^>]+)>", lambda m: "<" + qmap.get(m.group(1), m.group(1)) + ">", line)
    for en, ru in npcs.items():
        line = re.sub(r"\b%s(?=:)" % re.escape(en), ru, line)
    line = re.sub(r"\bkill\b", "убить", line)            # lvltracker_format_kill = "убить"
    line = line.replace("buy_gems", "купить_камни")      # lvltracker_gembuy = "купить камни"
    return line

errors, used, stats = [], set(), collections.Counter()
def convert(line):
    if line in tr:
        ru = tr[line]; used.add(line); stats["переведено"] += 1
        a, b = tokens(line), tokens(ru)
        if a != b:
            errors.append(f"метки не совпали:\n  en: {line}\n  ru: {ru}\n  разница: {dict((a - b) + (b - a))}")
        for q in re.findall(r"<([^>]+)>", line):        # квест в английской строке -> обязан стать русским квестом
            if q in qmap and "<%s>" % qmap[q] not in ru:
                errors.append(f"квест {q} не переименован в {qmap[q]}: {ru}")
        return ru
    stats["оставлено (переименованы квесты/NPC)"] += 1
    return rename(line)

def walk(x):
    if isinstance(x, str): return convert(x)
    if isinstance(x, list): return [walk(y) for y in x]
    if isinstance(x, dict): return {**x, "lines": walk(x["lines"])}
    return x

ru_guide = walk(guide)
# каждая фраза-подсказка должна встречаться в гайде, иначе картинка не покажется
hints = [k for k in load(os.path.join(here, "hints_ru.json")) if not k.startswith("_")]
text = json.dumps(ru_guide, ensure_ascii=False)
for h in hints:
    if h not in text:
        errors.append(f"фраза-подсказка не найдена в гайде: {h}")
unused = [k for k in tr if k not in used]
if unused: errors.append("строки перевода, которых нет в английском гайде (автор изменил гайд?):\n  " + "\n  ".join(unused))
if errors:
    sys.exit("ОШИБКИ:\n" + "\n".join(errors))
json.dump(ru_guide, open(os.path.join(out, "[leveltracker] default guide.json"), "w", encoding="utf-8", newline="\r\n"), ensure_ascii=False, indent=2)
print(", ".join(f"{k}: {v}" for k, v in stats.items()))
