# Сверка после обновления Exile UI: что автор поменял в английских файлах и что из-за этого надо сделать с переводом.
#
# Использование:
#   python tools/check_update.py "<папка Exile UI>"            — отчёт (ничего не меняет)
#   python tools/check_update.py "<папка Exile UI>" --accept   — принять новую версию как эталон (base/english)
#   python tools/check_update.py "<папка Exile UI>" --accept --force — принять, даже если есть «опасные» места
#
# Эталон — base/english: английские файлы той версии, по которой сделан перевод. Сборка (tools/build_all.py)
# берёт шаблоны оттуда, поэтому обновление программы ничего не ломает, пока эталон не принят.
# Порядок после обновления: сверка → доперевести/поправить таблицы в tools → --accept → build_all.py → установка.
#
# Отчёт также пишется в .tmp/update_report.txt. Код выхода: 0 — изменений нет, 1 — есть изменения.
import collections, difflib, glob, json, os, re, shutil, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "base", "english")
FILES = ["UI.txt", "client.txt", "[leveltracker] default guide.json", "[leveltracker] default guide 2.json",
         "help tooltips.json", "[leveltracker] areas.json", "[leveltracker] gems.json"]

args = [a for a in sys.argv[1:] if not a.startswith("--")]
flags = {a for a in sys.argv[1:] if a.startswith("--")}
if len(args) != 1:
    sys.exit('Использование: python tools/check_update.py "<папка Exile UI>" [--accept [--force]]')
NEW = os.path.join(args[0], "data", "english")
if not os.path.isdir(NEW):
    sys.exit(f"нет папки {NEW} — укажите корневую папку Exile UI (где лежит «Exile UI.ahk»)")

out, danger = [], []
def say(s=""): out.append(s)
def warn(s): danger.append(s); say("  ⚠ " + s)
def short(s, n=110): s = s.replace("\n", "⏎"); return s if len(s) <= n else s[:n] + "…"
def text(p): return open(p, encoding="utf-8-sig").read().replace("\r\n", "\n")
def js(p): return json.load(open(p, encoding="utf-8-sig"))
def load_tr(name): return {k: v for k, v in js(os.path.join(HERE, name)).items() if not k.startswith("_")}

# ---------- строки вида  ключ = "значение"  (UI.txt, client.txt) — разбор как в build_ui_ru.py ----------
line_rx = re.compile(r'^(\s*)([^;=\s][^=]*?)(\s*=\s*)(".*)$')
def entries(p):
    res = collections.defaultdict(list)
    for line in text(p).split("\n"):
        m = line_rx.match(line)
        if not m or line.lstrip().startswith(";"): continue
        full = m.group(4); cut = full.find(";##"); body = full if cut < 0 else full[:cut]
        res[m.group(2).strip()].append(full[1:body.rfind('"')])
    return res

# ---------- версия ----------
base_ver = js(os.path.join(ROOT, "base", "version.json")).get("release")
try: new_ver = js(os.path.join(args[0], "data", "versions.json"))["_release"][0]
except Exception: new_ver = "?"
say(f"Сверка Exile UI: эталон перевода — версия {base_ver}, в папке — версия {new_ver}")
say(f"Папка: {args[0]}")

changed_files = [f for f in FILES if not os.path.exists(os.path.join(NEW, f))
                 or text(os.path.join(NEW, f)) != text(os.path.join(BASE, f))]
missing = [f for f in FILES if not os.path.exists(os.path.join(NEW, f))]
for f in missing:
    warn(f"файла «{f}» больше нет в новой версии — нужно разбираться вручную")

# ---------- 1. интерфейс ----------
def check_ui():
    f = "UI.txt"
    if f not in changed_files or f in missing: return
    say(); say("== Интерфейс (UI.txt) ==")
    tr = load_tr("ui_ru.json")
    b, n = entries(os.path.join(BASE, f)), entries(os.path.join(NEW, f))
    prefixes = {k.rsplit("_", 1)[0] for k in tr}
    added = [k for k in n if k not in b]
    if added:
        say(f"  новые строки ({len(added)}), пока будут на английском:")
        for k in added:
            mark = " ★ раздел уже переведён" if k.rsplit("_", 1)[0] in prefixes else ""
            for v in n[k]: say(f"    + {k} = \"{short(v)}\"{mark}")
    for k in [k for k in b if k not in n]:
        if k in tr: say(f"  − удалён переведённый ключ {k} — убрать из tools/ui_ru.json (иначе сборка остановится)")
        else: say(f"  − удалён ключ {k} (не переведён, делать ничего не нужно)")
    for k in [k for k in n if k in b and n[k] != b[k]]:
        old, new, ru = b[k], n[k], tr.get(k)
        if len(old) != len(new):
            if ru:
                warn(f"{k}: значений было {len(old)}, стало {len(new)}. Переводы подставляются по порядку и СЪЕДУТ — "
                     f"переставить список в tools/ui_ru.json:")
                for i, v in enumerate(old): say(f"      было[{i}] \"{short(v, 60)}\" → \"{ru[i] if i < len(ru) else '—'}\"")
                for i, v in enumerate(new): say(f"      стало[{i}] \"{short(v, 60)}\"")
            else:
                say(f"  ~ {k}: значений было {len(old)}, стало {len(new)} (не переведён): {[short(v, 40) for v in new]}")
            continue
        for i, (x, y) in enumerate(zip(old, new)):
            if x == y: continue
            if ru and i < len(ru) and ru[i] is not None:
                say(f"  ~ {k}[{i}] изменился, перевод устарел — проверить:")
                say(f"      было \"{short(x)}\"  стало \"{short(y)}\"  перевод \"{short(ru[i])}\"")
            else:
                say(f"  ~ {k}[{i}] изменился (не переведён): \"{short(y)}\"")

