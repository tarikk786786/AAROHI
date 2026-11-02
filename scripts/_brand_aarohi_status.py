"""Replace user-visible Javis status strings with Aarohi. Internal javis_* untouched."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "server" / "main.py",
    ROOT / "dashboard" / "chat-lenh.js",
    ROOT / "dashboard" / "sw.js",
    ROOT / "server" / "dashboard" / "chat-lenh.js",
    ROOT / "server" / "dashboard" / "sw.js",
]

# Exact user-facing pairs only (do not touch tool names / comments indiscriminately).
REPL = [
    ('"Javis is thinking..."', '"Aarohi is thinking..."'),
    ('"Javis đang suy nghĩ..."', '"Aarohi đang suy nghĩ..."'),
    ('"Javis is double-checking what it just heard..."', '"Aarohi is double-checking what she just heard..."'),
    ('"Javis đang kiểm tra lại câu vừa nghe..."', '"Aarohi đang kiểm tra lại câu vừa nghe..."'),
    ('"Javis is answering quickly..."', '"Aarohi is answering quickly..."'),
    ('"Javis đang trả lời nhanh..."', '"Aarohi đang trả lời nhanh..."'),
    ('"Javis set a goal from this request."', '"Aarohi set a goal from this request."'),
    ('"Javis đã lập mục tiêu từ việc này."', '"Aarohi đã lập mục tiêu từ việc này."'),
    ('"Javis updated its understanding of the goal."', '"Aarohi updated her understanding of the goal."'),
    ('"Javis đã cập nhật cách hiểu mục tiêu."', '"Aarohi đã cập nhật cách hiểu mục tiêu."'),
    ('"A conversation shared from Javis OS"', '"A conversation shared from AAROHI"'),
    ('"Đoạn hội thoại được chia sẻ từ Javis OS"', '"Đoạn hội thoại được chia sẻ từ AAROHI"'),
    ('" · shared from Javis OS"', '" · shared from AAROHI"'),
    ('" · được chia sẻ từ Javis OS"', '" · được chia sẻ từ AAROHI"'),
    ('"You have a new message in Javis."', '"You have a new message in AAROHI."'),
    ('"Bạn có tin mới trong Javis."', '"Bạn có tin mới trong AAROHI."'),
    ('"Javis trả lời chat này như thường."', '"Aarohi trả lời chat này như thường."'),
    ('"Answering this chat: Javis."', '"Answering this chat: Aarohi."'),
    ('"Đang trả lời chat này: Javis."', '"Đang trả lời chat này: Aarohi."'),
    ('title, body = "Javis",', 'title, body = "AAROHI",'),
    ('"Javis", localefmt.chu("Thông báo đẩy đã chạy.', '"AAROHI", localefmt.chu("Thông báo đẩy đã chạy.'),
    ('const title = d.title || "Javis";', 'const title = d.title || "AAROHI";'),
    ('"Javis")', '"Aarohi")'),  # chat-lenh export headers - careful
]


def main() -> None:
    for path in FILES:
        if not path.exists():
            print("skip missing", path)
            continue
        t = path.read_text(encoding="utf-8")
        orig = t
        # File-specific safer replacements for chat-lenh
        if path.name == "chat-lenh.js":
            t = t.replace('| "Javis")', '| "Aarohi")')
            t = t.replace(': "Javis")', ': "Aarohi")')
            t = t.replace('|| "Javis")', '|| "Aarohi")')
            t = t.replace('(nguoi ? tw("lenh.ex_you") : "Javis")', '(nguoi ? tw("lenh.ex_you") : "Aarohi")')
        for a, b in REPL:
            if path.name == "chat-lenh.js" and a == '"Javis")':
                continue
            t = t.replace(a, b)
        if t != orig:
            path.write_text(t, encoding="utf-8")
            print("updated", path.relative_to(ROOT))
        else:
            print("no change", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
