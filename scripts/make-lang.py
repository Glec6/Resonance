#!/usr/bin/env python3
"""DeCast-S4 translations: Flycast's menus (resources/i18n/flycast.pot) plus the home screen's
texts (lang/decast-keys.txt), in the 12 languages DolphinPS4 and Crema have, plus Arabic.

lang/keys.txt numbers every English text (written by `make-lang.py keys`). lang/src/<code>.txt has
"<number><TAB><translation>" lines; a plural is "<form 0> || <form 1> || ...". Texts keep the .po
escapes (\\n, \\"). Flycast's own translations win where it has them (French, Japanese, Brazilian
Portuguese in full, part of Turkish and Spanish); the src files fill the rest.

  make-lang.py keys     write lang/keys.txt from the Flycast tree's flycast.pot
  make-lang.py          write <flycast>/resources/i18n/<po>.po for every language, and the fonts
                        (launcher-assets/launcher/fonts: Noto Sans JP/KR/SC cut to the characters
                        the texts use, Noto Sans Arabic with its presentation forms)
Needs fontTools for the fonts (~/dolphinps4-build/tools/fontenv) and the Noto sources in
~/dolphinps4-build/tools/noto.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..")
LANG = os.path.join(REPO, "lang")
FONTS = os.path.join(REPO, "launcher-assets", "launcher", "fonts")
FLYCAST = os.path.expanduser("~/decast-build/src/flycast")
I18N = os.path.join(FLYCAST, "resources", "i18n")
NOTO = os.path.expanduser("~/dolphinps4-build/tools/noto")

# our code -> (.po name, Language header, Plural-Forms)
LANGUAGES = {
    "de": ("de", "de_DE", "nplurals=2; plural=(n != 1);"),
    "es": ("es", "es_ES", "nplurals=2; plural=(n != 1);"),
    "fr": ("fr", "fr_FR", "nplurals=2; plural=(n > 1);"),
    "it": ("it", "it_IT", "nplurals=2; plural=(n != 1);"),
    "ja": ("ja", "ja_JP", "nplurals=1; plural=0;"),
    "ko": ("ko", "ko_KR", "nplurals=1; plural=0;"),
    "nl": ("nl", "nl_NL", "nplurals=2; plural=(n != 1);"),
    "pl": ("pl", "pl_PL", "nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"),
    "pt": ("pt_BR", "pt_BR", "nplurals=2; plural=(n > 1);"),
    "ru": ("ru", "ru_RU", "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"),
    "tr": ("tr", "tr_TR", "nplurals=2; plural=(n != 1);"),
    "zh": ("zh_CN", "zh_CN", "nplurals=1; plural=0;"),
    "ar": ("ar", "ar", "nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5"),
}
NPLURALS = {code: int(re.search(r"nplurals=(\d)", pf).group(1)) for code, (_, _, pf) in LANGUAGES.items()}
# Settings shows every language in its own script
LANGUAGE_NAMES = "English Español Français Deutsch Italiano Português Nederlands Polski Türkçe Русский 日本語 中文 (简体) 한국어 العربية"
CJK = {"ja": "JP", "zh": "SC", "ko": "KR"}


def parse_po(path):
    """[{ctx, id, plural, str: [..]}] without the header, in file order."""
    entries, cur, field = [], None, None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n").rstrip("\r")
        m = re.match(r'^(msgctxt|msgid|msgid_plural|msgstr(?:\[\d\])?) "(.*)"$', line)
        if m:
            key, value = m.groups()
            if key in ("msgctxt", "msgid") and (cur is None or cur["done"]):
                cur = {"ctx": None, "id": None, "plural": None, "str": {}, "done": False}
                entries.append(cur)
            field = key
            if key == "msgctxt":
                cur["ctx"] = value
            elif key == "msgid":
                cur["id"] = value
            elif key == "msgid_plural":
                cur["plural"] = value
            else:
                n = int(key[7:-1]) if "[" in key else 0
                cur["str"][n] = value
                cur["done"] = True
            continue
        m = re.match(r'^"(.*)"$', line)
        if m and cur is not None and field:
            v = m.group(1)
            if field == "msgctxt":
                cur["ctx"] += v
            elif field == "msgid":
                cur["id"] += v
            elif field == "msgid_plural":
                cur["plural"] += v
            else:
                n = int(field[7:-1]) if "[" in field else 0
                cur["str"][n] += v
        elif not line.strip():
            field = None
    return [e for e in entries if e["id"]]


def key_of(e):
    return (e["ctx"] or "") + "\x04" + e["id"]


def read_keys():
    """[(number, ctx, msgid, msgid_plural)] from lang/keys.txt"""
    keys = []
    for line in open(os.path.join(LANG, "keys.txt"), encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        num, text = line.split("\t", 1)
        ctx = None
        m = re.match(r"^\[(\w+)\] (.*)$", text)
        if m:
            ctx, text = m.groups()
        plural = None
        if " || " in text:
            text, plural = text.split(" || ", 1)
        keys.append((int(num), ctx, text, plural))
    return keys


def write_keys():
    pot = parse_po(os.path.join(I18N, "flycast.pot"))
    seen = set()
    lines = ["# English texts: Flycast's flycast.pot, then the home screen's (lang/decast-keys.txt).",
             "# <number><TAB>[context] text || plural. Written by scripts/make-lang.py keys."]
    n = 0
    for e in pot:
        n += 1
        seen.add(key_of(e))
        ctx = f"[{e['ctx']}] " if e["ctx"] else ""
        lines.append(f"{n}\t{ctx}{e['id']}" + (f" || {e['plural']}" if e["plural"] else ""))
    n = 2000
    for line in open(os.path.join(LANG, "decast-keys.txt"), encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        if "\x04" + line in seen:
            continue
        n += 1
        lines.append(f"{n}\t{line}")
    open(os.path.join(LANG, "keys.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"keys.txt: {len(lines) - 2} texts")


# printf conversions (no ' ' flag: "100% se" is prose)
FORMAT = re.compile(r"%(?:\d+\$)?[-+#0]*\d*(?:\.\d+)?(?:hh|h|ll|l|z)?[diouxXfFeEgGcsp%]")


def read_src(code):
    path = os.path.join(LANG, "src", code + ".txt")
    out = {}
    if not os.path.exists(path):
        return out
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n").rstrip("\r")
        if not line or line.startswith("#"):
            continue
        num, _, text = line.partition("\t")
        if not num.isdigit():
            sys.exit(f"{code}.txt:{i}: no number")
        out[int(num)] = text
    return out


def check(code, english, text):
    if FORMAT.findall(english.replace("%%", "")) != FORMAT.findall(text.replace("%%", "")):
        sys.exit(f"{code}: format specifiers differ:\n  {english}\n  {text}")


def build(code, keys):
    po_name, language, plural_forms = LANGUAGES[code]
    # Flycast's own translation as upstream shipped it (the tree's copy is ours after a run)
    upstream = {}
    base = open(os.path.join(REPO, "patches", "BASE.txt")).read().split("base:")[1].split()[0]
    shown = subprocess.run(["git", "-C", FLYCAST, "show", f"{base}:resources/i18n/{po_name}.po"],
                           capture_output=True, text=True, encoding="utf-8")
    if shown.returncode == 0:
        tmp = os.path.join(LANG, ".upstream.po")
        open(tmp, "w", encoding="utf-8").write(shown.stdout)
        for e in parse_po(tmp):
            if any(e["str"].values()):
                upstream[key_of(e)] = e
        os.remove(tmp)
    src = read_src(code)
    known = {k[0] for k in keys}
    for num in src:
        if num not in known:
            sys.exit(f"{code}: {num} is not in keys.txt")
    out = ['msgid ""', 'msgstr ""', '"Project-Id-Version: flycast\\n"',
           '"MIME-Version: 1.0\\n"', '"Content-Type: text/plain; charset=UTF-8\\n"',
           '"Content-Transfer-Encoding: 8bit\\n"', f'"Language: {language}\\n"',
           f'"Plural-Forms: {plural_forms}\\n"',
           '"X-Generator: DeCast-S4 scripts/make-lang.py (lang/src/' + code + '.txt)\\n"', ""]
    used, missing, mine = set(), 0, 0
    for num, ctx, msgid, plural in keys:
        k = (ctx or "") + "\x04" + msgid
        if ctx:
            out.append(f'msgctxt "{ctx}"')
        out.append(f'msgid "{msgid}"')
        if k in upstream and num < 2000:
            e = upstream[k]
            if plural:
                out.append(f'msgid_plural "{plural}"')
                for i in range(NPLURALS[code]):
                    out.append(f'msgstr[{i}] "{e["str"].get(i, "")}"')
            else:
                out.append(f'msgstr "{e["str"].get(0, "")}"')
            used.update(" ".join(e["str"].values()))
        elif num in src:
            mine += 1
            text = src[num]
            if plural:
                forms = text.split(" || ")
                if len(forms) != NPLURALS[code]:
                    sys.exit(f"{code}: {num} needs {NPLURALS[code]} plural forms")
                out.append(f'msgid_plural "{plural}"')
                for i, form in enumerate(forms):
                    check(code, plural if i else msgid, form)
                    out.append(f'msgstr[{i}] "{form}"')
            else:
                check(code, msgid, text)
                out.append(f'msgstr "{text}"')
            used.update(text)
        else:
            missing += 1
            if plural:
                out.append(f'msgid_plural "{plural}"')
                for i in range(NPLURALS[code]):
                    out.append(f'msgstr[{i}] ""')
            else:
                out.append('msgstr ""')
        out.append("")
    open(os.path.join(I18N, po_name + ".po"), "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print(f"{code} -> {po_name}.po: {len(keys) - missing}/{len(keys)} translated ({mine} from src/{code}.txt)"
          + (f", {missing} MISSING" if missing else ""))
    return used


def make_fonts(used):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools import subset

    os.makedirs(FONTS, exist_ok=True)
    common = set(LANGUAGE_NAMES) | {chr(c) for c in range(0x20, 0x7F)}
    jobs = []
    for code, tag in CJK.items():
        text = used.get(code, set()) | common
        if code == "ja":
            text |= {chr(c) for c in range(0x3040, 0x3100)}  # kana in full
        text |= {chr(c) for c in range(0x3000, 0x3040)} | {chr(c) for c in range(0xFF01, 0xFF5F)}
        jobs.append((f"NotoSans{tag}.ttf", f"NotoSans{tag}-Medium.ttf", text))
    # Arabic: every letter and the presentation forms the shaper (core/oslib/i18n.cpp) produces
    arabic = {chr(c) for c in range(0x0600, 0x0700)} | {chr(c) for c in range(0xFE70, 0xFF00)} \
        | {chr(c) for c in range(0xFB50, 0xFC00)} | common | {"،", "؟", "٫", "٬"}
    jobs.append(("NotoSansArabic.ttf", "NotoSansArabic-Medium.ttf", arabic))
    for source, name, text in jobs:
        font = TTFont(os.path.join(NOTO, source))
        if "fvar" in font:
            font = instancer.instantiateVariableFont(font, {a.axisTag: (500 if a.axisTag == "wght" else a.defaultValue)
                                                            for a in font["fvar"].axes})
        options = subset.Options()
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        subsetter = subset.Subsetter(options)
        subsetter.populate(text="".join(sorted(text)))
        subsetter.subset(font)
        out = os.path.join(FONTS, name)
        font.save(out)
        cmap = font.getBestCmap()
        print(f"  {name}: {os.path.getsize(out) // 1024} KiB, {len(cmap)} glyphs mapped")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "keys":
        write_keys()
        return
    keys = read_keys()
    used = {}
    for code in LANGUAGES:
        used[code] = build(code, keys)
    if "--no-fonts" not in sys.argv:
        make_fonts(used)


if __name__ == "__main__":
    main()
