#!/usr/bin/env python3
"""새로 모은 뉴스·행사를 data/news.json에 합친다.

- URL이 같은 항목은 새 것으로 덮어쓴다
- 뉴스는 최근 14일, 행사는 끝난 지 14일이 지나면 지운다
- 형식이 틀린 항목은 [버림]으로 알리고 넣지 않는다

사용: python3 scripts/merge_news.py --news /tmp/new.json --briefing /tmp/briefing.txt
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "news.json"
KST = timezone(timedelta(hours=9))

COUNTRIES = {"US", "CA", "GB", "DE", "FR", "CH", "EU", "IL", "JP", "CN", "KR", "SG", "AU",
             "BR", "AR", "PY", "UY", "BO"}
CATEGORIES = {"company", "policy", "investment", "event"}
IMPORTANCE = {"high", "medium", "low"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NEWS_DAYS = 14


def problem(n):
    for key in ("country", "category", "importance", "date", "title_ko", "summary_ko", "source", "url"):
        if not n.get(key):
            return f"{key} 없음"
    if n["country"] not in COUNTRIES:
        return f"알 수 없는 국가 {n['country']}"
    if n["category"] not in CATEGORIES:
        return f"알 수 없는 분류 {n['category']}"
    if n["importance"] not in IMPORTANCE:
        return f"알 수 없는 중요도 {n['importance']}"
    if not DATE_RE.match(n["date"]) or (n.get("date_end") and not DATE_RE.match(n["date_end"])):
        return "날짜 형식은 YYYY-MM-DD"
    if not re.match(r"^https?://", n["url"]):
        return "url은 http(s)로 시작"
    if len(n["title_ko"]) > 45:
        return "제목이 45자를 넘음"
    return None


def make_id(n, taken):
    base = ("ev-" if n["category"] == "event" else "") + f"{n['country']}-{n['date']}"
    i = 1
    while f"{base}-{i}" in taken:
        i += 1
    return f"{base}-{i}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--news", required=True, help="새 항목 JSON 배열 파일")
    ap.add_argument("--briefing", help="오늘의 브리핑 텍스트 파일 (2~3문장)")
    args = ap.parse_args()

    db = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"items": []}
    new = json.loads(Path(args.news).read_text(encoding="utf-8"))

    today = datetime.now(KST).date()
    cutoff = (today - timedelta(days=NEWS_DAYS - 1)).isoformat()

    by_url = {n["url"]: n for n in db.get("items", [])}
    added = 0
    for n in new:
        why = problem(n)
        if why:
            print(f"[버림] {why}: {n.get('title_ko') or n.get('url')}")
            continue
        n.pop("id", None)
        if n["url"] in by_url:
            n["id"] = by_url[n["url"]]["id"]
        else:
            added += 1
        n["collected_at"] = datetime.now(KST).isoformat(timespec="seconds")
        by_url[n["url"]] = n

    kept = []
    for n in by_url.values():
        if n["category"] == "event":
            if (n.get("date_end") or n["date"]) < cutoff:
                continue
        elif n["date"] < cutoff:
            continue
        kept.append(n)

    taken = {n["id"] for n in kept if n.get("id")}
    for n in kept:
        if not n.get("id"):
            n["id"] = make_id(n, taken)
            taken.add(n["id"])

    kept.sort(key=lambda n: n["date"], reverse=True)
    db["items"] = kept
    db["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if args.briefing:
        db["briefing_ko"] = Path(args.briefing).read_text(encoding="utf-8").strip()
        db["briefing_date"] = today.isoformat()

    DATA.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")

    counts = {}
    for n in kept:
        counts[n["country"]] = counts.get(n["country"], 0) + 1
    print(f"신규 {added}건 · 전체 {len(kept)}건")
    print(" ".join(f"{c}:{counts.get(c, 0)}" for c in sorted(COUNTRIES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
