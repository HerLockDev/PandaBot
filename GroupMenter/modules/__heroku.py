import asyncio
import math
import os

import heroku3
import requests

from GroupMenter import telethn as borg, HEROKU_APP_NAME, HEROKU_API_KEY, OWNER_ID
from GroupMenter.events import register

heroku_api = "https://api.heroku.com"
Heroku = heroku3.from_key(HEROKU_API_KEY)


@register(pattern="^/(set|see|del) var(?: |$)(.*)(?: |$)([\s\S]*)")
async def variable(var):
    if var.fwd_from:
        return
    if var.sender_id == OWNER_ID:
        pass
    else:
        return
    """
    ConfigVars ayarının çoğunu yönetin, yeni değişken ayarlayın, mevcut değişkeni alın, veya değişkeni silin...
    """
    if HEROKU_APP_NAME is not None:
        app = Heroku.app(HEROKU_APP_NAME)
    else:
        return await var.reply("`[HEROKU]:" "\nLütfen **HEROKU_APP_NAME** cihazınızı kurun")
    exe = var.pattern_match.group(1)
    heroku_var = app.config()
    if exe == "see":
        k = await var.reply("`Bilgi almak...`")
        await asyncio.sleep(1.5)
        try:
            variable = var.pattern_match.group(2).split()[0]
            if variable in heroku_var:
                return await k.edit(
                    "**ConfigVars**:" f"\n\n`{variable} = {heroku_var[variable]}`\n"
                )
            else:
                return await k.edit(
                    "**ConfigVars**:" f"\n\n`Hata:\n-> {variable} mevcut değil`"
                )
        except IndexError:
            configs = prettyjson(heroku_var.to_dict(), indent=2)
            with open("configs.json", "w") as fp:
                fp.write(configs)
            with open("configs.json", "r") as fp:
                result = fp.read()
                if len(result) >= 4096:
                    await var.client.send_file(
                        var.chat_id,
                        "configs.json",
                        reply_to=var.id,
                        caption="`Çıktı çok büyük, dosya olarak gönderiliyor`",
                    )
                else:
                    await k.edit(
                        "`[HEROKU]` ConfigVars:\n\n"
                        "================================"
                        f"\n```{result}```\n"
                        "================================"
                    )
            os.remove("configs.json")
            return
    elif exe == "set":
        s = await var.reply("`Bilgi ayarlanıyor... Bekle`")
        variable = var.pattern_match.group(2)
        if not variable:
            return await s.edit(">`.set var <ConfigVars-name> <value>`")
        value = var.pattern_match.group(3)
        if not value:
            variable = variable.split()[0]
            try:
                value = var.pattern_match.group(2).split()[1]
            except IndexError:
                return await s.edit(">`/set var <ConfigVars-name> <value>`")
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await s.edit(
                f"**{variable}**  `Başarıyla değişti`  ->  **{value}**"
            )
        else:
            await s.edit(
                f"**{variable}**  `Değere başarıyla eklendi`  ->  **{value}**"
            )
        heroku_var[variable] = value
    elif exe == "del":
        m = await var.edit("`Değişken silmek için bilgi alınıyor...`")
        try:
            variable = var.pattern_match.group(2).split()[0]
        except IndexError:
            return await m.edit("`Lütfen silmek istediğiniz ConfigVar'ları belirtin`")
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await m.edit(f"**{variable}**  `başarıyla silindi`")
            del heroku_var[variable]
        else:
            return await m.edit(f"**{variable}**  `mevcut değil`")


@register(pattern="^/usage(?: |$)")
async def dyno_usage(dyno):
    if dyno.fwd_from:
        return
    if dyno.sender_id == OWNER_ID:
        pass
    else:
        return
    """
    Hesabınızın Dyno Kullanımı'nı alın
    """
    die = await dyno.reply("**İşleme...**")
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    r = requests.get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await die.edit(
            "`Hata: kötü bir şey oldu`\n\n" f">.`{r.reason}`\n"
        )
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]

    """ - Used - """
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)

    """ - Current - """
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)

    await asyncio.sleep(1.5)

    return await die.edit(
        "**DYNO KULLANIMI**:\n\n"
        f"-> **{HEROKU_APP_NAME}** için `Dyno kullanımı`:\n"
        f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
        f"**|**  [`{AppPercentage}`**%**]"
        "\n\n"
        " -> `Dyno saat kotası bu ay kaldı`:\n"
        f"     •  `{hours}`**h**  `{minutes}`**m**  "
        f"**|**  [`{percentage}`**%**]"
    )


@register(pattern="^/logs$")
async def _(dyno):
    if dyno.fwd_from:
        return
    if dyno.sender_id == OWNER_ID:
        pass
    else:
        return
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        app = Heroku.app(HEROKU_APP_NAME)
    except:
        return await dyno.reply(
            " Lütfen Heroku API Anahtarınızın, Uygulama adınızın heroku'da doğru şekilde yapılandırıldığından emin olun."
        )
    v = await dyno.reply("Günlük Alma....")
    with open("logs.txt", "w") as log:
        log.write(app.get_log())
    await v.edit("Günlükleri aldım bir saniye bekleyin")
    await dyno.client.send_file(
        dyno.chat_id,
        "logs.txt",
        reply_to=dyno.id,
        caption="Emilia Bot Logz.",
    )

    await asyncio.sleep(5)
    await v.delete()
    return os.remove("logs.txt")


def prettyjson(obj, indent=2, maxlinelength=80):
    """JSON içeriğini, maksimum satır uzunluğuna uyacak şekilde girinti ve satır bölmeleri/birleştirmeleri ile işler.
     Yalnızca dikteler, listeler ve temel türler desteklenir"""

    items, _ = getsubitems(
        obj,
        itemkey="",
        islast=True,
        maxlinelength=maxlinelength - indent,
        indent=indent,
    )
    return indentitems(items, indent, level=0)
