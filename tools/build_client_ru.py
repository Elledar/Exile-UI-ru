# Собирает ru/client.txt из английского шаблона Exile UI, заменяя только проверенные значения.
# Использование: python tools/build_client_ru.py <путь к data/english/client.txt> <выходной файл>
import re, sys

# (ключ, английское значение) -> русское значение. Только строки, подтверждённые журналом русского клиента PoE 1.
RU = {
    # в Fontin SmallCaps нет русских букв; Fontin Sans CR SC кладётся в data\ как alt_font_*.ttf (см. README)
    ("system_font", "Fontin SmallCaps"): "Fontin Sans CR SC",
    ("log_level", "is now level"): "достигает # уровня",
    ("log_whois", "is a level # in the"): "имеет уровень # в лиге",
    ("log_whois_class", "level # in the"): "уровень # в лиге",
    ("log_slain", "has been slain"): "был повержен",
    ("log_suicide", "has committed suicide"): "покончил с собой",
    ("log_delirium", "Strange Voice:"): "Странный голос:",
    ("log_blight", "Sister Cassia:"): "Сестра Кассия:",
    ("log_harvest", "Oshabi:"): "Ошаби:",
    ("log_incursion", "Alva, Master Explorer:"): "Альва, Мастер исследований:",
    ("log_bestiary", "Einhar, Beastmaster:"): "Эйнар, Мастер зверей:",
    ("log_delve", "Niko, Master of the Depths:"): "Нико, Мастер глубин:",
    ("log_betrayal", "Jun, Veiled Master:"): "Джун, Скрытый мастер:",
    ("log_betrayal", "Aisling Laffrey, The Silent Butcher:"): "Ашлинг Лаффрей, Безмолвный палач:",
    ("log_betrayal", "Cameria the Coldblooded:"): "Камериа Хладнокровный:",
    ("log_betrayal", "Elreon, Light's Judge:"): "Элреон, Судья Света:",
    ("log_betrayal", "Gravicius Reborn:"): "Гравиций Возрождённый:",
    ("log_betrayal", 'Guff "Tiny" Grenn:'): 'Гафф "Малыш" Гренн:',
    ("log_betrayal", "Haku, Warmaster:"): "Хаку, Мастер войны:",
    ("log_betrayal", "Hillock, the Blacksmith:"): "Хиллок, Кузнец:",
    ("log_betrayal", "It That Fled:"): "То-Что-Сбежало:",
    ("log_betrayal", "Janus Perandus:"): "Янус Перандус:",
    ("log_betrayal", "Thane Jorgin the Banished:"): "Тан Йоргин Изгнанный:",
    ("log_betrayal", "Korell Goya, Son of Stone:"): "Корелл Гойя, Сын камня:",
    ("log_betrayal", "Leo, Wolf of the Pits:"): "Лео, Волк бойцовских ям:",
    ("log_betrayal", "Riker Maloney, Midnight Tinkerer:"): "Райкер Мэлоуни, Полуночный изобретатель:",
    ("log_betrayal", "Rin Yuushu:"): "Рин Юушу:",
    ("log_betrayal", "Tora, the Culler:"): "Тора, Отстрельщик:",
    ("log_betrayal", "Vagan, Victory's Herald:"): "Ваган, Вестник победы:",
    ("log_betrayal", "Vorici, Silent Brother:"): "Воричи, Безмолвный брат:",
    ("log_ultimatum", "The Trialmaster:"): "Мастер испытаний:",
    ("log_maven", "The Maven:"): "Мейвен:",
    ("log_mist", "A Reflecting Mist has manifested nearby"): "Поблизости возник отражающий туман",
    ("log_expedition", "Dannig, Warrior Skald:"): "Дэнниг, воин и скальд:",
    ("log_expedition", "Gwennen, the Gambler:"): "Гвеннен, спекулянтка:",
    ("log_expedition", "Rog:"): "Рог:",
    ("log_expedition", "Tujen, the Haggler:"): "Туджин, торгаш:",
    # комнаты Лабиринта (сверены по парам "код зоны -> название" в журнале на обоих языках)
    ("lab_aspirant's trial", "aspirant's trial"): "испытание претендента",
    ("lab_basilica annex", "basilica annex"): "флигель храма",
    ("lab_basilica atrium", "basilica atrium"): "атриум храма",
    ("lab_basilica halls", "basilica halls"): "залы храма",
    ("lab_basilica passage", "basilica passage"): "коридоры храма",
    ("lab_domain crossing", "domain crossing"): "перекрёсток имения",
    ("lab_domain enclosure", "domain enclosure"): "территория имения",
    ("lab_domain path", "domain path"): "путь к имению",
    ("lab_domain walkways", "domain walkways"): "аллеи имения",
    ("lab_estate crossing", "estate crossing"): "перекрёсток усадьбы",
    ("lab_estate enclosure", "estate enclosure"): "территория усадьбы",
    ("lab_estate path", "estate path"): "путь к усадьбе",
    ("lab_estate walkways", "estate walkways"): "аллеи усадьбы",
    ("lab_mansion annex", "mansion annex"): "флигель особняка",
    ("lab_mansion atrium", "mansion atrium"): "атриум особняка",
    ("lab_mansion halls", "mansion halls"): "залы особняка",
    ("lab_mansion passage", "mansion passage"): "коридоры особняка",
    ("lab_sanitorium annex", "sanitorium annex"): "флигель лазарета",
    ("lab_sanitorium atrium", "sanitorium atrium"): "атриум лазарета",
    ("lab_sanitorium halls", "sanitorium halls"): "залы лазарета",
    ("lab_sanitorium passage", "sanitorium passage"): "коридоры лазарета",
    ("lab_sepulchre annex", "sepulchre annex"): "флигель усыпальницы",
    ("lab_sepulchre atrium", "sepulchre atrium"): "атриум усыпальницы",
    ("lab_sepulchre halls", "sepulchre halls"): "залы усыпальницы",
    ("lab_sepulchre passage", "sepulchre passage"): "коридоры усыпальницы",
}
# квесты/NPC для логики гайда — те же названия, что в гайде и gems.json (tools/quest_names_ru.json)
import json, os
_q = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "quest_names_ru.json"), encoding="utf-8"))["client_quest_keys"]
_en = {"quest_lilly": "lilly", "quest_tarkleigh": "tarkleigh", "quest_fixture": "a fixture of fate",
       "quest_mercy": "mercy mission", "quest_fallen": "fallen from grace", "quest_breaking": "breaking some eggs"}
