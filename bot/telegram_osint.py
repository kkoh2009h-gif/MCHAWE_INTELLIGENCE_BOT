import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "meta":
            return
        data = dict(attrs)
        key = (data.get("property") or data.get("name") or "").lower()
        value = data.get("content", "").strip()
        if key and value:
            self.meta[key] = value

def lookup_public_telegram(value: str) -> str:
    username = value.strip().lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9_]{5,32}", username):
        return "❌ اليوزر غير صحيح. أرسل مثلاً: /tg username"
    url = f"https://t.me/s/{username}"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; MCHAWE-OSINT/1.0)"})
    try:
        with urlopen(request, timeout=12) as response:
            html = response.read(1_500_000).decode("utf-8", errors="replace")
    except HTTPError as exc:
        if exc.code == 404:
            return ("🔎 لم أجد معاينة عامة لهذا اليوزر. قد يكون حساباً شخصياً أو قناة خاصة "
                    "أو أن المعاينة العامة غير متاحة.")
        return f"⚠️ تعذر جلب الصفحة العامة (HTTP {exc.code})."
    except (URLError, TimeoutError, OSError):
        return "⚠️ تعذر الاتصال بصفحة تيليجرام العامة. حاول لاحقاً."

    parser = MetaParser()
    parser.feed(html)
    title = parser.meta.get("og:title", "")
    description = parser.meta.get("og:description", "")
    image = parser.meta.get("og:image", "")
    if not title and not description:
        return ("🔎 لم تتوفر بيانات عامة قابلة للقراءة لهذا اليوزر. "
                "تيليجرام لا يتيح للبوت معرفة رقم الهاتف المخفي أو بيانات الحساب الخاصة.")
    lines = [
        "🕵️ MCHAWE TELEGRAM OSINT",
        f"🔗 اليوزر: @{username}",
        f"👤 الاسم/العنوان العام: {title or 'غير متاح'}",
        f"📝 الوصف العام: {description or 'غير متاح'}",
        f"🖼 صورة عامة: {image or 'غير متاحة'}",
        "📞 رقم الهاتف: غير متاح عبر المعاينة العامة",
        f"🌐 المصدر: {url}",
        "",
        "ℹ️ هذه معاينة للمحتوى العام فقط؛ لا تثبت هوية صاحب الحساب ولا تكشف البيانات الخاصة."
    ]
    return "\n".join(lines)
