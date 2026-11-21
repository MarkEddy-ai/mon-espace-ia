from __future__ import annotations

import html
import math
import random
from typing import Any, Dict, List, Optional, Tuple

from kdp_extensions.i18n_config import (
    get_puzzle_word_banks,
    get_alphabet,
    get_editorial_labels,
    normalize_language,
    is_rtl,
)

WORD_BANKS: Dict[str, List[str]] = {
    "animaux": [
        "LION", "TIGRE", "ELEPHANT", "GIRAFE", "ZEBRE", "RENARD",
        "LAPIN", "OURS", "DAUPHIN", "AIGLE", "TORTUE", "HIBOU",
        "CHAMEAU", "PERROQUET", "ECUREUIL", "PANDA",
    ],
    "espace": [
        "ETOILE", "PLANETE", "FUSEE", "LUNE", "SOLEIL", "COMETE",
        "GALAXIE", "ORBITE", "ASTRE", "MARS", "SATURNE", "COSMOS",
        "METEORE", "ASTRONAUTE", "TELESCOPE", "NEBULEUSE",
    ],
    "ocean": [
        "BALEINE", "CORAIL", "REQUIN", "POULPE", "PHARE", "ANCRE",
        "VOILIER", "VAGUE", "CRABE", "MEDUSE", "PORT", "ILE",
        "COQUILLAGE", "HIPPOCAMPE", "SARDINE", "ROCHER",
    ],
    "voyage": [
        "VALISE", "CARTE", "BOUSSOLE", "SENTIER", "SOMMET", "VOYAGE",
        "HORIZON", "PASSEPORT", "EXCURSION", "CAMPING", "RIVIERE", "FORET",
    ],
    "general": [
        "AVENTURE", "ESPRIT", "LOGIQUE", "VICTOIRE", "MYSTERE", "ENIGME",
        "ASTUCE", "DEFI", "COURAGE", "CHEMIN", "ETAPE", "TALENT",
        "MEMOIRE", "REUSSITE", "DECOUVERTE", "SAVOIR",
    ],
}

RIDDLE_BANK: List[Tuple[str, str]] = [
    ("Je parle sans bouche et j'entends sans oreilles. Qui suis-je ?", "ECHO"),
    ("Plus je sèche, plus je deviens mouillée. Qui suis-je ?", "SERVIETTE"),
    ("J'ai des aiguilles mais je ne pique pas, et j'indique l'heure. Qui suis-je ?", "HORLOGE"),
    ("Je monte mais je ne descends jamais. Qui suis-je ?", "AGE"),
    ("J'ai des pages et des chapitres mais je ne suis pas un arbre. Qui suis-je ?", "LIVRE"),
    ("Je brille dans le ciel la nuit et je change de forme. Qui suis-je ?", "LUNE"),
]

WORD_LADDERS: List[List[str]] = [
    ["CHAT", "CHAR", "CHOR", "CHOU", "CLOU"],
    ["MAIN", "PAIN", "PAIX", "PAIS", "POIS"],
    ["BOIS", "BOIT", "SOIT", "SOIE", "SOIF"],
    ["LUNE", "DUNE", "DURE", "CURE", "CUBE"],
    ["PORT", "FORT", "SORT", "SORS", "BOLS"],
]


def _pick_words(
    words: Optional[List[str]],
    theme: str,
    count: int = 8,
    rng: Optional[random.Random] = None,
    language: str = "fr",
) -> List[str]:
    r = rng or random.Random(42)
    lang_code = normalize_language(language)
    localized_banks = get_puzzle_word_banks(lang_code)
    alphabet = get_alphabet(lang_code)
    allowed_chars = set(alphabet)

    base = words if words else localized_banks.get(theme.lower().strip(), localized_banks.get("general", WORD_BANKS["general"]))
    cleaned: List[str] = []
    for w in base:
        clean = "".join(ch for ch in str(w).upper() if ch in allowed_chars or ("A" <= ch <= "Z"))
        if 2 <= len(clean) <= 14 and clean not in cleaned:
            cleaned.append(clean)
    if not cleaned:
        cleaned = localized_banks.get("general", WORD_BANKS["general"])[:]
    r.shuffle(cleaned)
    while len(cleaned) < count:
        gen = localized_banks.get("general", WORD_BANKS["general"])
        filler = gen[len(cleaned) % len(gen)]
        if filler not in cleaned:
            cleaned.append(filler)
        else:
            cleaned.append(f"{filler}{len(cleaned) + 1}")
    return cleaned[:count]


