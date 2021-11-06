from GroupMenter import pbot as app
from GroupMenter.pyrogramee.errors import capture_err
from GroupMenter.pyrogramee.json_prettify import json_prettify
from GroupMenter.pyrogramee.fetch import fetch
from pyrogram import filters


@app.on_message(filters.command("covid") & ~filters.edited)
@capture_err
async def covid(_, message):
    if len(message.command) == 1:
        data = await fetch("'https://coronavirus-19-api.herokuapp.com/all")
        data = await json_prettify(data)
        await app.send_message(message.chat.id, text=data)
        return
    if len(message.command) != 1:
        country = message.text.split(None, 1)[1].strip()
        country = country.replace(" ", "")
        data = await fetch(f"https://coronavirus-19-api.herokuapp.com/countries/{country}")
        data = await json_prettify(data)
        await app.send_message(message.chat.id, text=data)
        return


__help__ = """
 ❍ /covid - Covid'in Küresel İstatistiklerini Almak İçin.
  ❍ /covid <country> - Tek Bir Ülkenin İstatistiklerini Almak İçin.
  
  __NOT__ 

API hizmeti yabancı dil. O Yüzden yapabilceğimiz bir şey yok... :(
"""

__mod_name__ = "COVID"