# ---------- 2. журнал игры ----------
def check_client():
    f = "client.txt"
    if f not in changed_files or f in missing: return
    say(); say("== Журнал игры (client.txt) — по нему программа понимает, что происходит в игре ==")
    sys.path.insert(0, HERE)
    import build_client_ru
    ru = build_client_ru.RU
    b, n = entries(os.path.join(BASE, f)), entries(os.path.join(NEW, f))
    for k in dict.fromkeys(list(n) + list(b)):
        old, new = b.get(k, []), n.get(k, [])
        if old == new: continue
        gone = [v for v in old if v not in new]; came = [v for v in new if v not in old]
        for v in gone:
            if (k, v) in ru: warn(f"{k} = \"{short(v)}\" убрано/изменено, а перевод «{ru[(k, v)]}» к нему привязан — "
                                 f"поправить tools/build_client_ru.py (иначе сборка остановится)")
            else: say(f"  − {k} = \"{short(v)}\"")
        for v in came:
            say(f"  + {k} = \"{short(v)}\" — нужен русский текст из журнала русского клиента")
        if not gone and not came: say(f"  ~ {k}: поменялся порядок значений")

# ---------- 3. гайды ----------
def flat_guide(p):
    return [(a + 1, s + 1, line) for a, act in enumerate(js(p)) for s, step in enumerate(act) for line in step]

def check_guide():
    f = "[leveltracker] default guide.json"
    if f in changed_files and f not in missing:
        say(); say("== Гайд акт-трекера PoE 1 ==")
        tr = {}
        for p in sorted(glob.glob(os.path.join(HERE, "guide_poe1_ru*.json"))):
            tr.update({k: v for k, v in js(p).items() if not k.startswith("_")})
        b, n = flat_guide(os.path.join(BASE, f)), flat_guide(os.path.join(NEW, f))
        sm = difflib.SequenceMatcher(None, [x[2] for x in b], [x[2] for x in n], autojunk=False)
        def where(x): return f"акт {x[0]}, шаг {x[1]}"
        def added(x):
            say(f"  + {where(x)}: \"{short(x[2])}\"" + (" (перевод уже есть)" if x[2] in tr else " — перевести"))
        def removed(x):
            say(f"  − {where(x)}: \"{short(x[2])}\"" + (" (перевод больше не нужен)" if x[2] in tr else ""))
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal": continue
            olds, news = b[i1:i2], n[j1:j2]
            if op == "replace":
                for x, y in zip(olds, news):
                    say(f"  ~ {where(y)}:")
                    say(f"      было  \"{short(x[2])}\"")
                    say(f"      стало \"{short(y[2])}\"")
                    if y[2] in tr: say(f"      (перевод для новой строки уже есть)")
                    elif x[2] in tr: say(f"      старый перевод: \"{short(tr[x[2]])}\" — поправить")
                    else: say(f"      (не была переведена)")
                olds, news = olds[len(news):], news[len(olds):]
            for x in olds: removed(x)
            for y in news: added(y)
        say("  Строки без перевода показываются в игре по-английски; ничего не ломается.")
    f = "[leveltracker] default guide 2.json"
    if f in changed_files and f not in missing:
        say(); say("== Гайд PoE 2 ==")
        say("  изменился; перевода пока нет — копия обновится сама при сборке (build_all.py)")

# ---------- 4. всплывающие подсказки ----------
def check_help():
    f = "help tooltips.json"
    if f not in changed_files or f in missing: return
    say(); say("== Всплывающие подсказки (help tooltips.json) ==")
    tr = load_tr("help_tooltips_ru.json")
    b, n = js(os.path.join(BASE, f)), js(os.path.join(NEW, f))
    for sec in dict.fromkeys(list(n) + list(b)):
        bs, ns, ts = b.get(sec, {}), n.get(sec, {}), tr.get(sec, {})
        for key in dict.fromkeys(list(ns) + list(bs)):
            if bs.get(key) == ns.get(key): continue
            label = f"{sec} / {key}"
            if key not in bs:
                say(f"  + {label}: \"{short(json.dumps(ns[key], ensure_ascii=False))}\"" +
                    (" ★ раздел уже переведён" if ts else ""))
            elif key not in ns:
                say(f"  − {label}" + (" — убрать из tools/help_tooltips_ru.json (иначе сборка остановится)" if key in ts else ""))
            elif key in ts:
                say(f"  ~ {label} изменилась, перевод устарел:")
                say(f"      было  {short(json.dumps(bs[key], ensure_ascii=False), 200)}")
                say(f"      стало {short(json.dumps(ns[key], ensure_ascii=False), 200)}")
            else:
                say(f"  ~ {label} изменилась (не переведена)")