def generate_word_search(
    title: str = "Mots Mêlés",
    words: Optional[List[str]] = None,
    theme: str = "general",
    rows: int = 12,
    cols: int = 12,
    allow_diagonal: bool = True,
    seed: Optional[int] = None,
    language: str = "fr",
) -> Dict[str, Any]:
    lang_code = normalize_language(language)
    alphabet = get_alphabet(lang_code)
    rng = random.Random(seed)
    rows = max(8, min(20, int(rows)))
    cols = max(8, min(20, int(cols)))
    max_len = min(rows, cols)

    candidates = [w for w in _pick_words(words, theme, count=10, rng=rng, language=lang_code) if len(w) <= max_len]
    grid: List[List[str]] = [["" for _ in range(cols)] for _ in range(rows)]
    placed: List[Dict[str, Any]] = []

    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    if allow_diagonal:
        dirs.extend([(1, 1), (-1, 1), (1, -1), (-1, -1)])

    for word in candidates:
        for _ in range(150):
            dr, dc = rng.choice(dirs)
            r0 = rng.randint(0, rows - 1)
            c0 = rng.randint(0, cols - 1)
            r1 = r0 + dr * (len(word) - 1)
            c1 = c0 + dc * (len(word) - 1)
            if not (0 <= r1 < rows and 0 <= c1 < cols):
                continue

            coords: List[Tuple[int, int]] = []
            conflict = False
            for idx, ch in enumerate(word):
                rr, cc = r0 + dr * idx, c0 + dc * idx
                if grid[rr][cc] not in ("", ch):
                    conflict = True
                    break
                coords.append((rr, cc))

            if not conflict:
                for (rr, cc), ch in zip(coords, word):
                    grid[rr][cc] = ch
                placed.append({"word": word, "cells": coords})
                break

    for r in range(rows):
        for c in range(cols):
            if not grid[r][c]:
                grid[r][c] = rng.choice(alphabet)

    labels = get_editorial_labels(lang_code)
    display_title = title if title != "Mots Mêlés" else labels.get("puzzle_title", "Mots Mêlés")

    return {
        "type": "word_search",
        "title": display_title,
        "rows": rows,
        "cols": cols,
        "grid": grid,
        "words": [p["word"] for p in placed],
        "solution": placed,
        "language": lang_code,
        "is_rtl": is_rtl(lang_code),
    }


