from GroupMenter import telethn as tbot
import os
import urllib.request
from datetime import datetime
from typing import List
from typing import Optional
import requests
from telethon import *
from telethon import events
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.types import *

from GroupMenter import *
from GroupMenter.events import register


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@register(pattern="^/stt$")
async def _(event):
    if event.fwd_from:
        return
    if event.is_group:
     if not (await is_register_admin(event.input_chat, event.message.sender_id)):
       await event.reply("🚨 Admin @AnossaQWE Gerekiyor.. Bu komutu kullanamazsınız.. Ama benim PM'imde kullanabilirsiniz.")
       return

    start = datetime.now()
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)

    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        required_file_name = await event.client.download_media(
            previous_message, TEMP_DOWNLOAD_DIRECTORY
        )
        if IBM_WATSON_CRED_URL is None or IBM_WATSON_CRED_PASSWORD is None:
            await event.reply(
                "Bu modül için gerekli ENV değişkenlerini ayarlamanız gerekir. \nModül durdurma"
            )
        else:
            # await event.reply("Starting analysis")
            headers = {
                "Content-Type": previous_message.media.document.mime_type,
            }
            data = open(required_file_name, "rb").read()
            response = requests.post(
                IBM_WATSON_CRED_URL + "/v1/recognize",
                headers=headers,
                data=data,
                auth=("apikey", IBM_WATSON_CRED_PASSWORD),
            )
            r = response.json()
            if "results" in r:
                # process the json to appropriate string format
                results = r["results"]
                transcript_response = ""
                transcript_confidence = ""
                for alternative in results:
                    alternatives = alternative["alternatives"][0]
                    transcript_response += " " + str(alternatives["transcript"])
                    transcript_confidence += (
                        " " + str(alternatives["confidence"]) + " + "
                    )
                end = datetime.now()
                ms = (end - start).seconds
                if transcript_response != "":
                    string_to_show = "TRANSKRİPT: `{}`\Alınan Süre: {} S aniye\Güven: `{}`".format(
                        transcript_response, ms, transcript_confidence
                    )
                else:
                    string_to_show = "TRANSKRİPT: `Nil`\nAlınan Süre: {} saniye\n\n**Sonuç Bulunamadı**".format(
                        ms
                    )
                await event.reply(string_to_show)
            else:
                await event.reply(r["error"])
            # now, remove the temporary file
            os.remove(required_file_name)
    else:
        await event.reply("Metni çıkarmak için sesli mesajı yanıtlayın.")


__help__ = """
Metni sese ve sesi metne çevirebilirim..

  ❍ /tts <lang kodu>*:* Metinden konuşmaya çıktı almak için herhangi bir mesajı yanıtlayın
  ❍ /stt*:* Metin almak için sesli mesaja yanıt yazın (yalnızca İngilizce desteği).

*Dil Kodları*
af,am,ar,az,olmak,bn,bs,ca,ceb,co,cs,cy,da,el,tr,eo,es,
et,ab,fa,fi,fr,fy,ga,gd,gl,gu,ha,ha,hi,hmn,hr,ht,hu,hy,
id,ig,is,o,iw,ja,jw,ka,kk,km,kn,ko,ku,ky,la,lb,lo,lt,lv,mg,mi,mk,
ml,mn,mr,ms,mt,my,ne,nl,no,ny,pa,pl,ps,pt,ro,ru,sd,si,sk,sl,
sm,sn,so,sq,sr,st,su,sv,sw,ta,te,tg,th,tl,tr,uk,ur,uz,
vi,xh,yi,yo,zh,zh_CN,zh_TW,zu`
"""

__mod_name__ = "TTS/STT"
