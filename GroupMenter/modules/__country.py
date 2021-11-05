from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from telethon.utils import get_input_location
import flag
import html, os
from countryinfo import CountryInfo
from GroupMenter import telethn as borg
from GroupMenter.events import register


@register(pattern="^/country (.*)")
async def msg(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    lol = input_str
    country = CountryInfo(lol)
    try:
	    a = country.info()
    except:
	    await event.reply("Ülke Şu anda Kullanılamıyor")
    name = a.get("name")
    bb= a.get("altSpellings")
    hu = ''
    for p in bb:
    	hu += p+",  "
	
    area = a.get("area")
    borders = ""
    hell = a.get("borders")
    for fk in hell:
	    borders += fk+",  "
	
    call = "" 
    WhAt = a.get("callingCodes")
    for what in WhAt:
	    call+= what+"  "
	
    capital = a.get("capital")
    currencies = ""
    fker = a.get("currencies")
    for FKer in fker:
	    currencies += FKer+",  "

    HmM = a.get("demonym")
    geo = a.get("geoJSON")
    pablo = geo.get("features")
    Pablo = pablo[0]
    PAblo = Pablo.get("geometry")
    EsCoBaR= PAblo.get("type")
    iso = ""
    iSo = a.get("ISO")
    for hitler in iSo:
      po = iSo.get(hitler)
      iso += po+",  "
    fla = iSo.get("alpha2")
    nox = fla.upper()
    okie = flag.flag(nox)

    languages = a.get("languages")
    lMAO=""
    for lmao in languages:
	    lMAO += lmao+",  "

    nonive = a.get("nativeName")
    waste = a.get("population")
    reg = a.get("region")
    sub = a.get("subregion")
    tik = a.get("timezones")
    tom =""
    for jerry in tik:
	    tom+=jerry+",   "

    GOT = a.get("tld")
    lanester = ""
    for targaryen in GOT:
	    lanester+=targaryen+",   "

    wiki = a.get("wiki")

    caption = f"""<b><u>Bilgi Başarıyla Toplandı</b></u>
<b>
Ülke Adı:- {name}
Alternatif Yazımlar:- {hu}
Ülke Alanı:- {area} kilometrekare
Sınırlar:- {borders}
Arama Kodları:- {call}
Ülkenin Başkenti:- {capital}
Ülkenin para birimi:- {currencies}
Ülkenin Bayrağı:- {okie}
Demonym:- {HmM}
Ülke Türü:- {EsCoBaR}
ISO Adları:- {iso}
Diller:- {lMAO}
Yerel Ad:- {nonive}
nüfus:- {waste}
Bölge:- {reg}
Alt Bölge:- {sub}
Saat Dilimleri:- {tom}
Üst Düzey Etki Alanı:- {lanester}
Wikipedia:- {wiki}</b>

Emilia Tarafından Toplandı.</b>
"""
    
    
    await borg.send_message(
        event.chat_id,
        caption,
        parse_mode="HTML",
    )
    

__help__ = """
Bir ülke hakkında bilgi vereceğim

  ❍ `/country <ülke adı>`*:* Verilen ülke hakkında bilgi toplama
"""

__mod_name__ = "COUNTRY"
