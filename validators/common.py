from pathlib import Path
import json

P0 = "P0"
P1 = "P1"
P2 = "P2"

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def fail(severity, code, message, path=None):
    return {"severity": severity, "code": code, "message": message, "path": str(path) if path else None}

def print_report(items):
    if not items:
        print("PASS")
        return 0
    order = {P0: 0, P1: 1, P2: 2}
    for item in sorted(items, key=lambda x: order.get(x["severity"], 9)):
        loc = f" [{item['path']}]" if item.get("path") else ""
        print(f"{item['severity']} {item['code']}{loc}: {item['message']}")
    return 2 if any(i["severity"] == P0 for i in items) else 1
