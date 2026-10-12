# -*- coding: utf-8 -*-
"""
نظام تنبيهات المؤتمرات المجانية → واتساب
يقرأ مواقع الفرص (RSS)، يفلتر المؤتمرات بدون رسوم، ويرسلها عبر CallMeBot.
"""
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import feedparser
import requests

import config

SEEN_FILE = "seen.json"
UA = {"User-Agent": "Mozilla/5.0 (conf-alerts student project)"}


# ------------------------------------------------------------------ helpers
def _pattern(kw):
    kw = kw.strip().lower()
    if kw.endswith("*"):
        return r"\b" + re.escape(kw[:-1])
    return r"\b" + re.escape(kw) + r"\b"


def compile_list(words):
    return re.compile("|".join(_pattern(w) for w in words), re.IGNORECASE)


EVENT_RE = compile_list(config.EVENT_KEYWORDS)
FEE_RE = compile_list(config.FEE_KEYWORDS)
FREE_RE = compile_list(config.FREE_KEYWORDS)
POL_RE = compile_list(config.POLITICS_KEYWORDS)
DEADLINE_RE = re.compile(
    r"deadline[^.:\n]{0,20}[:\-–]?\s*([A-Z]?[a-z]*\.?\s*\d{1,2}(?:st|nd|rd|th)?,?\s*[A-Za-z]*\.?\s*,?\s*\d{4}"
    r"|[A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{4}|\d{1,2}(?:st|nd|rd|th)?\s+[A-Z][a-z]+,?\s*\d{4})",
    re.IGNORECASE,
)


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(seen):
    # نحتفظ بآخر 3000 رابط فقط حتى لا يكبر الملف
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen)[-3000:], f, ensure_ascii=False, indent=0)


# ------------------------------------------------------------------ fetch
def fetch_feed(url):
    try:
        r = requests.get(url, headers=UA, timeout=25)
        r.raise_for_status()
        return feedparser.parse(r.content).entries
    except Exception as e:  # موقع واقف؟ نكمل بالباقي
        print(f"  ⚠️  تعذّر جلب {url}: {e}")
        return []


def entry_text(e):
    parts = [e.get("title", ""), e.get("summary", "")]
    for c in e.get("content", []) or []:
        parts.append(c.get("value", ""))
    return clean(" ".join(parts))


def entry_date(e):
    t = e.get("published_parsed") or e.get("updated_parsed")
    return datetime(*t[:6], tzinfo=timezone.utc) if t else None


# ------------------------------------------------------------------ filter
def classify(title, text):
    """يرجع (مقبول؟, مرتبط بالسياسة؟, سبب الرفض)"""
    blob = f"{title} {text}"
    if not EVENT_RE.search(blob):
        return False, False, "ليست فعالية"
    has_fee = bool(FEE_RE.search(blob))
    says_free = bool(FREE_RE.search(blob))
    if has_fee and not says_free:
        return False, False, "فيها رسوم"
    politics = bool(POL_RE.search(blob))
    if config.ONLY_POLITICS and not politics:
        return False, False, "ليست سياسية"
    return True, politics, ""


def find_deadline(text):
    m = DEADLINE_RE.search(text)
    return m.group(1).strip(" ,.") if m else None


def collect():
    seen = load_seen()
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.MAX_AGE_DAYS)
    picked, stats = {}, {"total": 0, "rejected": 0}

    for url in config.FEEDS:
        entries = fetch_feed(url)
        print(f"📥 {len(entries):3d} منشور من {url}")
        for e in entries:
            link = (e.get("link") or "").split("?")[0]
            if not link or link in seen or link in picked:
                continue
            d = entry_date(e)
            if d and d < cutoff:
                continue
            stats["total"] += 1
            title = clean(e.get("title", ""))
            text = entry_text(e)
            ok, politics, why = classify(title, text)
            if not ok:
                stats["rejected"] += 1
                seen.add(link)  # لا نعيد فحصه
                continue
            picked[link] = {
                "title": title,
                "link": link,
                "politics": politics,
                "free_explicit": bool(FREE_RE.search(text)),
                "deadline": find_deadline(text),
                "date": d.isoformat() if d else "",
            }

    items = sorted(
        picked.values(),
        key=lambda x: (not x["politics"], not x["free_explicit"], x["date"]),
    )
    items = items[: config.MAX_ITEMS_PER_RUN]
    print(f"✅ مقبول: {len(items)} | مرفوض: {stats['rejected']} | تم فحص: {stats['total']}")
    return items, seen


# ------------------------------------------------------------------ format & send
def format_messages(items, limit=1400):
    today = datetime.now().strftime("%Y-%m-%d")
    header = f"🌍 *مؤتمرات وفعاليات مجانية* — {today}\n({len(items)} فرصة جديدة)\n"
    blocks = []
    for i, it in enumerate(items, 1):
        tags = []
        if it["politics"]:
            tags.append("⭐ سياسة")
        if it["free_explicit"]:
            tags.append("💸 مجاني صراحةً")
        line = f"\n{i}. *{it['title']}*"
        if tags:
            line += f"\n   {' | '.join(tags)}"
        if it["deadline"]:
            line += f"\n   ⏰ آخر موعد: {it['deadline']}"
        line += f"\n   🔗 {it['link']}\n"
        blocks.append(line)

    msgs, cur = [], header
    for b in blocks:
        if len(cur) + len(b) > limit:
            msgs.append(cur)
            cur = ""
        cur += b
    if cur.strip():
        msgs.append(cur)
    if msgs:
        msgs[-1] += "\n⚠️ تأكد من صفحة الفرصة أنه لا توجد رسوم قبل التقديم."
    return msgs


def send_whatsapp(text):
    phone = os.environ.get("WHATSAPP_PHONE", "").strip().lstrip("+")
    key = os.environ.get("CALLMEBOT_APIKEY", "").strip()
    if not phone or not key:
        print("—— (وضع تجربة: لا يوجد رقم/مفتاح، الرسالة تُطبع فقط) ——\n" + text)
        return True
    url = (
        "https://api.callmebot.com/whatsapp.php"
        f"?phone={phone}&text={quote(text)}&apikey={key}"
    )
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=40)
            if r.ok and "error" not in r.text.lower()[:300]:
                return True
            print(f"  ⚠️ رد CallMeBot: {r.status_code} {r.text[:200]}")
        except Exception as e:
            print(f"  ⚠️ خطأ في الإرسال: {e}")
        time.sleep(10 * (attempt + 1))
    return False


def main():
    items, seen = collect()
    if not items:
        print("لا توجد فرص جديدة اليوم.")
        if os.environ.get("NOTIFY_EMPTY") == "1":
            send_whatsapp("🌍 لا توجد مؤتمرات مجانية جديدة اليوم.")
        save_seen(seen)
        return 0

    ok = True
    for m in format_messages(items):
        ok &= send_whatsapp(m)
        time.sleep(5)  # CallMeBot يحتاج مهلة بين الرسائل

    if ok:  # نحفظ فقط لو وصلت الرسائل، حتى لا تضيع فرص
        for it in items:
            seen.add(it["link"])
        save_seen(seen)
        return 0
    print("❌ فشل الإرسال — سيُعاد المحاولة في التشغيل القادم.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
