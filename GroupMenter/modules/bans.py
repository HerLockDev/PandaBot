import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from GroupMenter import (
    DEV_USERS,
    LOGGER,
    OWNER_ID,
    DRAGONS,
    DEMONS,
    TIGERS,
    WOLVES,
    dispatcher,
)
from GroupMenter.modules.disable import DisableAbleCommandHandler
from GroupMenter.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
    can_delete,
)
from GroupMenter.modules.helper_funcs.extraction import extract_user_and_text
from GroupMenter.modules.helper_funcs.string_handling import extract_time
from GroupMenter.modules.log_channel import gloggable, loggable


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bu kullanıcı DATABASE'im de yok. O kişinin bir mesajını iletip tekrar dene.")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Kullanıcı bulunamadı":
            raise
        message.reply_text("Bu kişiyi bulamıyor gibi görünüyor.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Oh evet, kendimi yasaklayım, noob!")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("Beni Tanrı seviyesinde bir felakete karşı koymaya çalışıyorsun ha?")
        elif user_id in DEV_USERS:
            message.reply_text("Kendimize karşı hareket edemem.")
        elif user_id in DRAGONS:
            message.reply_text(
                "Bu Ejderhayla burada savaşmak sivillerin hayatını riske atacak."
            )
        elif user_id in DEMONS:
            message.reply_text(
                "Bir İblis felaketiyle savaşmak için Kahramanlar birliğinden bir emir getir."
            )
        elif user_id in TIGERS:
            message.reply_text(
                "Tiger felaketiyle savaşmak için Kahramanlar derneğinden bir emir getir."
            )
        elif user_id in WOLVES:
            message.reply_text("Kurt yetenekleri onları bağışıklığı yasaklar!")
        else:
            message.reply_text("Bu kullanıcının dokunulmazlığı var ve yasaklanamaz.")
        return log_message
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}BANLANDI\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>Kullanıcı:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>Sebep:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"<code>❕</code><b>Yasaklama Etkinliği</b>\n"
            f"<code> </code><b>•  User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  Reason:</b> \n{html.escape(reason)}"
        bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML, quote=False)
        return log

    except BadRequest as excp:
        if excp.message == "Yanıt mesajı bulunamadı":
            # Do not reply
            if silent:
                return log
            message.reply_text("Banlandı!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "%s nedeniyle %s (%s) sohbetinde %s kullanıcısı yasaklanırken HATA oluştu",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uhm...bu işe yaramadı...")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bunun bir kullanıcı olduğundan şüpheliyim.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Kullanıcı bulunamadı":
            raise
        message.reply_text("Bu kullanıcıyı bulamıyorum.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Kendimi banlamayacağım, deli misin?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("öyle hissetmiyorum.")
        return log_message

    if not reason:
        message.reply_text("Bu kullanıcıyı yasaklamak için bir zaman belirtmediniz!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "__#BAN BİR BAN OLAYI__\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>Kullanıcı:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Zaman:</b> {time_val}"
    )
    if reason:
        log += "\n<b>Sebep:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"Yasaklandı! Kullanıcı {mention_html(member.user.id, html.escape(member.user.first_name))} "
            f"{time_val} süreyle yasaklanacak.",
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Yanıt mesajı bulunamadı":
            # Do not reply
            message.reply_text(
                f"Yasaklandı! Kullanıcı {time_val} süreyle yasaklanacak.", quote=False
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "%s nedeniyle %s (%s) sohbetinde %s kullanıcısı yasaklanırken HATA oluştu",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Lanet olsun, o kullanıcıyı yasaklayamam.")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def punch(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bunun bir kullanıcı olduğundan şüpheliyim.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Kullanıcı bulunamadı":
            raise

        message.reply_text("Bu kullanıcıyı bulamıyorum.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Evet, bunu yapmayacağım.")
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text("Keşke bu kullanıcıyı yumruklayabilseydim....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"Bir Yumruk! {mention_html(member.user.id, html.escape(member.user.first_name))}.",
            parse_mode=ParseMode.HTML,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#ATILDI\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>Kullanıcı:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<Sebep:</b> {reason}"

        return log

    else:
        message.reply_text("Lanet olsun, o kullanıcıyı yumruklayamam.")

    return log_message


@run_async
@bot_admin
@can_restrict
def punchme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Keşke yapabilseydim... Ama sen bir adminsin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("*seni gruptan atar*")
    else:
        update.effective_message.reply_text("Ha? yapamam :/")


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bunun bir kullanıcı olduğundan şüpheliyim.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Kullanıcı bulunamadı":
            raise
        message.reply_text("Bu kullanıcıyı bulamıyorum.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Burada olmasam kendimi nasıl kaldırırdım...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("Bu kişi zaten burada değil mi???")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("Evet, bu kullanıcı katılabilir!")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBAN\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>Kullanıcı:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\<b>Sebep:</b> {reason}"

    return log


@run_async
@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Geçerli bir sohbet kimliği verin.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "Kullanıcı bulunamadı":
            message.reply_text("Bu kullanıcıyı bulamıyorum.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Sen zaten sohbette değilmisin??")
        return

    chat.unban_member(user.id)
    message.reply_text("Evet, seni engelledim.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBAN\n"
        f"<b>Kullanıcı:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


__help__ = """
❍ /punchme*:* komutu veren kullanıcıyı yumruklar
(**TUTAMAÇ, MESAJ İLETİSİ DEMEK.
*Yalnızca yöneticiler:*
  ❍ /ban <userhandle>*:* bir kullanıcıyı yasaklar. (tutamaç veya yanıt yoluyla)
  ❍ /sban <userhandle>*:* Bir kullanıcıyı sessizce yasaklar. Komutu, Cevaplanan mesajı siler ve cevap vermez. (tutamaç veya yanıt yoluyla)
  ❍ /tban <userhandle> x(m/h/d)*:* bir kullanıcıyı 'x' süresi boyunca yasaklar. (tanıtıcı veya yanıt yoluyla). "m" = "dakika", "h" = "saat", "d" = "günler".
  ❍ /unban <userhandle>*:* bir kullanıcının yasağını kaldırır. (tutamaç veya yanıt yoluyla)
  ❍ /punch <userhandle>*:* Bir kullanıcıyı gruptan çıkarır, (tutamaç veya yanıt yoluyla)
"""

BAN_HANDLER = CommandHandler(["ban", "sban"], ban)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban)
PUNCH_HANDLER = CommandHandler("punch", punch)
UNBAN_HANDLER = CommandHandler("unban", unban)
ROAR_HANDLER = CommandHandler("roar", selfunban)
PUNCHME_HANDLER = DisableAbleCommandHandler("punchme", punchme, filters=Filters.group)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(PUNCH_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(PUNCHME_HANDLER)

__mod_name__ = "BANS"
__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    PUNCH_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    PUNCHME_HANDLER,
]
