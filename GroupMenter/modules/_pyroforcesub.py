# credits @InukaAsith, @Mr_dark_prince

import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from GroupMenter import DRAGONS as SUDO_USERS
from GroupMenter import pbot
from GroupMenter.modules.sql_extended import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗ @{channel} kanalımıza katılın ve 'SESİMİ AÇ' düğmesine basın.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Başka bir nedenden dolayı yöneticiler tarafından sessize alındınız.",
                    show_alert=True,
                )
        else:
            if (
                not client.get_chat_member(chat_id, (client.get_me()).id).status
                == "administrator"
            ):
                client.send_message(
                    chat_id,
                    f"❗ **{cb.from_user.mention} kendi sesini açmaya çalışıyor ama bu sohbette yönetici olmadığım için sesini açamıyorum.**\n__#Bu sohbetten ayrılıyor...__",
                )

            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Uyarı! Konuşabilecekken düğmeye basmayın.",
                    show_alert=True,
                )


@pbot.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        if (
            not client.get_chat_member(chat_id, user_id).status
            in ("administrator", "creator")
            and not user_id in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        "Hoş geldiniz {} 🙏 \n **Henüz @{} Kanalımıza katılmadınız** 😭 \n \nLütfen [Kanalımıza](https://t.me/{}) katılın ve **SESİMİ AÇ** Butonuna basın. \n \n".format(
                            message.from_user.mention, channel, channel
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "Kanala Katılın",
                                        url="https://t.me/{}".format(channel),
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "SESİMİ AÇ", callback_data="onUnMuteRequest"
                                    )
                                ],
                            ]
                        ),
                    )
                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "❗ **Emilia burada yönetici değil..**\n__Bana yasaklama izinleri verin ve yeniden deneyin.. \n#FSub'ı Bitiriyor...__"
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"❗ **Ben @{channel} kanalının yöneticisi değilim.**\n__Bana o kanalın yöneticisini verin ve yeniden deneyin.\n#FSub'ı Bitiriyor...__",
                )


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **Zorla Abone Olma Başarıyla Devre Dışı Bırakıldı.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**Sesi kapattığım tüm üyelerin sesini açıyorum...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("✅ **Sesi benim tarafımdan kapatılan tüm üyelerin sesi açıldı.**")
                except ChatAdminRequired:
                    sent_message.edit(
                        "❗ **Bu sohbette yönetici değilim.**\n__Üyelerin sesini açamıyorum çünkü bu sohbette yönetici değilim, beni kullanıcı yasaklama izniyle yönetici yap.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **Zorla Abone Ol Etkin**\n__Zorla Abone Ol etkin, bu grupta mesaj gönderebilmek için tüm grup üyelerinin bu [kanala](https://t.me/{input_str}) abone olması gerekir.__",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"❗ **Kanalda Yönetici Değilim**\n__[Kanalda](https://t.me/{input_str}) yönetici değilim. ForceSubscribe'ı etkinleştirmek için beni yönetici olarak ekleyin.__",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text(f"❗ **Geçersiz Kanal Kullanıcı Adı.**")
                except Exception as err:
                    message.reply_text(f"❗ **HATA:** ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                message.reply_text(
                    f"✅ **Bu sohbette Abone olmaya Zorla etkinleştirildi.**\n__Bu [Kanal](https://t.me/{sql.fs_settings(chat_id).channel})__ için",
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text("❌ **Bu sohbette Abone olmaya Zorla devre dışı bırakıldı.**")
    else:
        message.reply_text(
            "❗ **Grup Oluşturucu Gerekli**\n__Bunu yapmak için grup oluşturucu olmanız gerekir.__ (GRUP SAHİBİ)"
        )


__help__ = """
*Abone olmaya zorla:*

❍ Kanalınıza abone olmayan üyeleri abone olana kadar sessize alabilirim
❍ Etkinleştirildiğinde, abone olmayan üyelerin sesini kapatacağım ve onlara bir sesi açma düğmesi göstereceğim. Düğmeye bastıklarında sesini açacağım

*Kurulum*
*Yalnızca yaratıcı*
❍ Beni grubunuza yönetici olarak ekleyin
❍ Beni kanalınıza yönetici olarak ekleyin
 
*Komutlar*
  ❍ /fsub {kanal kullanıcı adı} - Kanalı açmak ve kurmak için.
   💡Önce bunu yapın...
  ❍ /fsub - Mevcut ayarları almak için.
  ❍ /fsub devre dışı - ForceSubscribe'ı kapatmak için..
   💡fsub'u devre dışı bırakırsanız, çalışmak için tekrar ayarlamanız gerekir.. /fsub {kanal kullanıcı adı}
  ❍ /fsub clear - Benim tarafımdan sessize alınan tüm üyelerin sesini açmak için.
"""
__mod_name__ = "BUTON"