def generate_word_scramble(
    title: str = "Mots Mélangés",
    words: Optional[List[str]] = None,
    theme: str = "general",
    count: int = 8,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    selected = _pick_words(words, theme, count=max(4, min(15, int(count))), rng=rng)
    items: List[Dict[str, str]] = []
    for w in selected:
        chars = list(w)
        scrambled = w
        for _ in range(10):
            rng.shuffle(chars)
            candidate = "".join(chars)
            if candidate != w:
                scrambled = candidate
                break
        items.append({"scrambled": scrambled, "answer": w, "hint": f"{len(w)} lettres"})

    return {
        "type": "word_scramble",
        "title": title,
        "items": items,
    }


def generate_word_ladder(
    title: str = "Échelle de Mots",
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    chain = rng.choice(WORD_LADDERS)
    steps: List[Dict[str, Any]] = []
    for idx, word in enumerate(chain):
        is_fixed = idx == 0 or idx == len(chain) - 1
        steps.append({
            "step": idx + 1,
            "length": len(word),
            "fixed": is_fixed,
            "value": word if is_fixed else "",
            "answer": word,
        })
    return {
        "type": "word_ladder",
        "title": title,
        "start_word": chain[0],
        "end_word": chain[-1],
        "steps": steps,
    }


def generate_riddles_set(
    title: str = "Devinettes & Mots Mystères",
    count: int = 4,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    pool = RIDDLE_BANK[:]
    rng.shuffle(pool)
    chosen = pool[: max(1, min(len(pool), int(count)))]
    items = [
        {"question": q, "answer": a, "blanks": ["_"] * len(a)}
        for q, a in chosen
    ]
    return {
        "type": "riddles",
        "title": title,
        "items": items,
    }


def generate_cryptogram(
    title: str = "Code Secret",
    phrase: str = "BRAVO TU AS REUSSI",
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    clean_phrase = "".join(ch for ch in phrase.upper() if ("A" <= ch <= "Z") or ch == " ")
    if not clean_phrase.strip():
        clean_phrase = "BRAVO TU AS REUSSI"

    letters = sorted({ch for ch in clean_phrase if "A" <= ch <= "Z"})
    codes = list(range(10, 10 + len(letters)))
    rng.shuffle(codes)
    cipher = {ch: str(code) for ch, code in zip(letters, codes)}
    reverse_cipher = {str(code): ch for ch, code in cipher.items()}

    encoded_tokens: List[Dict[str, Any]] = []
    for ch in clean_phrase:
        if ch == " ":
            encoded_tokens.append({"space": True})
        else:
            encoded_tokens.append({"space": False, "code": cipher[ch], "answer": ch})

    return {
        "type": "cryptogram",
        "title": title,
        "phrase": clean_phrase,
        "cipher_key": reverse_cipher,
        "tokens": encoded_tokens,
    }


def generate_maze(
    title: str = "Labyrinthe",
    width_cells: int = 12,
    height_cells: int = 12,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    cols = max(6, min(25, int(width_cells)))
    rows = max(6, min(25, int(height_cells)))

    visited = [[False for _ in range(cols)] for _ in range(rows)]
    walls: Dict[Tuple[int, int], Dict[str, bool]] = {
        (r, c): {"N": True, "E": True, "S": True, "W": True}
        for r in range(rows)
        for c in range(cols)
    }
    opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
    deltas = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}

    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {(0, 0): None}
    stack: List[Tuple[int, int]] = [(0, 0)]
    visited[0][0] = True

    while stack:
        r, c = stack[-1]
        neighbors = [
            (d, r + dr, c + dc)
            for d, (dr, dc) in deltas.items()
            if 0 <= r + dr < rows and 0 <= c + dc < cols and not visited[r + dr][c + dc]
        ]
        if neighbors:
            d, nr, nc = rng.choice(neighbors)
            walls[(r, c)][d] = False
            walls[(nr, nc)][opposite[d]] = False
            visited[nr][nc] = True
            parent[(nr, nc)] = (r, c)
            stack.append((nr, nc))
        else:
            stack.pop()

    walls[(0, 0)]["N"] = False
    walls[(rows - 1, cols - 1)]["S"] = False

    path: List[Tuple[int, int]] = []
    cur: Optional[Tuple[int, int]] = (rows - 1, cols - 1)
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()

    return {
        "type": "maze",
        "title": title,
        "rows": rows,
        "cols": cols,
        "walls": {f"{r},{c}": walls[(r, c)] for r in range(rows) for c in range(cols)},
        "solution_path": path,
    }


def generate_logic_grid(
    title: str = "Grille de Logique",
    size: int = 4,
    clues_to_remove: int = 6,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    n = 6 if int(size) >= 6 else 4
    base = (
        [
            [1, 2, 3, 4],
            [3, 4, 1, 2],
            [2, 1, 4, 3],
            [4, 3, 2, 1],
        ]
        if n == 4
        else [
            [1, 2, 3, 4, 5, 6],
            [4, 5, 6, 1, 2, 3],
            [2, 3, 1, 5, 6, 4],
            [5, 6, 4, 2, 3, 1],
            [3, 1, 2, 6, 4, 5],
            [6, 4, 5, 3, 1, 2],
        ]
    )

    nums = list(range(1, n + 1))
    shuffled = nums[:]
    rng.shuffle(shuffled)
    mapping = {a: b for a, b in zip(nums, shuffled)}

    solution = [[mapping[v] for v in row] for row in base]
    rng.shuffle(solution)
    puzzle = [row[:] for row in solution]

    to_clear = min(max(2, int(clues_to_remove)), n * n - n)
    coords = [(r, c) for r in range(n) for c in range(n)]
    rng.shuffle(coords)
    for r, c in coords[:to_clear]:
        puzzle[r][c] = 0

    return {
        "type": "logic_grid",
        "title": title,
        "size": n,
        "puzzle": puzzle,
        "solution": solution,
    }


def generate_connect_dots(
    title: str = "Points à Relier (1 à 12)",
    points_count: int = 12,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    n = max(6, min(30, int(points_count)))
    cx, cy = 200.0, 200.0
    base_r = 125.0
    pts: List[Dict[str, Any]] = []
    for i in range(n):
        angle = (2.0 * math.pi * i) / n - (math.pi / 2.0)
        jitter = rng.uniform(0.78, 1.15)
        x = round(cx + base_r * jitter * math.cos(angle), 1)
        y = round(cy + base_r * jitter * math.sin(angle), 1)
        pts.append({"num": i + 1, "x": x, "y": y})

    return {
        "type": "connect_dots",
        "title": title,
        "points": pts,
    }


def _render_maze_svg(maze: Dict[str, Any], highlight_solution: bool = False, cell_px: int = 32) -> str:
    rows, cols = int(maze["rows"]), int(maze["cols"])
    walls = maze["walls"]
    margin = 16
    w_svg = cols * cell_px + margin * 2
    h_svg = rows * cell_px + margin * 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_svg} {h_svg}" width="100%" style="max-width:{w_svg}px;background:#FFFFFF;display:block;margin:0 auto;">',
        f'<rect x="0" y="0" width="{w_svg}" height="{h_svg}" fill="#FFFFFF"/>',
    ]
    if highlight_solution and maze.get("solution_path"):
        poly = " ".join(
            f"{margin + c * cell_px + cell_px/2:.1f},{margin + r * cell_px + cell_px/2:.1f}"
            for r, c in maze["solution_path"]
        )
        out.append(f'<polyline points="{poly}" fill="none" stroke="#000000" stroke-width="3" stroke-dasharray="6,4"/>')

    for r in range(rows):
        for c in range(cols):
            w = walls[f"{r},{c}"]
            x0, y0 = margin + c * cell_px, margin + r * cell_px
            x1, y1 = x0 + cell_px, y0 + cell_px
            if w.get("N"):
                out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#000000" stroke-width="3"/>')
            if w.get("S"):
                out.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#000000" stroke-width="3"/>')
            if w.get("W"):
                out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#000000" stroke-width="3"/>')
            if w.get("E"):
                out.append(f'<line x1="{x1}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#000000" stroke-width="3"/>')
    out.append("</svg>")
    return "\n".join(out)


def _render_dots_svg(puzzle: Dict[str, Any], show_lines: bool = False) -> str:
    pts = puzzle.get("points", [])
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" style="max-width:380px;background:#FFFFFF;display:block;margin:0 auto;">',
        '<rect x="0" y="0" width="400" height="400" fill="#FFFFFF"/>',
    ]
    if show_lines and len(pts) >= 2:
        poly = " ".join(f"{p['x']},{p['y']}" for p in pts) + f" {pts[0]['x']},{pts[0]['y']}"
        out.append(f'<polygon points="{poly}" fill="none" stroke="#000000" stroke-width="2.5"/>')
    for p in pts:
        out.append(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="4" fill="#000000"/>')
        out.append(f'<text x="{p["x"] + 7}" y="{p["y"] - 6}" font-size="13" font-weight="700" fill="#000000">{p["num"]}</text>')
    out.append("</svg>")
    return "\n".join(out)


def _puzzle_html(p: Dict[str, Any], idx: int) -> str:
    t = p["type"]
    title = html.escape(str(p["title"]))
    head = f'<div class="p-head"><span class="p-num">#{idx}</span><h2>{title}</h2></div>'

    if t == "word_search":
        trs = ["<tr>" + "".join(f"<td>{html.escape(ch)}</td>" for ch in row) + "</tr>" for row in p["grid"]]
        words_html = "".join(f'<span class="chip">{html.escape(w)}</span>' for w in p["words"])
        return f'<section class="p-page">{head}<table class="grid">{"".join(trs)}</table><div class="bank"><strong>Mots à trouver :</strong><div class="chips">{words_html}</div></div></section>'

    if t == "word_scramble":
        lis = "".join(
            f'<li><span class="scr">{html.escape(it["scrambled"])}</span> <span class="hint">({html.escape(it["hint"])})</span> → <span class="line">________________</span></li>'
            for it in p["items"]
        )
        return f'<section class="p-page">{head}<ul class="scramble-list">{lis}</ul></section>'

    if t == "word_ladder":
        boxes = "".join(
            f'<div class="ladder-row">Étape {s["step"]} : <span class="word-slot">{html.escape(s["value"]) if s["fixed"] else " ".join(["_"] * s["length"])}</span></div>'
            for s in p["steps"]
        )
        return f'<section class="p-page">{head}<p class="hint">Changez une seule lettre à chaque étape pour passer de <strong>{html.escape(p["start_word"])}</strong> à <strong>{html.escape(p["end_word"])}</strong>.</p><div class="ladder">{boxes}</div></section>'

    if t == "riddles":
        cards = "".join(
            f'<div class="riddle-item"><p><strong>{html.escape(it["question"])}</strong></p><p class="answer-line">Réponse : {" ".join(["___"] * len(it["answer"]))}</p></div>'
            for it in p["items"]
        )
        return f'<section class="p-page">{head}{cards}</section>'

    if t == "cryptogram":
        cells = []
        for tok in p["tokens"]:
            if tok.get("space"):
                cells.append('<span class="space-gap"></span>')
            else:
                cells.append(f'<span class="crypto-box"><span class="blank"></span><span class="code-lbl">{html.escape(tok["code"])}</span></span>')
        key_pairs = " · ".join(f"{html.escape(k)}={html.escape(v)}" for k, v in sorted(p["cipher_key"].items(), key=lambda x: int(x[0])))
        return f'<section class="p-page">{head}<div class="crypto-phrase">{"".join(cells)}</div><p class="hint">Clé : {key_pairs}</p></section>'

    if t == "maze":
        return f'<section class="p-page">{head}{_render_maze_svg(p, False)}</section>'

    if t == "connect_dots":
        return f'<section class="p-page">{head}{_render_dots_svg(p, False)}</section>'

    trs = ["<tr>" + "".join(f"<td>{'' if v == 0 else html.escape(str(v))}</td>" for v in row) + "</tr>" for row in p["puzzle"]]
    return f'<section class="p-page">{head}<table class="grid">{"".join(trs)}</table><p class="hint">Complétez chaque ligne et colonne avec 1 à {int(p["size"])} sans répétition.</p></section>'


def _solution_html(p: Dict[str, Any], idx: int) -> str:
    t = p["type"]
    title = html.escape(str(p["title"]))
    head = f'<h4>#{idx} — {title}</h4>'

    if t == "word_search":
        sol_cells = {(r, c) for it in p.get("solution", []) for r, c in it.get("cells", [])}
        trs = [
            "<tr>" + "".join(f'<td class="{"hit" if (r, c) in sol_cells else "dim"}">{html.escape(ch)}</td>' for c, ch in enumerate(row)) + "</tr>"
            for r, row in enumerate(p["grid"])
        ]
        return f'<div class="sol-card">{head}<table class="grid mini">{"".join(trs)}</table></div>'

    if t == "word_scramble":
        items = ", ".join(f'{html.escape(it["scrambled"])} → <strong>{html.escape(it["answer"])}</strong>' for it in p["items"])
        return f'<div class="sol-card">{head}<p class="sol-text">{items}</p></div>'

    if t == "word_ladder":
        chain = " → ".join(html.escape(s["answer"]) for s in p["steps"])
        return f'<div class="sol-card">{head}<p class="sol-text">{chain}</p></div>'

    if t == "riddles":
        items = " · ".join(f'<strong>{html.escape(it["answer"])}</strong>' for it in p["items"])
        return f'<div class="sol-card">{head}<p class="sol-text">{items}</p></div>'

    if t == "cryptogram":
        return f'<div class="sol-card">{head}<p class="sol-text"><strong>{html.escape(p["phrase"])}</strong></p></div>'

    if t == "maze":
        return f'<div class="sol-card">{head}{_render_maze_svg(p, True, 20)}</div>'

    if t == "connect_dots":
        return f'<div class="sol-card">{head}{_render_dots_svg(p, True)}</div>'

    trs = ["<tr>" + "".join(f'<td class="hit">{html.escape(str(v))}</td>' for v in row) + "</tr>" for row in p["solution"]]
    return f'<div class="sol-card">{head}<table class="grid mini">{"".join(trs)}</table></div>'


def generate_full_puzzle_collection(
    book_title: str = "Grand Livre de Puzzles, Mots & Logique",
    theme: str = "general",
    age_group: str = "6-9",
    puzzle_types: Optional[List[str]] = None,
    puzzles_per_type: int = 2,
    custom_words: Optional[List[str]] = None,
    secret_phrase: str = "BRAVO TU AS REUSSI",
    seed: int = 123,
    language: str = "fr",
) -> Dict[str, Any]:
    lang_code = normalize_language(language)
    labels = get_editorial_labels(lang_code)
    rtl = is_rtl(lang_code)
    dir_attr = " dir='rtl'" if rtl else ""

    rng = random.Random(seed)
    all_types = [
        "word_search",
        "word_scramble",
        "word_ladder",
        "riddles",
        "cryptogram",
        "maze",
        "connect_dots",
        "logic_grid",
    ]
    active_types = [t for t in (puzzle_types or all_types) if t in all_types] or all_types
    per_type = max(1, min(20, int(puzzles_per_type)))

    is_young = str(age_group).strip() in ("3-5", "4-6", "4-8")
    grid_dim = 9 if is_young else 12
    logic_dim = 4 if is_young else 6

    puzzles: List[Dict[str, Any]] = []
    ws_title = labels.get("puzzle_title", "Mots Mêlés")
    for p_type in active_types:
        for i in range(per_type):
            s = rng.randint(1, 999999)
            if p_type == "word_search":
                puzzles.append(generate_word_search(f"{ws_title} ({i+1})", custom_words, theme, grid_dim, grid_dim, not is_young, s, language=lang_code))
            elif p_type == "word_scramble":
                puzzles.append(generate_word_scramble(f"Mots Mélangés ({i+1})", custom_words, theme, 6 if is_young else 8, s))
            elif p_type == "word_ladder":
                puzzles.append(generate_word_ladder(f"Échelle de Mots ({i+1})", s))
            elif p_type == "riddles":
                puzzles.append(generate_riddles_set(f"Devinettes ({i+1})", 3 if is_young else 4, s))
            elif p_type == "cryptogram":
                puzzles.append(generate_cryptogram(f"Code Secret ({i+1})", secret_phrase, s))
            elif p_type == "maze":
                puzzles.append(generate_maze(f"Labyrinthe ({i+1})", grid_dim, grid_dim, s))
            elif p_type == "connect_dots":
                puzzles.append(generate_connect_dots(f"Points à Relier ({i+1})", 10 if is_young else 16, s))
            elif p_type == "logic_grid":
                puzzles.append(generate_logic_grid(f"Logique ({i+1})", logic_dim, (logic_dim * logic_dim) // 2, s))

    body_html = "\n".join(_puzzle_html(p, idx + 1) for idx, p in enumerate(puzzles))
    sol_html = "\n".join(_solution_html(p, idx + 1) for idx, p in enumerate(puzzles))

    solutions_title = labels.get("puzzle_solutions", "Solutionnaire Complet")

    css = """
    <style>
      @page { size: letter; margin: 0.6in; }
      body { font-family: 'Nunito', 'Fredoka', Arial, sans-serif; color: #000000; background: #FFFFFF; margin: 0; }
      .header-banner { text-align: center; border-bottom: 2px solid #000000; padding-bottom: 14px; margin-bottom: 20px; }
      .p-page { page-break-after: always; padding: 8px 0; }
      .p-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
      .p-num { border: 2px solid #000000; padding: 2px 8px; font-weight: 800; }
      .grid { border-collapse: collapse; margin: 0 auto 14px; }
      .grid td { width: 28px; height: 28px; border: 1.5px solid #000000; text-align: center; vertical-align: middle; font-weight: 700; font-size: 13px; background: #FFFFFF; color: #000000; }
      .grid.mini td { width: 19px; height: 19px; font-size: 10px; }
      .grid td.hit { font-weight: 800; border: 2px solid #000000; }
      .grid td.dim { opacity: 0.35; }
      .bank { border: 1.5px solid #000000; padding: 10px; }
      .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
      .chip { border: 1px solid #000000; padding: 2px 7px; font-size: 12px; font-weight: 700; }
      .scramble-list { list-style: none; padding: 0; font-size: 15px; line-height: 2.1; }
      .scr { font-weight: 800; letter-spacing: 2px; border: 1px solid #000000; padding: 2px 8px; }
      .ladder-row { font-size: 15px; margin: 10px 0; font-weight: 700; }
      .word-slot { letter-spacing: 3px; border-bottom: 1.5px solid #000000; padding: 2px 10px; }
      .riddle-item { border: 1px solid #000000; padding: 10px 14px; margin-bottom: 12px; }
      .crypto-phrase { display: flex; flex-wrap: wrap; gap: 6px; margin: 18px 0; }
      .crypto-box { display: inline-flex; flex-direction: column; align-items: center; }
      .blank { width: 24px; height: 26px; border-bottom: 2px solid #000000; display: block; }
      .code-lbl { font-size: 11px; font-weight: 700; margin-top: 2px; }
      .space-gap { width: 18px; display: inline-block; }
      .hint { font-size: 12px; text-align: center; }
      .solutions { page-break-before: always; }
      .sol-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
      .sol-card { border: 1px solid #000000; padding: 8px; }
      .sol-card h4 { margin: 0 0 6px; font-size: 12px; }
      .sol-text { font-size: 12px; margin: 0; }
    </style>
    """

    full_html = (
        f"<!DOCTYPE html><html lang='{lang_code}'{dir_attr}><head><meta charset='utf-8'><title>{html.escape(book_title)}</title>{css}</head><body>"
        f"<div class='header-banner'><h1>{html.escape(book_title)}</h1>"
        f"<p>Thème : <strong>{html.escape(theme)}</strong> · Âge : <strong>{html.escape(age_group)}</strong> · Total jeux : <strong>{len(puzzles)}</strong></p></div>"
        f"{body_html}"
        f"<section class='solutions'><h2>{solutions_title}</h2><div class='sol-grid'>{sol_html}</div></section>"
        f"</body></html>"
    )

    return {
        "status": "success",
        "book_title": book_title,
        "theme": theme,
        "age_group": age_group,
        "puzzle_types": active_types,
        "total_puzzles": len(puzzles),
        "puzzles": puzzles,
        "html": full_html,
        "language": lang_code,
        "is_rtl": rtl,
    }