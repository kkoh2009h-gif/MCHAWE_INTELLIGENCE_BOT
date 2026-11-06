# MCHAWE INTELLIGENCE BOT

بوت تيليجرام عربي لفحوصات OSINT التقنية الأساسية من مصادر عامة، مع مراعاة الخصوصية.

## الميزات
- فحص DNS الأساسي للدومينات.
- فحص عناوين IP العامة مع Reverse DNS.
- التحقق الشكلي من البريد ونطاقه.
- تحليل تنسيق رقم الهاتف دون تحديد هوية صاحبه.
- قائمة أوامر عربية ولوحة مشرف بسيطة.

## التشغيل على Termux
```bash
pkg update -y && pkg upgrade -y
pkg install python git -y
git clone https://github.com/kkoh2009h-gif/MCHAWE_INTELLIGENCE_BOT.git
cd MCHAWE_INTELLIGENCE_BOT
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python main.py
```

ضع توكن BotFather في BOT_TOKEN ومعرّف Telegram الخاص بك في ADMIN_IDS. لا ترفع ملف .env إلى GitHub أبداً.

## الأوامر
- /start و /help
- /domain example.com
- /ip 1.1.1.1
- /email name@example.com
- /phone +9647XXXXXXXXX
- /stats للمشرف

## الخصوصية
لا يبحث المشروع عن مالكي أرقام الهواتف أو البريد، ولا يستعمل قواعد بيانات مسرّبة، ولا ينفذ تعرّفاً على الوجوه أو تتبعاً للأشخاص.
