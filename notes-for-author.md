# Заметки автору Exile UI

**Что это.** Три места в коде Exile UI, которые мешают русскому переводу: обойти их одними файлами перевода
нельзя, нужна правка в программе. Ниже текст на английском, готовый для обсуждения
[№326](https://github.com/Lailloken/Exile-UI/discussions/326) или отдельного issue. Отправлять или нет — решаете вы.
Номера строк — по версии 16501 (коммит 67d1a36).

Кратко по-русски:
1. **Лилия.** В одной проверке гайда имя «lilly» написано прямо в коде, а не берётся из перевода. Из-за этого мы
   оставили в русском гайде «lilly:» латиницей. Если автор поправит, можно будет написать «Лилия».
2. **Камни поддержки.** При клике по камню поддержки в окне связок программа копирует строку поиска для тайника
   и дописывает в конец английское слово «support». В русском клиенте камни называются «Поддержка: Урон огнём»
   (слово спереди), поэтому поиск ничего не находит.
3. **Гайд без запасного варианта.** Для языка RU программа ищет гайд только в папке `ru` и не берёт английский,
   если там его нет. Поэтому в пакете лежит английская копия гайда PoE 2, которую надо обновлять при каждой
   версии. Интерфейс и подсказки запасной английский вариант уже имеют.

---

## Text for the author (English)

Hi! I'm maintaining a Russian language pack for Exile UI (client.txt, UI.txt, area/gem names, the PoE 1 leveling
guide and help tooltips), distributed as a plain `data\ru` folder as you suggested in #326. Everything works through
the language files except three small spots in the code. Line numbers refer to commit 67d1a36.

**1. Hard-coded "lilly" in the guide gem check** — `modules/leveling tracker.ahk`, line 1619:

```ahk
!RegExMatch(line, "i)lilly.*" StrReplace(lilly_regex, " ", "."))
```

Everywhere else the code uses `Lang_Trans("quest_lilly")`, but here the literal `lilly` is used. With a translated
`quest_lilly` this check never matches, so translated guides have to keep the Latin "lilly:" in their lines.
Suggested fix: `"i)" Lang_Trans("quest_lilly") ".*"`.

**2. English ".support" suffix in the gem-link search string** — same file, line 2345:

```ahk
Clipboard := "^" StrReplace(regex, " ", ".") . (!vars.poe_version && InStr(A_GuiControl, "|") ? ".support" : "") "$"
```

In the Russian client, support gems are named with a prefix, e.g. *Added Fire Damage Support* →
*Поддержка: Урон огнём*. The generated string `^урон.огнём.support$` therefore matches nothing in the stash.
Could the pattern come from the language file? For example a UI.txt key like
`lvltracker_support_regex = "^#.support$"` (English) / `"^поддержка:.#$"` (Russian), with `#` replaced by the gem
name.

**3. No English fallback for the default leveling guide** — the guide is loaded only from
`data\<language>\[leveltracker] default guide*.json` (e.g. line 875). UI.txt and help tooltips already fall back to
English, but the guide doesn't, so a language pack must ship an untranslated copy of the PoE 2 guide and re-sync it
with every update. A fallback to `data\english\` when the file is missing would remove that.

Thanks for making the tool translation-friendly in the first place — the rest of the pack needed no code changes.