# ---------- 5. локации и камни ----------
def check_names():
    fa, fg = "[leveltracker] areas.json", "[leveltracker] gems.json"
    if fa in changed_files and fa not in missing:
        say(); say("== Локации акт-трекера ==")
        b = {o["id"]: o.get("name") for act in js(os.path.join(BASE, fa)) for o in act}
        n = {o["id"]: o.get("name") for act in js(os.path.join(NEW, fa)) for o in act}
        for i in n.keys() - b.keys(): say(f"  + {i} ({n[i]})")
        for i in b.keys() - n.keys(): say(f"  − {i} ({b[i]})")
        if n.keys() == b.keys(): say("  изменились данные локаций (уровни/порядок)")
        say("  → пересобрать названия: build_all.py (нужны свежие файлы RePoE в .tmp/repoe)")
    if fg in changed_files and fg not in missing:
        say(); say("== Камни и квесты (gems.json) ==")
        b, n = js(os.path.join(BASE, fg)), js(os.path.join(NEW, fg))
        bk = {k for k in b if not k.startswith("_")}; nk = {k for k in n if not k.startswith("_")}
        if nk - bk: say(f"  + новые камни ({len(nk - bk)}): {', '.join(sorted(nk - bk))}")
        if bk - nk: say(f"  − убранные камни ({len(bk - nk)}): {', '.join(sorted(bk - nk))}")
        bq, nq = set(b.get("_quests", {})), set(n.get("_quests", {}))
        if nq - bq: warn(f"новые квесты {sorted(nq - bq)} — добавить в tools/quest_names_ru.json (иначе сборка остановится)")
        if bq - nq: say(f"  − убранные квесты: {sorted(bq - nq)}")
        say("  → пересобрать названия: build_all.py (нужны свежие файлы RePoE в .tmp/repoe)")

# ---------- 6. новые файлы ----------
def check_files():
    known = set(open(os.path.join(ROOT, "base", "english_files.txt"), encoding="utf-8").read().split("\n")) - {""}
    now = set(os.listdir(NEW))
    if now - known:
        say(); say("== Новые файлы в data/english ==")
        for f in sorted(now - known): say(f"  + {f} — посмотреть, нужен ли ему перевод")
    if known - now:
        say(); say("== Пропавшие файлы в data/english ==")
        for f in sorted(known - now): say(f"  − {f}")
    return now != known

check_ui(); check_client(); check_guide(); check_help(); check_names()
files_changed = check_files()
any_change = bool(changed_files or files_changed)

say()
if not any_change:
    say("ИТОГ: изменений нет — перевод соответствует этой версии, делать ничего не нужно.")
else:
    say(f"ИТОГ: изменились файлы: {', '.join(changed_files) or 'только список файлов'}.")
    say(f"Опасных мест (перевод съедет или сборка остановится): {len(danger)}.")
    say("Дальше: поправить таблицы в tools → check_update.py --accept → build_all.py → установка.")

if "--accept" in flags:
    say()
    if danger and "--force" not in flags:
        say("ЭТАЛОН НЕ ОБНОВЛЁН: есть опасные места (⚠). Сначала поправьте таблицы, затем запустите с --accept --force.")
    elif missing:
        say("ЭТАЛОН НЕ ОБНОВЛЁН: в новой версии нет части файлов.")
    else:
        for f in FILES: shutil.copy2(os.path.join(NEW, f), os.path.join(BASE, f))
        open(os.path.join(ROOT, "base", "english_files.txt"), "w", encoding="utf-8").write("\n".join(sorted(os.listdir(NEW))) + "\n")
        v = js(os.path.join(ROOT, "base", "version.json")); v["release"] = new_ver; v["commit"] = "из папки " + args[0]
        json.dump(v, open(os.path.join(ROOT, "base", "version.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        say(f"ЭТАЛОН ОБНОВЛЁН до версии {new_ver}. Теперь: python tools/build_all.py, затем установка.")

report = "\n".join(out)
print(report)
os.makedirs(os.path.join(ROOT, ".tmp"), exist_ok=True)
open(os.path.join(ROOT, ".tmp", "update_report.txt"), "w", encoding="utf-8").write(report + "\n")
sys.exit(1 if any_change else 0)
