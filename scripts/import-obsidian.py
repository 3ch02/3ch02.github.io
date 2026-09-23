#!/usr/bin/env python3
"""
Import CTF write-ups from an Obsidian vault into src/content/writeups/.

    python3 scripts/import-obsidian.py "/home/echo/Obsidian Vault" --report   # dry run, prints a table
    python3 scripts/import-obsidian.py "/home/echo/Obsidian Vault"            # writes the files

What it does
- keeps only write-ups (course notes, labs, cheat-sheets, projects are skipped)
- converts Obsidian syntax: ![[image.png]], [[links]], callouts, #tags, ==highlight==, %%comments%%
- copies embedded images next to the write-ups (Astro optimises them at build time)
- infers title, source (CTF / platform), category, difficulty, points, date, tags, summary
- de-duplicates notes that exist twice (keeps the longest)
- marks as draft what must not be published yet (see DRAFT_RULES)

Adjust OVERRIDES / SKIP below and re-run: the import directory is regenerated each time,
files written by hand in src/content/writeups/ (without the `imported: true` marker) are untouched.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "src/content/writeups"
IMG_DIR = OUT_DIR / "images" / "obsidian"  # imported images only, regenerated on each run

# --------------------------------------------------------------------------------------
# Selection
# --------------------------------------------------------------------------------------

# Directories that contain courses / labs / notes, not write-ups
SKIP_DIRS = (
    "AZ-104", "AZ900", "CAPT", "CSOSA", "CWES", "CWSE", "NSE", "FortiGate Training",
    "PortSwiger", "PROJET", "Image", "CTF/Ressources", "CTF/Crypto Coffre", ".obsidian", ".trash",
    "Code review",  # vulnerability practice notes; the only real write-up there duplicates "Le Secret de Nana Benz"
)

SKIP_FILES = {
    "Ohana-security-review.md",  # security review of a real application: confidential, never publish
    "Reverse Courses.md",
    "Approfondissement -- Attaque par falsification de session (Session Forgery).md",
    "CTF/IDOR ID Brute force.md",  # script only, no write-up
    "ClearDesk.md",
    "Writeup --- oupsie.md",  # commands only
}

MIN_CHARS = 900  # notes shorter than this (after cleanup) are drafts/stubs

# Source (CTF / platform) by path prefix — first match wins
SOURCES = [
    ("CTF/picoCTF/picoCTF_2026/", "picoCTF 2026"),
    ("CTF/picoCTF/picoCTF_2019/", "picoCTF 2019"),
    ("CTF/picoCTF/", "picoCTF"),
    ("CTF/ForeverCTF/", "ForeverCTF"),
    ("CTF/hackviser/EcowsCTF{}/", "EcowsCTF (Hackviser)"),
    ("CTF/hackviser/", "Hackviser"),
    ("CTF/Writeup CTF Hackropole/", "Hackropole (FCSC)"),
    # Older IPNET CyberBattle challenges solved outside of any competition (3ch0 did not
    # compete in these editions, just solved the archived challenges) — confirmed 2026-09-23.
    ("CTF/Writeup IPNET Cyberbattle/🚩 Write-up - Find Me.md", "IPNET CyberBattle (archive)"),
    ("CTF/Writeup IPNET Cyberbattle/🚩Writeup Chall Agbetikɔr.md", "IPNET CyberBattle (archive)"),
    ("CTF/Writeup IPNET Cyberbattle/🚩 Writeup chall - My first app.md", "IPNET CyberBattle (archive)"),
    ("CTF/Writeup IPNET Cyberbattle/🚩 Writeup Beats & Spies - La Conspiration AklaaX.md", "IPNET CyberBattle (archive)"),
    ("CTF/Writeup IPNET Cyberbattle/noname.md", "IPNET CyberBattle (archive)"),
    ("CTF/Writeup IPNET Cyberbattle/", "IPNET CyberBattle 2026"),
    ("CTF/Le Secret de Nana Benz.md", "IPNET CyberBattle 2026"),
    ("CTF/Writeup -- Javascript Obfuscation 2.md", "Root-Me"),
    ("CTF/Writeup -- Timestamped Secrets.md", "picoCTF 2026"),
    ("CTF/Writeup -- Vaccine.md", "Hack The Box"),
    ("Kali CTF 2026/", "Kali Team CTF 26"),
    ("Cyberini/", "Cyberini"),
    ("Hackerdna/", "HackerDNA"),
    ("HTB/", "Hack The Box"),
    ("THM/", "TryHackMe"),
    ("pwn.college/", "pwn.college"),
    ("RootME/", "Root-Me"),
    ("Root-Me --- SQL injection - String.md", "Root-Me"),
    ("Writeup --- WAV - Analyse de bruit.md", "Root-Me"),
    ("Crypto 1 (ESIG Tech Arena).md", "ESIG Tech Arena 2026"),
    ("pwn-bof — Writeup.md", "ESIG Tech Arena 2026"),
    ("Web-sqli Writeup.md", "ESIG Tech Arena 2026"),
    ("picoCTF — Disko 2.md", "picoCTF"),
    ("CTF/picoCTF — Disko 2.md", "picoCTF"),
    ("Secret Box.md", "picoCTF"),
    ("Writeup -- No FA.md", "picoCTF"),
    ("Writeup ---No Sql Injection.md", "picoCTF 2024"),
    ("Writeup ---Related Messages.md", "picoCTF 2026"),
    ("Writeup -- Cipher Storm.md", "Hackviser"),
    ("Writeup -- Nexus.md", "Hack The Box"),
    ("Three.md", "Hack The Box"),
    ("Writeup ---  Smol.md", "TryHackMe"),
]

# Competitions that have a page in src/content/ctf/
COMPETITIONS = {
    "IPNET CyberBattle 2026": "ipnet-cyberbattle-2026",
    "Kali Team CTF 26": "kali-team-ctf-2026",
    "ESIG Tech Arena 2026": "esig-tech-arena-2026",
    "boroCTF 2026": "boroctf-2026",
}

# Draft = visible with `npm run dev` only. Reasons are printed in the report.
DRAFT_RULES = [
    (lambda m: m["ctf"] == "ESIG Tech Arena 2026", "ESIG final not played yet — publish after the event"),
    (lambda m: m["ctf"] == "Root-Me", "Root-Me rules forbid publishing solutions"),
    (lambda m: m["ctf"] == "Hack The Box" and m["key"] not in HTB_RETIRED, "HTB: publish only retired machines"),
    (lambda m: m["ctf"] == "Unknown", "unknown source"),
]

# Hack The Box content that is free/retired (Starting Point) — write-ups allowed
HTB_RETIRED = {
    "HTB/Starting Point/Dancing.md", "HTB/Starting Point/Fawn.md", "HTB/Starting Point/Redeemer.md",
    "HTB/Writeup --- Responder.md", "Three.md", "CTF/Writeup -- Vaccine.md",
}

# Manual corrections, keyed by path relative to the vault
OVERRIDES: dict[str, dict] = {
    # titles
    "HTB/Writeup --- Responder.md": {"title": "Responder"},
    "Crypto 1 (ESIG Tech Arena).md": {"title": "Crypto 1"},
    "pwn-bof — Writeup.md": {"title": "pwn-bof"},
    "CTF/hackviser/Next.js CVE-2025-29927(.md": {"title": "Next.js CVE-2025-29927"},
    "CTF/Writeup CTF Hackropole/Crypto/🚩 Chall A l'aise ( Vigenere).md": {"title": "À l'aise (Vigenère)"},
    "CTF/Writeup CTF Hackropole/Crypto/🚩 Crayon Cochon (Chiffre des francs-maçons - Pigpen).md": {"title": "Crayon Cochon (Pigpen)"},
    "CTF/Writeup CTF Hackropole/Crypto/🚩 Claire connu (Known Plaintext)-  XOR.md": {"title": "Clair connu (XOR, known plaintext)"},
    "CTF/Writeup CTF Hackropole/Pwn/Write-up - call-me-blah (Pwn).md": {"title": "call-me-blah"},
    "Kali CTF 2026/🚩 CTF Writeup -- rayray (Bounded Portal).md": {"title": "rayray (Bounded Portal)"},
    "CTF/picoCTF/picoCTF_2019/1_wanna_b3_a_r0ck5tar.md": {"title": "1_wanna_b3_a_r0ck5tar", "category": "Reverse Engineering"},
    "Writeup -- No FA.md": {"title": "No FA"},
    "CTF/picoCTF/picoCTF_2026/Writeup -Forensic - Git Interrupted Recovery.md": {"title": "Git Interrupted Recovery"},
    "Cyberini/Writeup — \"Souvenir de vacances\" (`bali.jpg`).md": {"title": "Souvenir de vacances"},
    "CTF/Writeup IPNET Cyberbattle/🚩 Writeup CTF - Challenge USB.ad1.md": {"title": "USB.ad1"},
    # categories
    "Cyberini/🚩 Writeup -- Cap ou Pcap.md": {"category": "Forensics"},
    "Cyberini/🚩 Writeup -- Crack py.md": {"category": "Reverse Engineering"},
    "Cyberini/🚩 Writeup  -- Crackme.md": {"category": "Reverse Engineering"},
    "CTF/picoCTF/picoCTF_2026/Heap Havoc.md": {"category": "Pwn"},
    # duplicates / untitled
    "Cyberini/🚩 Challenge  Souvenir de vacances.md": {"skip": True},
    "CTF/picoCTF/Writeup - Forensics Git 0.md": {"skip": True},
    "CTF/hackviser/Scénario.md": {"draft": "untitled scenario — add its name"},

    # --- Reviewed 2026-09-23: incomplete write-ups (no flag / no conclusion) kept as drafts ---
    "Cyberini/Writeup- Buffer Overflow.md": {"draft": "incomplete: stops before the exploit script and flag"},
    "CTF/picoCTF/picoCTF_2026/ClusterRSA.md": {"draft": "incomplete: script given but final flag never shown"},
    "CTF/picoCTF/picoCTF_2026/Heap Havoc.md": {"draft": "incomplete: stops before the exploit payload and flag"},
    "CTF/hackviser/EcowsCTF{}/📑 Writeup Challenge -Layer Cake.md": {"draft": "incomplete: script given but resulting flag never shown"},
    "CTF/picoCTF/picoCTF_2026/Quizploit.md": {"draft": "incomplete: stops before the exploit script and flag"},
    "CTF/hackviser/Scénario Rivalry.md": {"draft": "incomplete: only two recon commands, no resolution"},
    "CTF/hackviser/Shadow Track.md": {"draft": "incomplete: final answers (hash, count) never stated"},
    "CTF/Writeup CTF Hackropole/Crypto/🚩 SMIC 1.md": {"draft": "incomplete: script given but computed flag value never shown"},
    "Writeup ---  Smol.md": {"draft": "incomplete: stops after recovering WordPress creds, no flag"},
    "Three.md": {"draft": "incomplete: stops at subdomain discovery, no flag"},
    "CTF/Writeup -- Vaccine.md": {"draft": "incomplete: stops before exploiting the SQLi/RCE, no flag"},
    "CTF/ForeverCTF/Warnhup Alahoma.md": {"draft": "incomplete: stops mid-enumeration, no flag"},
    "CTF/hackviser/Pwn22Pwn.md": {"draft": "raw payload dump, no challenge context or flag"},
    "Hackerdna/Query Quake.md": {"draft": "incomplete: dumps a table but never states the flag"},
    "CTF/picoCTF/picoCTF_2026/Printes Share 2.md": {"draft": "incomplete: stops before reading the flag"},
    "HTB/Writeup --- Responder.md": {"draft": "incomplete: gets a shell but never states the flag"},
    "CTF/hackviser/Warmup Able.md": {"draft": "incomplete: gets root but never states the flag"},
    "CTF/hackviser/Warmup Dynamic Book.md": {"draft": "incomplete: privesc set up but never confirmed/flag missing"},
    "CTF/hackviser/Warmup Quenovia.md": {"draft": "incomplete: reverse shell sent but result/flag never shown"},
    "CTF/hackviser/Warmups Moonshade.md": {"draft": "incomplete: stops mid-privesc, no flag"},
    "CTF/hackviser/warmups Satellite.md": {"draft": "incomplete: exploit listed but never run, no flag"},
    "CTF/hackviser/Warmups Work Stuff.md": {"draft": "incomplete: stops mid-exploitation, no flag"},
    "CTF/picoCTF/picoCTF_2026/Front_Running.md": {"draft": "incomplete: attack described but never executed, no flag"},
    "CTF/picoCTF/picoCTF_2026/MSS_ADVANCE Revenge.md": {"draft": "incomplete: script given but flag never shown"},
    "CTF/hackviser/EcowsCTF{}/Annoying XOR.md": {"draft": "incomplete: stops after a partial Ghidra dump, no flag"},
    "CTF/hackviser/EcowsCTF{}/📑 Writeup -Adinkra.md": {"draft": "incomplete: only shows the data file, no analysis or flag"},
    "Writeup -- Cipher Storm.md": {"draft": "incomplete: identifies the vuln but never exploits it, no flag"},
    "CTF/hackviser/Next.js CVE-2025-29927(.md": {"draft": "incomplete: bypass shown but no flag ever captured"},
    "pwn.college/web security/🚩 CMDi 6 (Newline Filter Bypass) — pwn.college.md": {"draft": "duplicate of cmdi-6-command-injection-bypass-via-encodage-url (same challenge, same flag)"},
    "CTF/Writeup CTF Hackropole/Crypto/🚩 Crayon Cochon (Chiffre des francs-maçons - Pigpen).md": {"draft": "flag looks unverified: raw pigpen ciphertext submitted, not decoded"},
    # metadata fix: this note is filed under Cyberini but is a Kali Team CTF challenge
    "Cyberini/🚩 Writeup -- Robots (Web - 100 PTS).md": {"ctf": "Kali Team CTF 26"},
    # metadata fix: filed under picoCTF by folder, but the flag format (boroCTF{...}) and the
    # note itself ("Plateforme : boroCTF") say otherwise.
    "CTF/picoCTF/Writeup - Flight.md": {"ctf": "boroCTF 2026"},
    "CTF/picoCTF/Writeup - So Many Layers.md": {"ctf": "boroCTF 2026"},
}

# Body clean-ups keyed by vault path: (regex, replacement) applied after conversion.
BODY_FIXES: dict[str, list[tuple[str, str]]] = {
    "CTF/hackviser/Scénario Data Heist.md": [(r"\n+HACKKKK THE WORD\s*$", "\n")],
}

CATEGORIES = ["Forensics", "Cryptography", "Web", "Reverse Engineering", "Steganography", "OSINT", "Pwn", "Misc", "Boot2Root"]

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return re.sub(r"-{2,}", "-", value)


def split_frontmatter(text: str) -> tuple[dict, str]:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            try:
                data = yaml.safe_load(text[4:end]) or {}
                if isinstance(data, dict):
                    return data, text[end + 4 :].lstrip("\n")
            except yaml.YAMLError:
                pass
    return {}, text


def source_for(key: str) -> str:
    for prefix, name in SOURCES:
        if key == prefix or key.startswith(prefix):
            return name
    return "Unknown"


def clean_title(raw: str) -> str:
    t = EMOJI_RE.sub("", raw)
    t = re.sub(r"\.md$", "", t)
    t = re.sub(r"(?i)\b(write[- ]?up|writep|wrieup|wrirteup)\b", "", t)
    t = re.sub(r"(?i)^\s*(htb|ctf|chall(enge)?|forensic|forensics)\b\s*[-—:]*", "", t)
    t = re.sub(r"(?i)\b(challenge|chall)\s*[-—:]+", "", t)
    t = re.sub(r"(?i)\s*[-—]+\s*(pwn\.college|cyberini|tryhackme)\s*$", "", t)
    t = re.sub(r"(?i)\(tryhackme\)|tryhackme\s*", "", t)
    t = re.sub(r"(?i)\s*\((easy|medium|hard|insane)\)", "", t)
    t = re.sub(r"(?i)\s*\((web|crypto|pwn)?\s*-?\s*\d+\s*pts?\)", "", t)
    t = re.sub(r"(?i)\s*\(\d+\s*pts?\)", "", t)
    t = re.sub(r"(?i)^\s*(picoctf|root-me)\s*[-—:]+", "", t)
    t = re.sub(r"(?i)\s*[-—]+\s*writeup\s*$", "", t)
    t = t.replace("`", "").replace("\"", "")
    t = re.sub(r"\s*[-—:]+\s*$", "", t)
    t = re.sub(r"^\s*[-—:]+\s*", "", t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t[:1].upper() + t[1:] if t else raw


CATEGORY_WORDS = [
    ("Steganography", r"st[ée]g|steghide|zsteg|exiftool|audacity|spectrogram"),
    ("Forensics", r"forensi|pcap|wireshark|disk|\.dd\b|volatility|memory|m[ée]moire|autopsy|sleuth|fls\b|icat\b|git\b|timeline|metadata|m[ée]tadonn"),
    ("Cryptography", r"crypt|rsa\b|\bxor\b|cipher|chiffr|aes\b|ecdsa|vigen|hash|hmac|diffie"),
    ("Reverse Engineering", r"reverse|ghidra|crackme|d[ée]compil|disassembl|obfusc|bytecode|apk\b"),
    ("Pwn", r"\bpwn\b|buffer overflow|\bbof\b|rop\b|format string|shellcode|gdb\b|pwntools|heap"),
    ("OSINT", r"osint|g[ée]olocali|geoint"),
    ("Web", r"\bweb\b|sqli|sql injection|xss|ssti|ssrf|idor|cookie|jwt|burp|curl\b|http|lfi\b|path traversal|cmdi|command injection|nosql"),
    ("Boot2Root", r"privesc|privilege escalation|[ée]l[ée]vation de privil|root\.txt|user\.txt|\bssh\b|nmap"),
]

EXPLICIT = [
    ("Steganography", r"st[ée]g"),
    ("Forensics", r"forensi"),
    ("Cryptography", r"crypt"),
    ("Reverse Engineering", r"revers|\brev\b"),
    ("Pwn", r"\bpwn\b|binary exploitation|exploitation binaire"),
    ("OSINT", r"osint"),
    ("Misc", r"\bmisc\b|prompt injection"),
    ("Web", r"\bweb\b"),
]


def infer_category(key: str, fm: dict, title: str, body: str) -> str:
    if key.startswith("pwn.college/web"):
        return "Web"
    explicit = " ".join(
        str(x)
        for x in [fm.get("category", ""), fm.get("categorie", ""), fm.get("catégorie", "")]
        + [m.group(1) for m in re.finditer(r"(?i)cat[ée]gorie\s*:?\**\s*:?\s*\**\s*([^\n]+)", body[:1500])]
    )
    for cat, pat in EXPLICIT:
        if re.search(pat, explicit, re.I):
            return cat
    head = " ".join([title, key.replace("pwn.college", ""), " ".join(map(str, fm.get("tags", []) or []))])
    for cat, pat in EXPLICIT:
        if re.search(pat, head, re.I):
            return cat
    if key.startswith(("HTB/", "THM/", "CTF/hackviser/Warm", "CTF/hackviser/warm", "CTF/hackviser/Sc", "Three.md", "CTF/Writeup -- Vaccine", "Writeup -- Nexus", "Writeup ---  Smol", "Writeup -- Cipher Storm")):
        return "Boot2Root"
    if key.startswith("pwn.college/web"):
        return "Web"
    scores = {c: len(re.findall(p, body, re.I)) for c, p in CATEGORY_WORDS}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Misc"


def infer_difficulty(fm: dict, title: str, body: str) -> str | None:
    blob = " ".join([str(fm.get("difficulty", "")), str(fm.get("difficulte", "")), title, body[:2500]])
    m = re.search(r"(?i)difficult[ée]\s*:?\**\s*:?\s*\**\s*([^\n]+)", blob) or re.search(
        r"(?i)\b(very easy|easy|medium|hard|insane)[- ]difficulty", blob
    )
    text = (m.group(1) if m else str(fm.get("difficulty", "")) or title).lower()
    for word, level in [
        ("insane", "Insane"), ("very easy", "Easy"), ("easy", "Easy"), ("facile", "Easy"), ("medium", "Medium"),
        ("moyen", "Medium"), ("intermédiaire", "Medium"), ("intermediaire", "Medium"), ("hard", "Hard"), ("difficile", "Hard"),
    ]:
        if word in text:
            return level
    return None


def infer_points(fm: dict, title: str, body: str) -> int | None:
    for src in [str(fm.get("points", "")), title, body[:1500]]:
        m = re.search(r"(?i)points?\s*:?\**\s*:?\s*\**\s*(\d{2,4})\b", src) or re.search(r"(?i)\b(\d{2,4})\s*pts?\b", src)
        if m:
            return int(m.group(1))
    return None


def birth_or_mtime(path: Path) -> date:
    """File creation time (when the note was written), falling back to mtime."""
    st = path.stat()
    ts = getattr(st, "st_birthtime", None)
    if not ts:
        try:
            out = subprocess.run(["stat", "-c", "%W", str(path)], capture_output=True, text=True, check=True).stdout.strip()
            ts = int(out) or None
        except (OSError, subprocess.CalledProcessError, ValueError):
            ts = None
    return datetime.fromtimestamp(ts or st.st_mtime).date()


def infer_date(fm: dict, body: str, path: Path) -> date:
    d = fm.get("date")
    if isinstance(d, (date, datetime)):
        return d if isinstance(d, date) else d.date()
    if isinstance(d, str):
        try:
            return datetime.fromisoformat(d[:10]).date()
        except ValueError:
            pass
    stamps = re.findall(r"Pasted image (20\d{6})", body)
    if stamps:
        s = min(stamps)
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    return birth_or_mtime(path)


KNOWN_LANGS = set(
    "python py bash sh shell zsh console powershell ps1 c cpp c++ js javascript ts typescript json yaml yml html xml css sql "
    "php java go rust ruby perl text txt plaintext diff http ini toml dockerfile nginx asm nasm markdown md jsx tsx lua csharp "
    "cs kotlin swift r makefile graphql regex vb batch cmd hex".split()
)
LANG_ALIASES = {"c++": "cpp", "hex": "text", "cmd": "batch", "txt": "text", "plaintext": "text"}


def convert_body(body: str, images: dict[str, Path], slug: str, copy: bool, log: list[str]) -> tuple[str, set[str]]:
    tags: set[str] = set()
    body = re.sub(r"%%[\s\S]*?%%", "", body)  # Obsidian comments
    lines = body.split("\n")
    out: list[str] = []
    in_code = False
    fence = ""
    pending_lang: str | None = None
    used_names: dict[str, str] = {}

    def image_md(name: str, alt: str = "") -> str:
        name = name.split("|")[0].strip()
        base = Path(name).name
        src = images.get(base) or images.get(base.replace("%20", " "))
        if not src:
            log.append(f"missing image: {name}")
            return ""
        stem = slugify(Path(base).stem) or "image"
        ext = src.suffix.lower()
        fname = used_names.setdefault(base, f"{stem}{ext}")
        if copy:
            dest = IMG_DIR / slug / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        return f"![{alt or 'Screenshot'}](./images/obsidian/{slug}/{fname})"

    for line in lines:
        stripped = line.strip()
        fm = re.match(r"^(\s*)(```+|~~~+)\s*([\w+#.-]*)(.*)$", line)
        if fm:
            if not in_code:
                in_code, fence = True, fm.group(2)
                lang = (fm.group(3) or pending_lang or "").lower()
                lang = LANG_ALIASES.get(lang, lang)
                if lang and lang not in KNOWN_LANGS:
                    lang = "text"
                out.append(f"{fm.group(1)}{fence}{lang}")
                pending_lang = None
                continue
            if fm.group(2).startswith(fence[0]) and len(fm.group(2)) >= len(fence) and not fm.group(3):
                in_code = False
                out.append(f"{fm.group(1)}{fm.group(2)}")
                continue
        if in_code:
            out.append(line)
            continue

        # stray language label copied from a web page ("Bash" on its own line before a code block)
        if re.fullmatch(r"(?i)(bash|python|shell|sh|plaintext|text|javascript|js|sql|powershell|json|html|c|code|php|console)", stripped):
            pending_lang = stripped.lower()
            continue
        if stripped == "" and pending_lang:
            continue
        pending_lang = None

        # typing artefacts such as "''''''''''''" or "21''''''"
        if re.fullmatch(r"\d*'{5,}\S*", stripped) or re.fullmatch(r"'{3,}", stripped):
            continue

        # standalone wiki links to other notes: drop
        if re.fullmatch(r"\[\[[^\]]+\]\]", stripped):
            continue

        # images: ![[x.png]] / ![[x.png|300]] / ![alt](local.png)
        line = re.sub(r"!\[\[([^\]]+\.(?:png|jpe?g|gif|webp|svg|bmp))(?:\|[^\]]*)?\]\]", lambda m: image_md(m.group(1)), line, flags=re.I)
        line = re.sub(
            r"!\[([^\]]*)\]\((?!https?:|\./images/obsidian/)([^)\s]+\.(?:png|jpe?g|gif|webp|svg|bmp))\)",
            lambda m: image_md(m.group(2).replace("%20", " "), m.group(1)),
            line,
            flags=re.I,
        )
        line = re.sub(r"!\[\[[^\]]+\]\]", "", line)  # embedded notes
        # wiki links → text
        line = re.sub(r"\[\[([^\]|#]+)(?:#[^\]|]*)?\|([^\]]+)\]\]", r"\2", line)
        line = re.sub(r"\[\[([^\]|#]+)(?:#([^\]|]*))?\]\]", lambda m: m.group(2) or m.group(1), line)
        # callouts
        line = re.sub(
            r"^(\s*>\s*)\[!(\w+)\][+-]?\s*(.*)$",
            lambda m: f"{m.group(1)}**{m.group(3).strip() or m.group(2).capitalize()}**",
            line,
        )
        # table alignment markers (:---) become inline styles, which the CSP blocks
        if re.fullmatch(r"\s*\|?(\s*:?-+:?\s*\|)+\s*(:?-+:?)?\s*\|?\s*", line):
            line = line.replace(":", "")
        # highlights
        line = re.sub(r"==([^=\n]+)==", r"**\1**", line)

        # inline #tags (outside inline code)
        parts = re.split(r"(`[^`]*`)", line)
        for i, part in enumerate(parts):
            if part.startswith("`"):
                continue

            def tag_repl(m: re.Match) -> str:
                tags.add(m.group(1).lower())
                return m.group(1)

            parts[i] = re.sub(r"(?<![\w/&#.:=?%'\"-])#([A-Za-zÀ-ÿ][\w/À-ÿ-]*)", tag_repl, part)
        new_line = "".join(parts)
        if not re.match(r"^\s*#{1,6}\s", line) and re.fullmatch(r"(\s*(\*\*)?tags\s*:?\s*(\*\*)?\s*:?)?[\s\w/À-ÿ-]*", new_line) and new_line.strip() and new_line.strip() != line.strip() and len(new_line.split()) <= 8:
            # the line only contained tags
            continue
        out.append(new_line)

    text = "\n".join(out)
    # headings: the page already renders an <h1>, so body headings start at h2
    heading_levels = [len(m.group(1)) for m in re.finditer(r"(?m)^(#{1,6})\s", strip_code(text))]
    if heading_levels and min(heading_levels) == 1:
        text = shift_headings(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text, tags


def strip_code(text: str) -> str:
    return re.sub(r"(?ms)^(```|~~~).*?^\1", "", text)


def shift_headings(text: str) -> str:
    out, in_code = [], False
    for line in text.split("\n"):
        if re.match(r"^\s*(```|~~~)", line):
            in_code = not in_code
        if not in_code and re.match(r"^#{1,5}\s", line):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def extract_summary(fm: dict, body: str) -> str | None:
    for key in ("description", "summary"):
        if isinstance(fm.get(key), str) and fm[key].strip():
            return shorten(fm[key])
    text = strip_code(body)
    m = re.search(r"(?is)#+\s*[^\n]*description[^\n]*\n+((?:>.*\n?)+|[^\n#].*)", text)
    candidates = [m.group(1)] if m else []
    candidates += [p for p in re.split(r"\n\s*\n", text) if p.strip() and not p.lstrip().startswith(("#", "|", "!", "-", "*", "---", "<"))]
    for c in candidates:
        s = re.sub(r"(?m)^\s*>\s?", "", c)
        s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
        s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
        s = re.sub(r"[*_`]+", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        s = re.sub(r"^[-•]\s*", "", s)
        s = re.split(r"\s#{1,6}\s", s)[0].strip()
        metadata_like = len(re.findall(r"\b[\wÀ-ÿ' ]{2,25}\s:\s", s)) >= 2 or c.lstrip().startswith(("-", "*"))
        if len(s) >= 40 and not metadata_like and not re.match(r"(?i)^(aper[çc]u|cat[ée]gorie|points|auteur|author|flag|tags?|plateforme)\b", s):
            return shorten(s)
    return None


def shorten(s: str, n: int = 180) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:.—-")
    return cut + "…"


def title_from(fm: dict, body: str, filename: str) -> tuple[str, str]:
    if isinstance(fm.get("title"), str) and fm["title"].strip():
        t = fm["title"].strip()
        t = re.sub(r"(?i)^(forensics|crypto|web|pwn|misc)\s*-\s*", "", t)
        t = re.sub(r"\s*\((memory\.dump|picoctf \d{4})\)\s*$", "", t, flags=re.I)
        return clean_title(t), body
    body = re.sub(r"^\s*#[ \t]*\n", "", body)
    m = re.match(r"\s*#[ \t]+(\S.*)\n", body)
    if m and len(m.group(1)) < 90:
        return clean_title(m.group(1)), body[m.end():]
    return clean_title(filename), body


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------


def collect(vault: Path, copy: bool) -> list[dict]:
    images = {p.name: p for p in vault.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}}
    notes = []
    for path in sorted(vault.rglob("*.md")):
        key = path.relative_to(vault).as_posix()
        if key.startswith(SKIP_DIRS) or key in SKIP_FILES or re.match(r"(.*/)?Sans titre", key):
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        fm, body = split_frontmatter(raw)
        if len(body.strip()) < 200:
            continue
        ov = OVERRIDES.get(key, {})
        if ov.get("skip"):
            continue
        title, body = title_from(fm, body, path.name)
        title = ov.get("title", title)
        ctf = ov.get("ctf", source_for(key))
        slug = ov.get("slug") or slugify(f"{title}")
        notes.append(dict(key=key, path=path, fm=fm, body=body, title=title, ctf=ctf, slug=slug, ov=ov))

    # de-duplicate: same title + same platform family → keep the longest note
    def family(ctf: str) -> str:
        return re.sub(r"\s*\d{4}$", "", ctf)

    best: dict[tuple, dict] = {}
    for n in notes:
        k = (slugify(n["title"]), family(n["ctf"]))
        if k not in best or len(n["body"]) > len(best[k]["body"]):
            if k in best:
                best[k]["dup_of"] = n["key"]
            best[k] = n
    notes = list(best.values())

    # unique slugs
    seen: dict[str, int] = {}
    for n in sorted(notes, key=lambda n: n["key"]):
        if n["slug"] in seen:
            n["slug"] = f"{n['slug']}-{slugify(n['ctf'])}"
        seen[n["slug"]] = 1

    results = []
    for n in notes:
        log: list[str] = []
        text, inline_tags = convert_body(n["body"], images, n["slug"], copy, log)
        for pat, repl in BODY_FIXES.get(n["key"], []):
            text = re.sub(pat, repl, text)
        fm, ov = n["fm"], n["ov"]
        category = ov.get("category") or infer_category(n["key"], fm, n["title"], n["body"])
        fm_tags = fm.get("tags") or []
        if isinstance(fm_tags, str):
            fm_tags = re.split(r"[,\s]+", fm_tags)
        tags = {slugify(str(t).split("/")[-1]) for t in list(fm_tags) + list(inline_tags)}
        tags |= {slugify(category), slugify(n["ctf"].split(" (")[0])}
        tags -= {"", "ctf", "writeup", "write-up", "unknown", "resolu", "solved", "easy", "medium", "hard", "facile"}
        meta = dict(
            key=n["key"],
            slug=n["slug"],
            title=n["title"],
            ctf=n["ctf"],
            category=category,
            difficulty=ov.get("difficulty") or infer_difficulty(fm, n["title"], n["body"]),
            points=ov.get("points") or infer_points(fm, n["title"], n["body"]),
            date=infer_date(fm, n["body"], n["path"]),
            tags=sorted(tags)[:8],
            summary=ov.get("summary") or extract_summary(fm, text),
            chars=len(text),
            log=log,
        )
        reasons = [why for rule, why in DRAFT_RULES if rule(meta)]
        if meta["chars"] < MIN_CHARS:
            reasons.append("very short note")
        if "draft" in ov:
            reasons = [ov["draft"]] if ov["draft"] else []
        meta["draft_reasons"] = reasons
        meta["body"] = text
        results.append(meta)
    return sorted(results, key=lambda m: (m["ctf"], m["title"]))


def write(results: list[dict]) -> None:
    # remove previously imported files only
    for f in OUT_DIR.glob("*.md"):
        if "\nimported: true\n" in f.read_text(encoding="utf-8"):
            f.unlink()
    for m in results:
        target = OUT_DIR / f"{m['slug']}.md"
        if target.exists() and "\nimported: true\n" not in target.read_text(encoding="utf-8"):
            continue  # curated by hand (reviewed / cleaned): never overwritten
        data = {
            "title": m["title"],
            "category": m["category"],
            **({"difficulty": m["difficulty"]} if m["difficulty"] else {}),
            "ctf": m["ctf"],
            **({"competition": COMPETITIONS[m["ctf"]]} if m["ctf"] in COMPETITIONS else {}),
            "date": m["date"],
            **({"summary": m["summary"]} if m["summary"] else {}),
            "tags": m["tags"],
            **({"points": m["points"]} if m["points"] else {}),
            "lang": "fr",
            **({"draft": True} if m["draft_reasons"] else {}),
            "imported": True,
        }
        head = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)
        comment = f"# Imported from Obsidian: {m['key']}\n"
        if m["draft_reasons"]:
            comment += f"# Draft: {'; '.join(m['draft_reasons'])}\n"
        target.write_text(f"---\n{comment}{head}---\n\n{m['body']}", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vault", type=Path)
    ap.add_argument("--report", action="store_true", help="dry run: print the table, write nothing")
    args = ap.parse_args()
    if not args.vault.is_dir():
        sys.exit(f"vault not found: {args.vault}")

    if not args.report and IMG_DIR.exists():
        shutil.rmtree(IMG_DIR)  # imported images are regenerated from scratch
    results = collect(args.vault, copy=not args.report)
    for m in results:
        flag = "DRAFT" if m["draft_reasons"] else "pub  "
        print(
            f"{flag}\t{m['ctf'][:22]:22}\t{m['category'][:12]:12}\t{(m['difficulty'] or '-'):6}\t{m['date']}\t{m['chars']:6}\t"
            f"{m['title'][:48]:48}\t{m['key']}\t{'; '.join(m['draft_reasons'])}\t{' | '.join(m['log'][:2])}"
        )
    pub = sum(1 for m in results if not m["draft_reasons"])
    print(f"\n{len(results)} write-ups: {pub} published, {len(results) - pub} drafts", file=sys.stderr)
    if not args.report:
        write(results)


if __name__ == "__main__":
    main()
