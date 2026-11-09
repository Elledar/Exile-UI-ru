# Собирает русские названия локаций и камней для акт-трекера Exile UI (PoE 1).
# Источник русских названий — выгрузка данных самой игры (RePoE: repoe-fork.github.io, папка Russian),
# сопоставление идёт по внутренним кодам игры, а не по переводу на глаз.
#
# Использование:
#   python tools/build_names_ru.py <папка data/english Exile UI> <папка с RePoE-файлами> <выходная папка ru>
# В папке RePoE нужны: en_world_areas.json, ru_world_areas.json, en_gems.json, ru_gems.json
# (скачиваются с https://repoe-fork.github.io/<файл>.min.json и .../Russian/<файл>.min.json).
import json, os, re, sys

src, repoe, out = sys.argv[1:4]
load = lambda p: json.load(open(p, encoding="utf-8-sig"))
report = []

# русский клиент хранит склонения: "<if:gen>{Сумрачного взморья}<else>{Сумрачное взморье}" -> именительный падеж
def clean(name):
    m = re.search(r"<else>\{([^}]*)\}", name)
    name = m.group(1) if m else name
    name = re.sub(r"<[^>]*>|[{}]", "", name).strip()
    return re.sub(r" — уровень (\d+)$", r" (\1)", name)  # как у автора: "Chamber of Sins (1)"

# ---------- локации ----------
en_areas, ru_areas = load(os.path.join(repoe, "en_world_areas.json")), load(os.path.join(repoe, "ru_world_areas.json"))
by_en_name = {}
for aid, a in en_areas.items():
    by_en_name.setdefault(a.get("name", "").lower(), aid)

def ru_area(aid):
    a = ru_areas.get(aid)
    return clean(a["name"]) if a and a.get("name") else None

areas = load(os.path.join(src, "[leveltracker] areas.json"))
done = miss = 0
for act in areas:
    for o in act:
        name = ru_area(o["id"])
        if name:
            o["name"] = name; done += 1
        else:
            miss += 1; report.append(f"локация без русского названия: {o['id']} ({o['name']})")
        if "map_name" in o:
            # подпись на карте мира: ищем зону с таким английским названием (с "The"/" Level 1" и без)
            n = o["map_name"].lower()
            aid = next((by_en_name[c] for c in (n, "the " + n, n + " level 1", "the " + n + " level 1") if c in by_en_name), None)
            ru = ru_area(aid) if aid else None
            if not ru and name:  # подписи карты нет в данных игры — берём название самой зоны без номера уровня
                ru = re.sub(r" \(\d+\)$", "", name)
                report.append(f"map_name взят из названия зоны: {o['id']} ({o['map_name']} -> {ru})")
            if ru:
                o["map_name"] = re.sub(r" \(\d+\)$", "", ru)
json.dump(areas, open(os.path.join(out, "[leveltracker] areas.json"), "w", encoding="utf-8", newline="\r\n"), ensure_ascii=False, indent=2)
report.insert(0, f"локации: переведено {done}, без перевода {miss}")

# ---------- камни ----------
en_gems, ru_gems = load(os.path.join(repoe, "en_gems.json")), load(os.path.join(repoe, "ru_gems.json"))
def disp(g):
    b = g.get("base_item") or {}
    return b.get("display_name")
gem_by_en = {}
for gid, g in en_gems.items():
    n = disp(g)
    if n and gid in ru_gems and disp(ru_gems[gid]):
        gem_by_en.setdefault(n.lower(), disp(ru_gems[gid]))

# камни, которые в Exile UI записаны под старыми именами или не являются камнями
MANUAL_IDS = {"dark pact": "DarkPact"}                      # в игре переименован в Dark Bargain
en_base, ru_base = load(os.path.join(repoe, "en_base_items.json")), load(os.path.join(repoe, "ru_base_items.json"))
for bid, b in en_base.items():                              # флаконы и прочие предметы из гайда
    if b.get("name") and bid in ru_base and ru_base[bid].get("name"):
        gem_by_en.setdefault(b["name"].lower(), ru_base[bid]["name"])
for key, gid in MANUAL_IDS.items():
    gem_by_en[key] = disp(ru_gems[gid])

gems = load(os.path.join(src, "[leveltracker] gems.json"))
done = 0
for key, val in gems.items():
    if key.startswith("_") or not isinstance(val, dict):
        continue
    ru = gem_by_en.get(key.lower())
    if ru:
        ru = ru.lower()                     # Exile UI хранит названия камней строчными
        if key.endswith(" support"):       # автор убирает слово "support" (поддержки и так помечены "|")
            ru = re.sub(r"^поддержка:\s*", "", ru)
        val["name"] = ru; done += 1
    else:
        report.append(f"камень без русского названия: {key}")

# ---------- квесты: те же русские названия, что в гайде и client.txt (tools/quest_names_ru.json) ----------
names = load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "quest_names_ru.json"))
qmap, npcs = names["quests"], names["npcs"]
missing = [q for q in gems["_quests"] if q not in qmap]
if missing:
    sys.exit(f"квесты без перевода в quest_names_ru.json (автор добавил новые?): {missing}")
gems["_quests"] = {qmap[q]: {**v, "npc": npcs.get(v.get("npc", ""), v.get("npc", ""))} for q, v in gems["_quests"].items()}
for key, val in gems.items():
    if not key.startswith("_") and isinstance(val, dict) and isinstance(val.get("quests"), dict):
        val["quests"] = {qmap.get(q, q): v for q, v in val["quests"].items()}
report.insert(2, f"квесты: переименовано {len(qmap)}")
json.dump(gems, open(os.path.join(out, "[leveltracker] gems.json"), "w", encoding="utf-8", newline="\r\n"), ensure_ascii=False, indent=2)
report.insert(1, f"камни: переведено {done} из {sum(1 for k, v in gems.items() if not k.startswith('_') and isinstance(v, dict))}")

open(os.path.join(out, "..", ".tmp", "names_report.txt"), "w", encoding="utf-8").write("\n".join(report) + "\n")
print("\n".join(report[:3]))
