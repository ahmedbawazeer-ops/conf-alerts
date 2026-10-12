# -*- coding: utf-8 -*-
"""
إعدادات النظام — عدّل هذا الملف فقط لتغيير المصادر أو الكلمات المفتاحية.
"""

# ---------------------------------------------------------------
# 1) المصادر: روابط RSS لمواقع تجمع الفرص (كلها مجانية ولا تحتاج حساب)
#    لو موقع توقف أو تغير رابطه، النظام يتخطاه ويكمل بالباقي.
# ---------------------------------------------------------------
FEEDS = [
    # Opportunity Desk — قسم المؤتمرات + التدريب
    "https://opportunitydesk.org/category/conferences/feed/",
    "https://opportunitydesk.org/category/training/feed/",
    # Opportunities for Youth
    "https://opportunitiesforyouth.org/category/conferences/feed/",
    "https://opportunitiesforyouth.org/feed/",
    # Opportunities Corners
    "https://opportunitiescorners.com/category/conferences/feed/",
    # After School Africa
    "https://www.afterschoolafrica.com/category/conferences/feed/",
    # Youth Opportunities Hub / Opportunities Circle
    "https://www.opportunitiescircle.com/category/conferences/feed/",
    "https://youthopportunitieshub.com/feed/",
    # Scholarship Positions (فيه مؤتمرات أحياناً)
    "https://scholarship-positions.com/category/conferences/feed/",
]

# ---------------------------------------------------------------
# 2) لازم يكون المنشور "فعالية" (مؤتمر / قمة / منتدى / نموذج محاكاة ...)
# ---------------------------------------------------------------
EVENT_KEYWORDS = [
    "conference", "summit", "forum", "symposium", "congress", "convention",
    "model united nations", "mun", "youth assembly", "assembly", "dialogue",
    "workshop", "seminar", "summer school", "winter school", "academy", "bootcamp", "festival",
    "exchange program", "delegation", "roundtable", "parliament",
]

# ---------------------------------------------------------------
# 3) كلمات تدل على وجود رسوم → المنشور يُستبعد
# ---------------------------------------------------------------
FEE_KEYWORDS = [
    "application fee", "registration fee", "participation fee",
    "conference fee", "delegate fee", "program fee", "programme fee",
    "non-refundable fee", "fee of $", "fee of €", "fee of usd", "fee of eur",
    "processing fee", "tuition fee", "self-funded", "self funded",
    "partially funded", "fees apply", "pay a fee", "payment of",
]

# كلمات تدل صراحة على أنه مجاني → تنفي كلمات الرسوم لو وُجدت معاً
FREE_KEYWORDS = [
    "no application fee", "free of charge", "free to apply", "free registration",
    "no registration fee", "no participation fee", "fully funded", "fully-funded",
    "free of cost", "no fee", "free participation", "free conference",
]

# ---------------------------------------------------------------
# (الكلمة المنتهية بـ * تعني "تبدأ بـ": legislat* = legislation, legislative...)
# 4) كلمات مرتبطة بالعلوم السياسية → الفرصة تأخذ ⭐ وتظهر أولاً
# ---------------------------------------------------------------
POLITICS_KEYWORDS = [
    "political", "politics", "policy", "public policy", "diplomacy", "diplomat",
    "international relations", "governance", "democracy", "democratic",
    "election", "human rights", "peace", "security", "conflict", "united nations",
    "un", "unesco", "unicef", "undp", "osce", "nato", "european union", "eu",
    "african union", "arab league", "parliament", "legislat*", "foreign affairs",
    "geopolitic*", "global affairs", "civic", "advocacy", "leadership",
    "sustainable development", "sdg", "climate policy", "migration", "refugee",
    "law", "justice", "middle east", "mena", "model united nations", "mun",
    "think tank", "public administration", "economics", "development",
]

# كم يوم للخلف نقبل منشورات (حتى لا تصلك فرص قديمة أول مرة)
MAX_AGE_DAYS = 21

# أقصى عدد فرص في الرسالة الواحدة يومياً
MAX_ITEMS_PER_RUN = 15

# لو True: يرسل فقط الفرص المرتبطة بالسياسة (⭐). لو False: يرسل كل المؤتمرات المجانية.
ONLY_POLITICS = False
