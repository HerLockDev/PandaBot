import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from GroupMenter import DRAGONS, dispatcher
from GroupMenter.modules.disable import DisableAbleCommandHandler
from GroupMenter.modules.helper_funcs.chat_status import (
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
    ADMIN_CACHE,
)
from GroupMenter.helper_extra.admin_rights import (
    user_can_pin,
    user_can_promote,
    user_can_changeinfo,
)

from GroupMenter.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from GroupMenter.modules.log_channel import loggable
from GroupMenter.modules.helper_funcs.alternate import send_message
from GroupMenter.modules.helper_funcs.alternate import typing_action


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("Bunu yapmak için gerekli haklara sahip değilsiniz!")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "Bir kullanıcıya atıfta bulunmuyor gibisiniz veya belirtilen kimlik yanlış.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "administrator" or user_member.status == "creator":
        message.reply_text("Zaten yönetici olan birini nasıl terfi ettirebilirim?")
        return

    if user_id == bot.id:
        message.reply_text("Kendimi terfi ettiremiyorum! Bunu benim için yapması için bir yönetici bul.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("Grupta olmayan birini terfi ettiremem.")
        else:
            message.reply_text("Tanıtım yapılırken bir hata oluştu.")
        return

    bot.sendMessage(
        chat.id,
        f"<b>{user_member.user.first_name or user_id}</b> başarıyla yükseltildi!",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Kullanıcı:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Bir kullanıcıya atıfta bulunmuyor gibisiniz veya belirtilen kimlik yanlış.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creator":
        message.reply_text("Bu kişi sohbeti OLUŞTURDU, onların sıralamasını nasıl düşürürüm?")
        return

    if not user_member.status == "administrator":
        message.reply_text("Terfi edilmeyen şeyin derecesi düşürülemez!")
        return

    if user_id == bot.id:
        message.reply_text("Kendimi küçültemem! Bunu benim için yapacak bir yönetici bulun.")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
        )

        bot.sendMessage(
            chat.id,
            f"<b>{user_member.user.first_name or user_id}</b> başarıyla düşürüldü!",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTE\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Kullanıcı:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "İndirilemedi. Yönetici olmayabilirim veya yönetici statüsü başka biri tarafından atanmış olabilir"
            " kullanıcı, bu yüzden onlara göre hareket edemem!"
        )
        return


@run_async
@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("Yönetici önbelleği yenilendi!")


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "Bir kullanıcıya atıfta bulunmuyor gibisiniz veya belirtilen kimlik yanlış.."
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "Bu kişi sohbeti OLUŞTURDU, ona nasıl özel başlık ayarlayabilirim?"
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "Yönetici olmayanlar için başlık ayarlanamıyor!\nÖzel başlık ayarlamak için önce onları tanıtın!"
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "Kendi başlığımı kendim belirleyemem! Beni yönetici yapanı benim için yapsın."
        )
        return

    if not title:
        message.reply_text("Boş başlık ayarlamak hiçbir şey yapmaz!")
        return

    if len(title) > 16:
        message.reply_text(
            "Başlık uzunluğu 16 karakterden uzun.\n16 karaktere kısaltılıyor."
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text("Terfi etmediğim yöneticiler için özel başlık belirleyemiyorum!")
        return

    bot.sendMessage(
        chat.id,
        f"<code>{user_member.user.first_name or user_id}</code> için başlık başarıyla ayarlandı "
        f"<code>{html.escape(title[:16])}</code>'a!",
        parse_mode=ParseMode.HTML,
    )


@run_async
@bot_admin
@user_admin
@typing_action
def setchatpic(update, context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("Grup bilgilerini değiştirme hakkınız yok!")
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("Bazı fotoğrafları yalnızca sohbet resmi olarak ayarlayabilirsiniz!")
            return
        dlmsg = msg.reply_text("Sadece bir saniye...")
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                msg.reply_text("Yeni sohbet resmi başarıyla ayarlandı!")
        except BadRequest as excp:
            msg.reply_text(f"HATA! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("Yeni sohbet resmi ayarlamak için bir fotoğrafa veya dosyaya yanıt verin!")


@run_async
@bot_admin
@user_admin
@typing_action
def rmchatpic(update, context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("Grup fotoğrafını silmek için yeterli hakkınız yok")
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text("Sohbetin profil fotoğrafı başarıyla silindi!")
    except BadRequest as excp:
        msg.reply_text(f"HATA! {excp.message}.")
        return


@run_async
@bot_admin
@user_admin
@typing_action
def setchat_title(update, context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("Sohbet bilgilerini değiştirmek için yeterli hakkınız yok!")
        return

    title = " ".join(args)
    if not title:
        msg.reply_text("Sohbetinizde yeni başlık belirlemek için bir metin girin!")
        return

    try:
        context.bot.set_chat_title(int(chat.id), str(title))
        msg.reply_text(
            f"<b>{title}</b> başarıyla yeni sohbet başlığı olarak ayarlandı!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"HATA! {excp.message}.")
        return


@run_async
@bot_admin
@user_admin
@typing_action
def set_sticker(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("Sohbet bilgilerini değiştirme haklarınız yok!")

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(
                "Sohbet çıkartma setini ayarlamak için bazı çıkartmalara cevap vermeniz gerekiyor!"
            )
        stkr = msg.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stkr)
            msg.reply_text(
                f"{chat.title}'da başarıyla yeni grup çıkartmaları ayarlayın!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "Üzgünüz, Telegram kısıtlamaları nedeniyle, grup çıkartmalarına sahip olabilmeleri için sohbetin en az 100 üyeye sahip olması gerekiyor!"
                )
            msg.reply_text(f"HATA! {excp.message}.")
    else:
        msg.reply_text(
            "Sohbet çıkartma setini ayarlamak için bazı çıkartmaları yanıtlamanız gerekiyor!")


@run_async
@bot_admin
@user_admin
@typing_action
def set_desc(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("Sohbet bilgilerini değiştirme hakkınız yok!")

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text("Boş açıklama ayarlamak hiçbir şey yapmaz!")
    try:
        if len(desc) > 255:
            return msg.reply_text(
                "Açıklama 255 karakterin altında olmalıdır!")
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(
            f"{chat.title} sohbet açıklaması başarıyla güncellendi!")
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")


def __chat_settings__(chat_id, user_id):
    return "Siz *yöneticisiniz*: `{}`".format(
        dispatcher.bot.get_chat_member(chat_id, user_id).status
        in ("administrator", "creator")
    )


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    user = update.effective_user
    chat = update.effective_chat

    is_group = chat.type != "private" and chat.type != "channel"
    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (
            args[0].lower() == "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#PIN\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNPIN\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@run_async
@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "Davet bağlantısına erişimim yok, izinlerimi değiştirmeyi deneyin!"
            )
    else:
        update.effective_message.reply_text(
            "Size sadece süper gruplar ve kanallar için davet linkleri verebilirim, üzgünüm!"
        )


@run_async
@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    args = context.args
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message, "Bu komut yalnızca Gruplarda çalışır.")
        return

    chat = update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title

    try:
        msg = update.effective_message.reply_text(
            "Grup yöneticileri getiriliyor...", parse_mode=ParseMode.HTML
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "Grup yöneticileri getiriliyor...", quote=False, parse_mode=ParseMode.HTML
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "<b>{}</b> içindeki yöneticiler:".format(html.escape(update.effective_chat.title))

    bot_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Silinen Hesaplar"
        else:
            name = "{}".format(
                mention_html(
                    user.id, html.escape(user.first_name + " " + (user.last_name or ""))
                )
            )

        if user.is_bot:
            bot_admin_list.append(name)
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 👑 Yaratıcı:"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n🔱 Adminler:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Silinen Hesaplar"
        else:
            name = "{}".format(
                mention_html(
                    user.id, html.escape(user.first_name + " " + (user.last_name or ""))
                )
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0], html.escape(admin_group)
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🚨 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    text += "\n🤖 Botlar:"
    for each_bot in bot_admin_list:
        text += "\n<code> • </code>{}".format(each_bot)

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


__help__ = """
❍ /admins*:* sohbetteki yöneticilerin listesi

*Yalnızca yöneticiler:*
  ❍ /pin*:* yanıtlanan mesajı sessizce sabitler - kullanıcılara bildirim vermek için "yüksek sesle" veya "bildir" ekleyin
  ❍ /unpin*:* şu anda sabitlenmiş mesajın sabitlemesini kaldırır
  ❍ /invitelink*:* davet bağlantısını alır
  ❍ /promote*:* kullanıcıyı tanıtır
  ❍ /demote*:* kullanıcıyı indirger
  ❍ /title <buraya başlık>*:* botun terfi ettirdiği bir yönetici için özel bir başlık ayarlar
  ❍ /admincache*:* adminler listesini yenilemeye zorla
  ❍ /antispam <on/off/yes/no>*:* Antispam teknolojimizi değiştirir veya mevcut ayarlarınızı döndürür.

*Not:* Gece Modu sohbetleri saat 12'de (IST) Otomatik olarak kapanır
ve Gece İstenmeyen Postaları Önlemek için sabah 6'da (IST) Otomatik olarak açılır.

"""

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote)

SET_TITLE_HANDLER = CommandHandler("title", set_title)
ADMIN_REFRESH_HANDLER = CommandHandler(
    "admincache", refresh_admin, filters=Filters.group
)

CHAT_PIC_HANDLER = CommandHandler("setgpic", setchatpic, filters=Filters.group)
DEL_CHAT_PIC_HANDLER = CommandHandler(
    "delgpic", rmchatpic, filters=Filters.group)
SETCHAT_TITLE_HANDLER = CommandHandler(
    "setgtitle", setchat_title, filters=Filters.group
)
SETSTICKET_HANDLER = CommandHandler(
    "setsticker", set_sticker, filters=Filters.group)
SETDESC_HANDLER = CommandHandler(
    "setdescription",
    set_desc,
    filters=Filters.group)

dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)
dispatcher.add_handler(CHAT_PIC_HANDLER)
dispatcher.add_handler(DEL_CHAT_PIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(SETSTICKET_HANDLER)
dispatcher.add_handler(SETDESC_HANDLER)

__mod_name__ = "ADMIN"
__command_list__ = [
    "adminlist",
    "admins",
    "invitelink",
    "promote",
    "demote",
    "admincache",
]
__handlers__ = [
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
