"""Write the CODE-Q1 fixture files and manifest from the definitions below.

Deterministic and offline: running it twice produces byte-identical files. It executes
nothing and contacts nothing. Run `python grade.py verify-fixtures` afterwards.

Task ids, families, callables and contracts follow research/coding-quality-v1.proposed.json
(ChatGPT/Codex, main at 3701d34). This file adds what that proposal left null: prompts,
pinned starters, references, decoys and test cases.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "fixtures"

SINGLE = ("Reply with exactly one fenced Python code block containing the complete file. "
          "No explanation.")
MULTI = ("Reply with one fenced Python code block per file. The first line inside each block "
         "must be a comment naming the file, for example `# file: invoice.py`. No explanation.")
SINGLE_AR = "أجب بمقطع برمجي واحد فقط بلغة Python داخل علامات ``` يحتوي الملف كاملا، ومن دون أي شرح."


def case(call, args, expect=None, raises=None):
    item = {"call": call, "args": args}
    if raises:
        item["raises"] = raises
    else:
        item["expect"] = expect
    return item


TASKS = {}


def task(tid, family, lang, files, prompt, reference, decoy, public, hidden, starter=None):
    TASKS[tid] = dict(family=family, prompt_language=lang, files=files, prompt=prompt,
                      reference=reference, decoy=decoy, public=public, hidden=hidden,
                      starter=starter or {})


# ---------------------------------------------------------------- F01
task("F01", "function", "en", ["solution.py"],
     "Write solution.py with a function stable_unique(values: list[str]) -> list[str].\n"
     "Return the first occurrence of each distinct string, in the original order. Comparison is "
     "case-sensitive. Empty strings and any Unicode are valid. Do not modify the input list.\n"
     "Example: stable_unique([\"b\", \"a\", \"b\"]) returns [\"b\", \"a\"].\n" + SINGLE,
     {"solution.py": '''def stable_unique(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
'''},
     {"solution.py": '''def stable_unique(values):
    return sorted(set(values))
'''},
     [case("solution.stable_unique", [["b", "a", "b"]], ["b", "a"])],
     [case("solution.stable_unique", [[]], []),
      case("solution.stable_unique", [["a", "A", "a"]], ["a", "A"]),
      case("solution.stable_unique", [["", "x", "", "x"]], ["", "x"]),
      case("solution.stable_unique", [["z", "y", "x", "y", "z"]], ["z", "y", "x"]),
      case("solution.stable_unique", [["سلام", "hi", "سلام"]],
           ["سلام", "hi"]),
      case("solution.stable_unique", [["one"]], ["one"])])

# ---------------------------------------------------------------- F02
task("F02", "function", "en", ["solution.py"],
     "Write solution.py with a function merge_intervals(intervals: list[list[int]]) -> list[list[int]].\n"
     "Each input item is [start, end] with start <= end. Return new closed intervals sorted by "
     "start, with all overlapping intervals merged. Intervals that share an endpoint, such as "
     "[1, 3] and [3, 5], overlap. Intervals that are only adjacent as integers, such as [1, 2] "
     "and [3, 4], stay separate. An empty list returns []. Do not modify the input.\n"
     "Example: merge_intervals([[1, 3], [2, 6]]) returns [[1, 6]].\n" + SINGLE,
     {"solution.py": '''def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
'''},
     {"solution.py": '''def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
'''},
     [case("solution.merge_intervals", [[[1, 3], [2, 6]]], [[1, 6]])],
     [case("solution.merge_intervals", [[]], []),
      case("solution.merge_intervals", [[[1, 2], [3, 4]]], [[1, 2], [3, 4]]),
      case("solution.merge_intervals", [[[1, 3], [3, 5]]], [[1, 5]]),
      case("solution.merge_intervals", [[[8, 10], [1, 3], [2, 6], [15, 18]]], [[1, 6], [8, 10], [15, 18]]),
      case("solution.merge_intervals", [[[1, 10], [2, 3], [4, 5]]], [[1, 10]]),
      case("solution.merge_intervals", [[[-5, -1], [-2, 0], [5, 5]]], [[-5, 0], [5, 5]]),
      case("solution.merge_intervals", [[[4, 4], [4, 4]]], [[4, 4]])])

# ---------------------------------------------------------------- F03
task("F03", "function", "en", ["solution.py"],
     "Write solution.py with a function parse_kv(text: str) -> dict[str, str].\n"
     "Split the text with str.splitlines(). Ignore blank lines and lines whose first "
     "non-whitespace character is #. Split every other line at its first =, and strip outer "
     "whitespace from the key and from the value; later = characters stay in the value. A "
     "repeated key keeps its last value. An empty value is allowed. A line with an empty key or "
     "with no = raises ValueError.\n"
     "Example: parse_kv(\"a = 1\\n# note\\nb=x=y\") returns {\"a\": \"1\", \"b\": \"x=y\"}.\n" + SINGLE,
     {"solution.py": '''def parse_kv(text):
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ValueError("missing =")
        key, value = stripped.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("empty key")
        result[key] = value.strip()
    return result
'''},
     {"solution.py": '''def parse_kv(text):
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split("=")
        if len(parts) < 2:
            raise ValueError("missing =")
        result[parts[0].strip()] = parts[1].strip()
    return result
'''},
     [case("solution.parse_kv", ["a = 1\n# note\nb=x=y"], {"a": "1", "b": "x=y"})],
     [case("solution.parse_kv", [""], {}),
      case("solution.parse_kv", ["\n   \n  # only a comment\n"], {}),
      case("solution.parse_kv", ["k=\n"], {"k": ""}),
      case("solution.parse_kv", ["k=1\nk=2"], {"k": "2"}),
      case("solution.parse_kv", ["  name =  two  words  "], {"name": "two  words"}),
      case("solution.parse_kv", ["url=http://x/?a=b&c=d"], {"url": "http://x/?a=b&c=d"}),
      case("solution.parse_kv", ["اسم=قيمة"],
           {"اسم": "قيمة"}),
      case("solution.parse_kv", ["novalue"], raises="ValueError"),
      case("solution.parse_kv", [" = 3"], raises="ValueError")])

# ---------------------------------------------------------------- B01
B01_STARTER = '''def sliding_windows(values, size):
    windows = []
    for start in range(len(values) - size):
        windows.append(values[start:start + size])
    return windows
'''
task("B01", "bugfix", "en", ["windows.py"],
     "The file windows.py below has bugs. Fix sliding_windows(values: list[int], size: int) -> "
     "list[list[int]] so that it returns every contiguous window of the given size, moving one "
     "position at a time, in order. If size is larger than the list, return []. If size equals "
     "the list length (and the list is not empty), return one window. If size <= 0, raise "
     "ValueError. An empty list with a positive size returns []. Do not modify the input.\n"
     "Example: sliding_windows([1, 2, 3], 2) returns [[1, 2], [2, 3]].\n\n"
     "```python\n" + B01_STARTER + "```\n" + SINGLE,
     {"windows.py": '''def sliding_windows(values, size):
    if size <= 0:
        raise ValueError("size must be positive")
    return [values[start:start + size] for start in range(len(values) - size + 1)]
'''},
     None,
     [case("windows.sliding_windows", [[1, 2, 3], 2], [[1, 2], [2, 3]])],
     [case("windows.sliding_windows", [[1, 2, 3], 3], [[1, 2, 3]]),
      case("windows.sliding_windows", [[1, 2, 3], 4], []),
      case("windows.sliding_windows", [[], 1], []),
      case("windows.sliding_windows", [[7], 1], [[7]]),
      case("windows.sliding_windows", [[1, 2, 3, 4], 1], [[1], [2], [3], [4]]),
      case("windows.sliding_windows", [[1, 2, 3], 0], raises="ValueError"),
      case("windows.sliding_windows", [[1, 2, 3], -1], raises="ValueError"),
      case("windows.sliding_windows", [[], 0], raises="ValueError")],
     starter={"windows.py": B01_STARTER})

# ---------------------------------------------------------------- B02
B02_STARTER = '''def lookup(cache, key, default):
    return cache.get(key) or default
'''
task("B02", "bugfix", "en", ["cache.py"],
     "The file cache.py below has a bug. Fix lookup(cache: dict, key: str, default) so that it "
     "returns cache[key] whenever the key exists, even when the stored value is None, False, 0, "
     "an empty string, an empty list or an empty dict. Return default only when the key is "
     "absent. Do not modify the arguments.\n"
     "Example: lookup({\"a\": 0}, \"a\", 5) returns 0.\n\n"
     "```python\n" + B02_STARTER + "```\n" + SINGLE,
     {"cache.py": '''def lookup(cache, key, default):
    if key in cache:
        return cache[key]
    return default
'''},
     None,
     [case("cache.lookup", [{"a": 0}, "a", 5], 0)],
     [case("cache.lookup", [{"a": None}, "a", "d"], None),
      case("cache.lookup", [{"a": False}, "a", True], False),
      case("cache.lookup", [{"a": ""}, "a", "d"], ""),
      case("cache.lookup", [{"a": []}, "a", [1]], []),
      case("cache.lookup", [{"a": {}}, "a", {"x": 1}], {}),
      case("cache.lookup", [{"a": 1}, "b", "d"], "d"),
      case("cache.lookup", [{}, "a", None], None),
      case("cache.lookup", [{"a": "v"}, "a", "d"], "v")],
     starter={"cache.py": B02_STARTER})

# ---------------------------------------------------------------- B03
B03_STARTER = '''def median(values):
    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) // 2
'''
task("B03", "bugfix", "en", ["stats.py"],
     "The file stats.py below has bugs. Fix median(values: list[int]) -> float. Work on a sorted "
     "copy. For an odd number of values return the middle one; for an even number return the "
     "arithmetic mean of the two middle values. Always return a float. An empty list raises "
     "ValueError. Do not modify the input.\n"
     "Example: median([3, 1, 2]) returns 2.0.\n\n"
     "```python\n" + B03_STARTER + "```\n" + SINGLE,
     {"stats.py": '''def median(values):
    if not values:
        raise ValueError("empty")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2
'''},
     None,
     [case("stats.median", [[3, 1, 2]], 2.0)],
     [case("stats.median", [[5]], 5.0),
      case("stats.median", [[4, 1, 3, 2]], 2.5),
      case("stats.median", [[2, 2]], 2.0),
      case("stats.median", [[-3, 10, 0]], 0.0),
      case("stats.median", [[1000000, -1000000]], 0.0),
      case("stats.median", [[9, 7, 8, 1, 3]], 7.0),
      case("stats.median", [[]], raises="ValueError")],
     starter={"stats.py": B03_STARTER})

# ---------------------------------------------------------------- E01
E01_STARTER = '''def to_seconds(config):
    """Return the configuration unchanged (timeouts are still in milliseconds)."""
    return dict(config)
'''
task("E01", "edit", "en", ["config.py"],
     "Change to_seconds in config.py below. It must return a new dict. If the key timeout_ms is "
     "present, replace it with the key timeout_s whose value is timeout_ms / 1000, and keep "
     "every other entry. If both timeout_ms and timeout_s are present, raise ValueError. If "
     "timeout_ms is absent, return an equal copy. Do not modify the input.\n"
     "Example: to_seconds({\"timeout_ms\": 1500, \"name\": \"a\"}) returns "
     "{\"timeout_s\": 1.5, \"name\": \"a\"}.\n\n"
     "```python\n" + E01_STARTER + "```\n" + SINGLE,
     {"config.py": '''def to_seconds(config):
    """Return a copy with timeout_ms converted to timeout_s."""
    result = dict(config)
    if "timeout_ms" in result:
        if "timeout_s" in result:
            raise ValueError("both timeout_ms and timeout_s present")
        result["timeout_s"] = result.pop("timeout_ms") / 1000
    return result
'''},
     None,
     [case("config.to_seconds", [{"timeout_ms": 1500, "name": "a"}], {"timeout_s": 1.5, "name": "a"})],
     [case("config.to_seconds", [{"timeout_ms": 2000}], {"timeout_s": 2.0}),
      case("config.to_seconds", [{"timeout_ms": 0}], {"timeout_s": 0.0}),
      case("config.to_seconds", [{"name": "x", "retries": 3}], {"name": "x", "retries": 3}),
      case("config.to_seconds", [{}], {}),
      case("config.to_seconds", [{"timeout_s": 4}], {"timeout_s": 4}),
      case("config.to_seconds", [{"timeout_ms": 1, "nested": {"timeout_ms": 5}}],
           {"timeout_s": 0.001, "nested": {"timeout_ms": 5}}),
      case("config.to_seconds", [{"timeout_ms": 1000, "timeout_s": 1}], raises="ValueError")],
     starter={"config.py": E01_STARTER})

# ---------------------------------------------------------------- E02
E02_STARTER = '''def clamp(value, lo, hi):
    raise NotImplementedError


def sign(value):
    raise NotImplementedError


def is_even(value):
    raise NotImplementedError


def first_or_none(values):
    raise NotImplementedError


def last_or_none(values):
    raise NotImplementedError


def count_nonempty(values):
    raise NotImplementedError


def reverse_text(text):
    raise NotImplementedError
'''
task("E02", "edit", "en", ["bundle.py"],
     "Implement all seven functions in bundle.py below.\n"
     "- clamp(value, lo, hi): value limited to the inclusive range lo..hi (lo <= hi).\n"
     "- sign(value): -1, 0 or 1.\n"
     "- is_even(value): True or False.\n"
     "- first_or_none(values): the first item, or None for an empty list.\n"
     "- last_or_none(values): the last item, or None for an empty list.\n"
     "- count_nonempty(values): how many strings have length > 0 (a space counts as non-empty).\n"
     "- reverse_text(text): the text reversed by Unicode code points.\n"
     "Do not modify inputs.\n\n"
     "```python\n" + E02_STARTER + "```\n" + SINGLE,
     {"bundle.py": '''def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def sign(value):
    return (value > 0) - (value < 0)


def is_even(value):
    return value % 2 == 0


def first_or_none(values):
    return values[0] if values else None


def last_or_none(values):
    return values[-1] if values else None


def count_nonempty(values):
    return sum(1 for value in values if len(value) > 0)


def reverse_text(text):
    return text[::-1]
'''},
     None,
     [case("bundle.clamp", [5, 1, 3], 3), case("bundle.sign", [-4], -1)],
     [case("bundle.clamp", [0, 1, 3], 1), case("bundle.clamp", [2, 1, 3], 2),
      case("bundle.clamp", [3, 3, 3], 3), case("bundle.clamp", [-7, -5, -1], -5),
      case("bundle.sign", [0], 0), case("bundle.sign", [9], 1),
      case("bundle.is_even", [0], True), case("bundle.is_even", [7], False),
      case("bundle.is_even", [-2], True),
      case("bundle.first_or_none", [[]], None), case("bundle.first_or_none", [[0, 1]], 0),
      case("bundle.first_or_none", [[None, 2]], None),
      case("bundle.last_or_none", [[]], None), case("bundle.last_or_none", [[1, False]], False),
      case("bundle.count_nonempty", [[]], 0), case("bundle.count_nonempty", [["", " ", "a"]], 2),
      case("bundle.reverse_text", [""], ""), case("bundle.reverse_text", ["abc"], "cba"),
      case("bundle.reverse_text", ["سلام"], "مالس")],
     starter={"bundle.py": E02_STARTER})

# ---------------------------------------------------------------- E03
E03_INVOICE = '''def subtotal(items):
    return sum(unit_cents for quantity, unit_cents in items)


def total(items, discount_cents):
    return subtotal(items) - discount_cents
'''
E03_SUMMARY = '''from invoice import subtotal, total


def render(items, discount_cents):
    return {
        "line_count": len(set(map(tuple, items))),
        "subtotal": subtotal(items),
        "total": total(items, discount_cents),
    }
'''
ITEMS = [[2, 250], [1, 100], [2, 250]]
task("E03", "edit", "en", ["invoice.py", "summary.py"],
     "Fix the two files below and keep the public functions.\n"
     "- invoice.subtotal(items): items is a list of [quantity, unit_cents] rows; return the sum "
     "of quantity * unit_cents.\n"
     "- invoice.total(items, discount_cents): subtotal minus the discount, never below 0.\n"
     "- summary.render(items, discount_cents): return exactly the keys line_count (number of "
     "rows; duplicate rows count separately), subtotal_cents and total_cents.\n"
     "Do not modify inputs.\n\n"
     "```python\n# file: invoice.py\n" + E03_INVOICE + "```\n\n"
     "```python\n# file: summary.py\n" + E03_SUMMARY + "```\n" + MULTI,
     {"invoice.py": '''def subtotal(items):
    return sum(quantity * unit_cents for quantity, unit_cents in items)


def total(items, discount_cents):
    return max(0, subtotal(items) - discount_cents)
''',
      "summary.py": '''from invoice import subtotal, total


def render(items, discount_cents):
    return {
        "line_count": len(items),
        "subtotal_cents": subtotal(items),
        "total_cents": total(items, discount_cents),
    }
'''},
     None,
     [case("invoice.subtotal", [[[2, 250], [1, 100]]], 600)],
     [case("invoice.subtotal", [[]], 0),
      case("invoice.subtotal", [ITEMS], 1100),
      case("invoice.subtotal", [[[0, 999], [3, 0]]], 0),
      case("invoice.total", [ITEMS, 100], 1000),
      case("invoice.total", [ITEMS, 5000], 0),
      case("invoice.total", [[], 0], 0),
      case("summary.render", [ITEMS, 100], {"line_count": 3, "subtotal_cents": 1100, "total_cents": 1000}),
      case("summary.render", [[], 50], {"line_count": 0, "subtotal_cents": 0, "total_cents": 0}),
      case("summary.render", [[[1, 1]], 0], {"line_count": 1, "subtotal_cents": 1, "total_cents": 1})],
     starter={"invoice.py": E03_INVOICE, "summary.py": E03_SUMMARY})

# ---------------------------------------------------------------- A01 (Arabic instruction)
task("A01", "arabic", "ar", ["solution.py"],
     "اكتب الملف solution.py وفيه الدالة word_counts(text) لعد الكلمات الناتجة من str.split() دون فاصل "
     "محدد. احتفظ بالحروف وعلامات الترقيم والتشكيل كما هي دون تطبيع. أعد قاموسا بعدد مرات ظهور كل "
     "كلمة؛ والنص الفارغ أو المكوّن من فراغات فقط يعطي قاموسا فارغا.\n"
     "مثال: word_counts(\"a b a\") تعيد {\"a\": 2, \"b\": 1}.\n" + SINGLE_AR,
     {"solution.py": '''def word_counts(text):
    counts = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts
'''},
     {"solution.py": '''def word_counts(text):
    counts = {}
    for word in text.lower().split(" "):
        counts[word] = counts.get(word, 0) + 1
    return counts
'''},
     [case("solution.word_counts", ["a b a"], {"a": 2, "b": 1})],
     [case("solution.word_counts", [""], {}),
      case("solution.word_counts", ["  \n\t "], {}),
      case("solution.word_counts", ["Hi hi HI"], {"Hi": 1, "hi": 1, "HI": 1}),
      case("solution.word_counts", ["one,  one, one"], {"one,": 2, "one": 1}),
      case("solution.word_counts", ["سلام عليكم سلام"],
           {"سلام": 2, "عليكم": 1}),
      case("solution.word_counts", ["عِلم علم"],
           {"عِلم": 1, "علم": 1}),
      case("solution.word_counts", ["x\ny\tx"], {"x": 2, "y": 1})])

# ---------------------------------------------------------------- A02
task("A02", "arabic", "ar", ["solution.py"],
     "اكتب الملف solution.py وفيه الدالة ascii_digits(text) لتحويل الأرقام من المجالين U+0660 إلى U+0669 "
     "وU+06F0 إلى U+06F9 إلى الأرقام ASCII من 0 إلى 9. حافظ على جميع المحارف الأخرى وترتيبها، بما فيها "
     "الأرقام الموجودة أصلا بالصيغة ASCII. النص الفارغ يبقى فارغا.\n"
     "مثال: ascii_digits(\"١٢\") تعيد \"12\".\n" + SINGLE_AR,
     {"solution.py": '''def ascii_digits(text):
    result = []
    for char in text:
        code = ord(char)
        if 0x0660 <= code <= 0x0669:
            result.append(chr(code - 0x0660 + 48))
        elif 0x06F0 <= code <= 0x06F9:
            result.append(chr(code - 0x06F0 + 48))
        else:
            result.append(char)
    return "".join(result)
'''},
     {"solution.py": '''import unicodedata


def ascii_digits(text):
    return "".join(str(unicodedata.digit(char)) if char.isdigit() else char for char in text)
'''},
     [case("solution.ascii_digits", ["١٢"], "12")],
     [case("solution.ascii_digits", [""], ""),
      case("solution.ascii_digits", ["٠١٢٣٤٥٦٧٨٩"], "0123456789"),
      case("solution.ascii_digits", ["۰۱۲۳۴۵۶۷۸۹"], "0123456789"),
      case("solution.ascii_digits", ["a1٢b"], "a12b"),
      case("solution.ascii_digits", ["عام ٢٠٢٦"], "عام 2026"),
      case("solution.ascii_digits", ["१२"], "१२"),
      case("solution.ascii_digits", ["no digits"], "no digits")])

# ---------------------------------------------------------------- A03
A03_STARTER = '''def chunk_text(text, width):
    chunks = []
    for start in range(0, len(text) - width, width):
        chunks.append(text[start:start + width])
    return chunks
'''
task("A03", "arabic", "ar", ["chunks.py"],
     "أصلح الدالة chunk_text(text, width) في الملف chunks.py أدناه لتقسيم النص من اليسار إلى اليمين إلى "
     "مقاطع لا يتجاوز طول كل منها width من نقاط Unicode، لا من البايتات أو العناقيد الكتابية أو عرض "
     "المحارف على الشاشة. حافظ على جميع المحارف كما هي. إذا كان width غير موجب فارفع ValueError حتى مع "
     "النص الفارغ؛ والنص الفارغ مع عرض موجب يعطي قائمة فارغة.\n"
     "مثال: chunk_text(\"abcde\", 2) تعيد [\"ab\", \"cd\", \"e\"].\n\n"
     "```python\n" + A03_STARTER + "```\n" + SINGLE_AR,
     {"chunks.py": '''def chunk_text(text, width):
    if width <= 0:
        raise ValueError("width must be positive")
    return [text[start:start + width] for start in range(0, len(text), width)]
'''},
     None,
     [case("chunks.chunk_text", ["abcde", 2], ["ab", "cd", "e"])],
     [case("chunks.chunk_text", ["", 3], []),
      case("chunks.chunk_text", ["abc", 3], ["abc"]),
      case("chunks.chunk_text", ["abc", 10], ["abc"]),
      case("chunks.chunk_text", ["abcdef", 3], ["abc", "def"]),
      case("chunks.chunk_text", ["سلام عليكم", 4],
           ["سلام", " علي", "كم"]),
      case("chunks.chunk_text", ["a", 1], ["a"]),
      case("chunks.chunk_text", ["abc", 0], raises="ValueError"),
      case("chunks.chunk_text", ["", 0], raises="ValueError"),
      case("chunks.chunk_text", ["abc", -2], raises="ValueError")],
     starter={"chunks.py": A03_STARTER})


def write(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def dump(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def tree_hash(entries: dict[str, str]) -> str:
    """One digest for a set of files: sha256 over 'name\\0sha256\\n' lines sorted by name."""
    joined = "".join(f"{name}\0{digest}\n" for name, digest in sorted(entries.items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def main() -> None:
    manifest = {"suite_id": "CODE-Q1", "fixture_revision": 1,
                "based_on": "research/coding-quality-v1.proposed.json at main 3701d34",
                "executable": False, "model_traffic_enabled": False,
                "generated_code_execution_enabled": False, "tasks": {}}
    for tid, t in TASKS.items():
        base = FIX / tid
        entry = {"family": t["family"], "prompt_language": t["prompt_language"],
                 "files": t["files"],
                 "required_callables": sorted({c["call"] for c in t["public"] + t["hidden"]}),
                 "n_public": len(t["public"]), "n_hidden": len(t["hidden"])}
        entry["prompt_sha256"] = write(base / "prompt.txt", t["prompt"])
        entry["public_tests_sha256"] = write(base / "public_tests.json", dump(t["public"]))
        entry["hidden_tests_sha256"] = write(base / "hidden_tests.json", dump(t["hidden"]))
        entry["reference_sha256"] = tree_hash(
            {name: write(base / "reference" / name, text) for name, text in t["reference"].items()})
        entry["starter_sha256"] = tree_hash(
            {name: write(base / "starter" / name, text) for name, text in t["starter"].items()}
        ) if t["starter"] else None
        # The decoy is a plausible wrong answer. For bugfix/edit tasks the starter is the decoy.
        decoy = t["decoy"] or t["starter"]
        entry["decoy_sha256"] = tree_hash(
            {name: write(base / "decoy" / name, text) for name, text in decoy.items()})
        manifest["tasks"][tid] = entry
    write(ROOT / "manifest.json", dump(manifest))
    print(f"wrote {len(TASKS)} tasks under {FIX}")


if __name__ == "__main__":
    main()