for _k, _v in _q.items():
    if _v != _en[_k]:
        RU[(_k, _en[_k])] = _v

EXTRA_AFTER = {  # дополнительные строки после указанной (ключ, значение)
    ("log_expedition", "Rog:"): ['log_expedition\t\t\t=\t"Рог, распылитель:"\t\t;## ru: в русском клиенте Рог говорит под двумя именами'],
}
# ВАЖНО: для log_level/log_whois/log_slain нельзя добавлять вторые значения — программа требует,
# чтобы в строке журнала нашлись ВСЕ значения ключа сразу (Lang_Match). Вторые значения можно только
# для реплик NPC (log_expedition и т.п.), там значения проверяются по одному.
line_rx = re.compile(r'^(\s*)([^;=\s][^=]*?)(\s*=\s*)"(.*)"(.*)$')
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8-sig").read().splitlines()
out, used = [], set()
for line in text:
    m = line_rx.match(line)
    if m and not line.lstrip().startswith(";"):
        indent, key, eq, val, rest = m.groups()
        # значение может само содержать кавычки (Guff "Tiny" Grenn) — берём до последней кавычки
        full = line[len(indent) + len(key) + len(eq):]
        cut = full.find(";##"); body = full if cut < 0 else full[:cut]
        q = body.rfind('"'); val = full[1:q]; rest = full[q + 1:]
        k = (key.strip(), val)
        if k in RU:
            used.add(k)
            if RU[k] is not None:
                line = f'{indent}{key}{eq}"{RU[k]}"{rest}'
        out.append(line)
        for extra in EXTRA_AFTER.get(k, []):
            out.append(indent + extra); used.add(k)
    else:
        out.append(line)
missing = [k for k in RU if k not in used]
if missing:
    sys.exit("Не найдены в шаблоне (автор что-то поменял): %r" % missing)
header = [";## Русский языковой пакет для Exile UI (клиент игры на русском; общая папка для PoE 1 и PoE 2, проверено на PoE 1) — client.txt",
          ";## Собран скриптом tools/build_client_ru.py из английского шаблона. Непереведённые строки пока на английском.", ""]
open(dst, "w", encoding="utf-8-sig", newline="\r\n").write("\n".join(header + out) + "\n")
print("ok:", len(RU), "замен")
