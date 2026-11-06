import asyncio
import logging
import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

from bot.checks import check_domain, check_ip, check_email, check_phone
from bot.telegram_osint import lookup_public_telegram

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}
TG_COOLDOWN_SECONDS = 10

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", level=logging.INFO)
log = logging.getLogger("mchawe-bot")

WELCOME = ("🕵️ *MCHAWE INTELLIGENCE BOT*\n"
           "منصة عربية لفحص المعلومات التقنية المتاحة علناً وبطريقة قانونية.\n\n"
           "اختر خدمة من القائمة أو استخدم الأوامر.")

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔎 بحث Telegram OSINT", callback_data="tg_help")],
        [InlineKeyboardButton("🌐 فحص دومين", callback_data="domain_help"),
         InlineKeyboardButton("📡 فحص IP", callback_data="ip_help")],
        [InlineKeyboardButton("📧 فحص بريد", callback_data="email_help"),
         InlineKeyboardButton("📱 تحليل رقم", callback_data="phone_help")],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, parse_mode="Markdown", reply_markup=menu())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ("📚 *الأوامر المتاحة*\n\n"
           "`/tg username` — معاينة معلومات Telegram العامة\n"
           "`/domain example.com` — معلومات DNS والدومين\n"
           "`/ip 1.1.1.1` — معلومات IP عام فقط\n"
           "`/email name@example.com` — فحص الصيغة وسجلات البريد\n"
           "`/phone +9647XXXXXXXXX` — تحليل صيغة الرقم فقط\n"
           "`/stats` — إحصائيات للمشرف\n\n"
           "⚠️ لا يكشف البوت أرقام الهواتف المخفية أو البيانات الخاصة أو المسربة.")
    await update.message.reply_text(msg, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    texts = {
        "tg_help": "🔎 أرسل اليوزر بهذا الشكل: `/tg username`\nسنعرض فقط المعاينة والمعلومات العامة المتاحة.",
        "domain_help": "اكتب: `/domain example.com`",
        "ip_help": "اكتب: `/ip 1.1.1.1` — العناوين الخاصة والمحلية مرفوضة.",
        "email_help": "اكتب: `/email name@example.com`",
        "phone_help": "اكتب: `/phone +9647XXXXXXXXX` — تحليل تنسيق فقط.",
        "help": "استخدم /help لعرض جميع الأوامر."
    }
    await q.message.reply_text(texts.get(q.data, "استخدم /help."), parse_mode="Markdown")

async def tg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("طريقة الاستخدام: /tg username")
        return
    now = time.monotonic()
    last = context.user_data.get("last_tg_lookup", 0)
    remaining = TG_COOLDOWN_SECONDS - (now - last)
    if remaining > 0:
        await update.message.reply_text(f"⏳ انتظر {int(remaining) + 1} ثوانٍ قبل البحث التالي.")
        return
    context.user_data["last_tg_lookup"] = now
    username = context.args[0].strip()
    status = await update.message.reply_text("⏳ جارٍ البحث في المعاينات العامة...")
    try:
        result = await asyncio.to_thread(lookup_public_telegram, username)
        await status.edit_text(result, disable_web_page_preview=True)
    except Exception:
        log.exception("Telegram public lookup failed")
        await status.edit_text("تعذر إكمال البحث. حاول لاحقاً.")

async def run_check(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str):
    if not context.args:
        examples = {"domain": "/domain example.com", "ip": "/ip 1.1.1.1",
                    "email": "/email name@example.com", "phone": "/phone +9647XXXXXXXXX"}
        await update.message.reply_text(f"طريقة الاستخدام:\n{examples[kind]}")
        return
    value = " ".join(context.args).strip()
    await update.message.reply_text("⏳ جارٍ الفحص...")
    try:
        result = {"domain": check_domain, "ip": check_ip,
                  "email": check_email, "phone": check_phone}[kind](value)
        await update.message.reply_text(result)
    except Exception:
        log.exception("Check failed: %s", kind)
        await update.message.reply_text("تعذر إكمال الفحص. تأكد من المدخل وحاول لاحقاً.")

async def domain_cmd(update, context): await run_check(update, context, "domain")
async def ip_cmd(update, context): await run_check(update, context, "ip")
async def email_cmd(update, context): await run_check(update, context, "email")
async def phone_cmd(update, context): await run_check(update, context, "phone")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("هذا الأمر للمشرف فقط.")
        return
    await update.message.reply_text(
        f"🛡️ لوحة المشرف\nمعرّفك: `{update.effective_user.id}`\nالإصدار: 2.1.0\nالحالة: يعمل",
        parse_mode="Markdown")

async def post_init(app: Application):
    await app.bot.set_my_commands([
        ("start", "بدء تشغيل البوت"), ("help", "عرض المساعدة"),
        ("tg", "بحث في معلومات Telegram العامة"),
        ("domain", "فحص دومين"), ("ip", "فحص عنوان IP عام"),
        ("email", "فحص بريد إلكتروني"), ("phone", "تحليل صيغة رقم هاتف"),
        ("stats", "إحصائيات المشرف")])

def main():
    if not TOKEN:
        raise SystemExit("ضع BOT_TOKEN داخل متغير البيئة BOT_TOKEN أو ملف .env")
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    for name, handler in [("start", start), ("help", help_cmd), ("tg", tg_cmd),
                          ("domain", domain_cmd), ("ip", ip_cmd), ("email", email_cmd),
                          ("phone", phone_cmd), ("stats", stats_cmd)]:
        app.add_handler(CommandHandler(name, handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    log.info("MCHAWE INTELLIGENCE BOT started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
