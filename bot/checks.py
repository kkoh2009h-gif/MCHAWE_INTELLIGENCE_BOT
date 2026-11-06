import ipaddress
import re
import socket
from urllib.parse import urlparse

def clean_domain(value: str) -> str:
    value = value.strip().lower()
    if "://" in value:
        value = urlparse(value).hostname or ""
    value = value.rstrip(".")
    if not value or len(value) > 253 or not re.fullmatch(r"[a-z0-9.-]+", value):
        raise ValueError("صيغة الدومين غير صحيحة.")
    if ".." in value:
        raise ValueError("صيغة الدومين غير صحيحة.")
    return value

def check_domain(value: str) -> str:
    domain = clean_domain(value)
    lines = [f"🌐 نتيجة فحص الدومين: {domain}"]
    try:
        infos = socket.getaddrinfo(domain, None)
        ips = sorted({item[4][0] for item in infos})
        lines.append("📡 عناوين IP:")
        lines.extend(f"• {ip}" for ip in ips[:10])
    except socket.gaierror:
        lines.append("⚠️ لم يتم العثور على عنوان DNS.")
    lines.append("\nملاحظة: هذا فحص تقني أساسي، وليس حكماً على موثوقية الموقع.")
    return "\n".join(lines)

def check_ip(value: str) -> str:
    try:
        ip = ipaddress.ip_address(value.strip())
    except ValueError:
        raise ValueError("عنوان IP غير صحيح.")
    if not ip.is_global:
        return "⛔ لأسباب الخصوصية والأمان، نفحص عناوين IP العامة فقط."
    try:
        host = socket.gethostbyaddr(str(ip))[0]
    except (socket.herror, socket.gaierror):
        host = "غير متوفر"
    return (f"📡 فحص عنوان IP\nالعنوان: {ip}\nالإصدار: IPv{ip.version}\n"
            f"عكس DNS: {host}\nعام: نعم\n\n"
            "لا يتم استنتاج عنوان السكن أو هوية صاحب الاتصال.")

def check_email(value: str) -> str:
    email = value.strip()
    pattern = r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    if len(email) > 254 or not re.fullmatch(pattern, email):
        return "❌ صيغة البريد غير صحيحة."
    domain = email.rsplit("@", 1)[1].lower()
    lines = [f"📧 فحص البريد: {email}", "✅ الصيغة تبدو صحيحة.", f"النطاق: {domain}"]
    try:
        socket.getaddrinfo(domain, 25, type=socket.SOCK_STREAM)
        lines.append("✅ النطاق لديه عنوان DNS يمكن الوصول إليه.")
    except socket.gaierror:
        lines.append("⚠️ لم نتمكن من حلّ نطاق البريد عبر DNS.")
    lines.append("تنبيه: لا يؤكد هذا أن صندوق البريد موجود أو أن صاحبه هو شخص معين.")
    return "\n".join(lines)

def check_phone(value: str) -> str:
    raw = value.strip()
    if not re.fullmatch(r"\+?[0-9][0-9\s().-]{5,22}", raw):
        return "❌ صيغة الرقم غير صحيحة. استخدم الصيغة الدولية مثل +9647XXXXXXXXX"
    digits = re.sub(r"\D", "", raw)
    if len(digits) < 7 or len(digits) > 15:
        return "❌ طول الرقم خارج النطاق المعتاد."
    return ("📱 تحليل الرقم\n"
            f"المدخل: {raw}\nعدد الأرقام: {len(digits)}\n"
            f"صيغة دولية: {'نعم' if raw.startswith('+') else 'لا'}\n\n"
            "هذا تحليل تنسيق فقط؛ لا يحدد اسم المالك أو عنوانه أو حساباته.")
